# APICv Summary

[Intel SDM Chapter 29: APIC Virtualizaton & Virtual Interrupts | tcbbd的博客](https://tcbbd.moe/ref-and-spec/intel-sdm/sdm-vmx-ch29/)

## Virtual APIC Accesses Conclusion

下面是对 APIC 访问虚拟化的总结。

![APICv Overview](./images/apicv.assets/intel-sdm-vmx-apicv.png)

首先，对于MMIO方式的访问，可以通过 *virtualize APIC access* 令对 APIC-access page 的访问，产生 APIC-access VM Exit，该功能是对 MMIO 访问进行进一步虚拟化的前提，它可以独立于 *use TPR shadow* 开启。

其次，*use TPR shadow* 是 CR8、MMIO、MSR 三种访问方式的虚拟化的总开关，必须开启才能将 guest 的 APIC 访问重定向到 virtual-APIC page：

- 对 CR8 访问方式，*use TPR shadow* 直接控制其虚拟化
- 对 xAPIC 模式的 MMIO 访问，开启 *use TPR shadow* 才能令对部分或全部寄存器的访问重定向到 virtual-APIC page，否则只会产生 APIC-access VM Exit
- 对 x2APIC 模式的 MSR 访问，*virtualize x2APIC mode* 控制其虚拟化，而启用该功能的前提是 *use TPR shadow* 已经启用
- 另外需要注意 *virtualize APIC access* 和 *virtualize x2APIC mode* 不能同时启用

开启 *use TPR shadow* 后仅仅是启用了对 TPR 寄存器的虚拟化，*APIC-register virtualization* 和 *virtual-interrupt delivery* 提供了进一步的控制，这两个功能都必须在 *use TPR shadow* 启用后才能使用：

- 开启 *APIC-register virtualization* 就会虚拟化对所有 APIC 寄存器的读取
- 开启 *virtual-interrupt delivery* 就会虚拟化对 TPR、EOI Register、Self IPI (ICR_Low/Self-IPI Register) 的写入
- 另外开启 *virtual-interrupt delivery* 还要求 *Pin-Based VM-Execution Controls.external-interrupt exiting*[0] = 1

对 xAPIC 模式的虚拟化，可以认为相比 x2APIC 模式增加了以下规则：

- 开启 *APIC-register virtualization* 就会虚拟化对所有 APIC 寄存器的写入
- 开启 *virtual-interrupt delivery* 就会虚拟化对 TPR、EOI Register、ICR_Low 的读取

## Autotriggered Behaviors Conclusion

### FlexPriority

在 APICv 推出之前，还有一个过渡性的技术，称为 VT-x FlexPriority，它引入了 shadow TPR，即 VTPR 寄存器（virtual-APIC page 也是此时引入的）。此时，virtual-APIC page 中仅实现了 VTPR 一个寄存器，并且尚未发明 APIC-write VM Exit，因此对 VTPR 寄存器的写入会起到类似 APIC-write emulation 的效果，不会引起 APIC-write VM Exit。


### Virtual Interrupt Delivery

当 *virtual-interrupt delivery* 为 1 时，才会开启虚拟中断投递，此时会引入一个 *guest interrupt status*，它由两个 8-bit 字段构成：

- 低 8 位为 Requesting Virtual Interrupt (RVI)，表示正在等待处理的中断中最大的向量，相当于 IRRV
- 高 8 位为 Servicing Virtual Interrupt (SVI)，表示正在处理的中断中最大的向量，相当于 ISRV

#### PPR virtualization

从前文可知，VPPR 寄存器不允许 guest 读取，未启用 *virtual-interrupt delivery* 时，它等同于不存在。由于虚拟中断投递功能需要判断 guest 的虚拟 PPR，因此在 VM Entry、TPR virtualization 和 EOI virtualization 时会自动更新 VPPR 寄存器的值：

- 若 `VTPR[7:4] >= SVI[7:4]`，则 `VPPR = VTPR & 0xFF`
- 否则，`VPPR = SVI & 0xF0`

这基本上和 APIC 中 PPR 根据 TPR 和 ISRV 更新的规则相同，即取两者中大者（优先级更高者），从而屏蔽优先级低于两者中任意一个的中断。

VPPR 更新的三个时机，选择的依据如下：

- VM Entry 时，VTPR 和 SVI 的值都可能已被 VMM 修改过
- TPR virtualization 发生时，VTPR 的值被 guest 改变
- EOI virtualization 发生时，guest 完成了其当前正在处理的中断，VISR 发生变化，从而 SVI 发生变化（详下）

#### Interrupt Delivery

为了解释虚拟中断投递机制，本节需要介绍一些手册中不涉及的背景知识，以及手册前几章节的内容

顾名思义，虚拟中断投递引入了对中断投递功能的（硬件辅助）虚拟化支持。首先回顾通常情况（无虚拟化）下的中断处理：

- IPI 以及外部中断首先是由系统总线上的中断消息到达 CPU 的 APIC 而触发，若 CPU 发现自己是该中断消息的目标，则会根据中断消息的向量设置 IRR 中的相应位（不考虑 NMI、SMI、INIT、ExtINT 和 Start-IPI）。
- 对于来自本地中断源的中断，省略判断是否接收中断的步骤（因为必定接收），根据 LVT 表中配置的向量设置 IRR 中的相应位。
- 对于 IRR 中 Pending 的最高优先级中断，若其优先级高于 PPR 的优先级，则清空 IRR 中的对应位，设置 ISR 中的对应位，并将中断分发给 CPU。
- 对于 NMI、SMI、INIT、ExtINT 以及 Start-IPI，直接分发给 CPU。

为了厘清它们在虚拟化中的实现，将它们分解成几个步骤：

- 对于 IPI 和外部中断，第一步是中断路由（Interrupt Routing），这一步可以在软件中模拟（非 Passthrough 情形），例如 QEMU 会模拟一个设备产生虚拟中断，然后经过 INTx 来到 IOAPIC 最后发送到 LAPIC 的过程。
- 随后的步骤是设置 IRR，将中断加入等待队列（不考虑 NMI、SMI、INIT、ExtINT 和 Start-IPI），我们将这一步称为 Interrupt Acceptance（中断接受）。
- 对于将中断分发给 CPU 执行 IDT 中注册的中断处理例程这一行为，我们称之为 Interrupt Delivery（中断交付）。
- 对于 NMI、SMI、INIT、ExtINT 以及 Start-IPI，可以直接进行中断投递。
- 否则要先从 IRR 中取出最高优先级的中断，设置 ISR 中对应位，这个过程不妨称之为 Interrupt Acknowledgement（中断确认），然后才能进行中断交付。

通常来说，外部中断（此处的外部中断指的是除 NMI、SMI、INIT 和 Start-IPI 外的所有中断，与 CPU 内部异常相对）和发送给 guest 的虚拟中断之间没有必然联系，除了它们可能可以通过上述中断路由的过程间接地联系起来。一个外部中断首先由 host 处理，然后可能导致 VMM 生成一个或多个虚拟中断，并经软件模拟的中断路由，最终注入到 vCPU 中，当然，也可能不产生任何虚拟中断。对于直通给 guest 的设备产生的中断，情况略有不同，其物理中断和虚拟中断基本上是一一对应的关系，并且对中断路由的模拟有所简化甚至完全省略。不论如何，虚拟中断的产生和路由都是系统指定的，对于不同的虚拟化解决方案、不同的虚拟设备都有所不同，这里我们不关心这一步骤是如何完成的。

对于中断接受，一般来说总是需要 VMM 进行模拟，也就是虚拟中断到达 vCPU 的虚拟 APIC 时，要由 VMM 手动设置 VIRR 寄存器，这一步即使使用了 *virtual-interrupt delivery* 也是一样的（除非使用了 posted interrupt）。

真正的区别在于中断确认和中断投递：

首先来看传统的处理方法，VMM 会手动设置 VIRR 和 VISR 的位，然后通过中断注入机制在紧接着的下一次 VM Entry 时注入一个中断向量号，调用 guest 的 IDT 中注册的中断处理例程。如果 guest 正处在屏蔽外部中断的状态，即 guest 的 RFLAGS.IF=0 或 *guest Non-Register State.interruptibility state*（`VMCS[0x4824](32 bit)`）的 Bit 0 (Blocking by STI) 和 Bit 1 (Blocking by MOV-SS) 不全为零，将不允许在 VM Entry 时进行中断注入。为了向 vCPU 注入中断，可以临时设置 *interrupt-window exiting* 为 1，然后主动 VM Entry 进入 non-root 模式。一旦 CPU 进入能够接收中断的状态，即 RFLAGS.IF=1 且 *interruptibility state*[1:0] = 0，便会产生一个 VM Exit（`VM Exit No.7` interrupt-window），此时 VMM 便可注入刚才无法注入的中断，并将 *interrupt-window exiting* 重置为 0。

虚拟中断投递解决了上述做法中的两个问题，第一个是需要 VMM 手动模拟中断确认、中断投递，第二个是有时需要产生 interrupt-window VM Exit 以正确注入中断。

具体来说，在进行 VM Entry、TPR virtualization、EOI vitualization、Self-IPI virtualization 以及 Posted-Interrupt proessing 时，会进行一个称为评估 pending 虚拟中断的行为：

- 若 *interrupt-window exiting* = 0，且`RVI[7:4] > VPPR[7:4]`，则确认一个 pending virtual interrupt
- 一旦确认，硬件会持续检查 vCPU 是否能够接收中断（即 RFLAGS.IF=1 且 *interruptibility state*[1:0] = 0）
  - 若当前已经能接收中断，则立即进行虚拟中断投递
  - 否则令 vCPU 继续执行，直到 vCPU 能够接收中断时，进行虚拟中断投递

而所谓的虚拟中断投递，实际上就是进行如下操作：

1. 根据 RVI，清除 VIRR 中对应位，设置 VISR 中对应位，设置 `SVI = RVI`
2. 设置 `VPPR = RVI & 0xF0`
3. 若 VIRR 中还有非零位，设置 `RVI = VIRRV`，即 VIRR 中优先级最高的向量号，否则设置`RVI = 0`
4. 根据 RVI 提供的向量调用 guest 的 IDT 中注册的中断处理例程

基本上，虚拟中断投递就是用硬件自动执行了我们前文定义的中断确认和中断投递两个步骤，除了它还需要同步 RVI、SVI 与 VIRRV、VISRV。

现在来考察一下虚拟中断投递的用法：

- 我们仍旧需要在 VMM 中模拟中断接受，即设置 VIRR 寄存器
- 但只要设置了 RVI，VM Entry 时就可以自动进行中断确认和中断投递，并且硬件会自动阻塞虚拟中断投递直至 vCPU 允许接收中断，从而避免了此前使用的 interrupt-window VM Exit
- 如果 vCPU 尚未被调度到，则我们可以在其 VIRR 寄存器中设置多个位，从而积累多个 pending 的中断，只要设置 RVI 为其中优先级最高者，VM Entry 后 vCPU 就会自动对所有 pending 的中断进行虚拟中断投递，而无需每发送一个中断就 VM Exit 一次
  - 这里的原理是每当 vCPU 进行 EOI 时，都会触发 EOI virtualization，从而引起下一次虚拟中断投递，整个过程不需要 VM Exit。而原本每次进行 EOI 都要 VM Exit 到 VMM，重新向 guest 注入中断。

#### APIC-write Emulation

为了在 non-root 模式中不退出地处理 VIRR 中累积的中断，虚拟中断投递功能引入了 APIC-write emulation，即 guest 写入 TPR、EOI 寄存器以及进行 Self-IPI 时，除了对 virtual-APIC page 写入，还会进行以下操作：

##### TPR virtualization

1. 首先进行 PPR virtualization，更新 VPPR 寄存器的值
2. 其次根据 RVI 和 VPPR 的值评估 pending 虚拟中断

#### EOI virtulization

1. 根据 SVI，清除 VISR 中对应位
2. 若 VISR 中还有非零位，设置 `SVI = VISRV`，即 VISR 中优先级最高的 Vector 号，否则设置 `SVI = 0`
3. 然后进行 PPR virtualization，更新 VPPR 寄存器的值
4. 检查 *EOI-Exit Bitmap*[Vector]，其中 Vector 为 SVI 的旧值，即被 EOI 的中断
  - 若该位为 1，则引起 VM Exit（`VM Exit No.45` Virtualized EOI），exit qualification 的第 0-7 位会记录引起 VM Exit 的 Vector 值
  - 否则评估 pending 虚拟中断
  - *EOI-Exit Bitmap* 由 4 个 64 位寄存器构成，分别位于`VMCS[0x201C]/VMCS[0x201D](64 bit full/high)`、`VMCS[0x201E]/VMCS[0x201F]`、`VMCS[0x2020]/VMCS[0x2021]`、`VMCS[0x2022]/VMCS[0x2023]`

##### Self-IPI virtualization

1. 根据 Self-IPI 的 Vector，设置 VIRR 中的对应位
2. 设置 `RVI = max(RVI, Vector)`，其中 Vector 为 Self-IPI 的中断向量号
3. 然后评估 pending 虚拟中断

### Posted Interrupt

Posted interrupt 是对虚拟中断投递的进一步发展，让我们可以省略中断接受的过程，直接令正在运行的 vCPU 收到一个虚拟中断，而不产生 VM Exit。它可以向正在运行的 vCPU 注入中断，配合 VT-d 的 posted interrupt 功能，还可以实现直通设备的中断直接发给 vCPU 而不引起 VM Exit。

我们可以通过 *process posted interrupt* 开启 posted interrupt 功能，要启用该功能必须先开启 *virtual-interrupt delivery* 以及 *VM Exit Controls.Acknowledge Interrupt on Exit*。

首先来回顾一下，non-root 模式下对外部中断（指除 NMI、SMI、INIT 和 Start-IPI 外的所有中断）的处理：

当 *external-interrupt exiting* = 1 时，non-root 模式下接收到外部中断后，会产生 VM Exit（`VM Exit No.1` External Interrupt），将中断交给 host 处理。开启 *virtual-interrupt delivery* 的前提就是开启 *external-interrupt exiting*。根据 *Acknowledge Interrupt on Exit* 的取值，Host 对中断有不同的处理：

- 若 *Acknowledge Interrupt on Exit* = 0，则 VM Exit 后该中断还在 IRR 中 pending，host 应该开中断（即取消中断屏蔽）以调用其 IDT 中注册的中断处理例程
- 否则，VM Exit 时会进行中断确认，但不会进行 EOI，中断的向量号会存储在 *VM-Exit Interruption Information*（`VMCS[0x4404](32 bit)`）中，host 应该读取该向量号然后作出相应的处理

回到 posted interrupt，它引入了一个 posted-interrupt notification vector（`VMCS[0x0002](16 bit)`，仅最低 8 位有效）和一个 64 字节（恰好占满一个 Cache Line）的 posted-interrupt descriptor（PID）。后者位于内存中，其地址（HPA）通过 posted-interrupt descriptor address（`VMCS[0x2016]/VMCS[0x2017](64 bit full/high)`）指定，格式如下：

- 第 0-255 位为 posted-interrupt requests (PIR)，是一个位图，每个位对应一个向量
- 第 256 位为 outstanding notification (ON)，取 1 表示有一个 outstanding 的 notificaton event（即中断）尚未处理
- 第 257-511 位为 available，即允许软件使用的 ignored 位

当 non-root 模式下收到一个外部中断时，cpu 首先完成中断接受和中断确认（因为开启 posted interrupt 必先开启 *acknowledge interrupt on exit*），并取得中断的向量号。然后，若向量与 posted-interrupt notification vector 相等，则进入 posted-interrupt processing，否则照常产生 external interrupt VM Exit。posted-interrupt processing 的过程如下：

1. 清除 PID 的 ON 位
2. 向 CPU 的 EOI 寄存器写入 0，执行 EOI，至此在硬件 APIC 上该中断已经处理完毕
3. 令 `VIRR |= PIR`，并清空 PIR
4. 设置 `RVI = max(RVI, PIRV)`，其中 PIRV 为 PIR 的旧值中优先级最高的 Vector
5. 最后评估 pending 虚拟中断

其中步骤 1 和步骤 3 都是针对 PID 所在的 cache line 的原子操作，这就是 PID 正好占满一个 cache line 的原因。

现在来考察一下 posted interrupt 的用法：

假设现在想给一个正在运行的 vCPU 注入中断，除非该 vCPU 正在处理中断，否则仅凭虚拟中断投递，仍需要令其 VM Exit 并设置 RVI，以便在 VM Entry 时触发虚拟中断投递。若使用 posted interrupt，则可以设置 PID.PIR 中对应位，然后给 vCPU 所在的 CPU 发送一个 notification event，即中断向量号为 posted-interrupt notification vector 的中断，这样 vCPU 无需 VM Exit 就可以被注入一个甚至多个中断。