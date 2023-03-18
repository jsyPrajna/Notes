[toc]

# AMD SVM Instruction Reference

## 15.5 VMRUN instruction

VMRUN 指令是 SVM 的基石，以保存在 RAX 中的 4K 对齐 VMCB 地址为操作数。

VMRUN 会保存一些 host 状态信息到 VM_HSAVE_PA MSR 指定的物理地址，并从 VMCB 状态保存域加载相关的 guest 状态，并根据 VMCB 中的控制位进行刷新 TLB、中断注入等操作。

VMRUN 只会保存或恢复允许 VMM 恢复 guest 执行的最少 guest 状态信息，这可以让 VMM 很快地处理简单的陷入。而如果需要额外的 guest 状态信息，VMM 需要使用 VMLOAD 和 VMSAVE 指令。

VMRUN 保存的 host 状态包括：

- CS.SEL、NEXT_RIP：VM Exit 之后 host 恢复执行的地址；
- RFLAGS、RAX：host 处理器模式以及用于寻址 VMCB 的 RAX；
- SS.SEL、RSP：host 栈指针；
- CR0、CR3、CR4、EFER：host 的分页和操作模式；
- IDTR、GDTR：描述符，不保存 host LDTR；
- ES.SEL、DS.SEL。

处理器可能只将一部分 host 状态保存到 VM_HSAVE_PA MSR 指定的内存，而是保存到不可见的片上存储。因此，软件不能依赖与 host 保存域的格式或内容，或者尝试通过修改保存域内容来改变 host 状态。

VMRUN 加载的 guest 状态包括：

- CS、RIP：guest 开始执行的地址，隐藏的 CS 值也要从 VMCB 加载；
- RFLAGS、RAX;
- SS、RSP、ES、DS：包括隐藏的 SS、ES、DS 值；
- CR0、CR2、CR3、CR4、EFER：guest 分页模式，VMRUN 写分页相关的控制寄存器不会因切换地址空间而刷新 TLB；
- INTERRUPT_SHADOW：指定 guest 当前的中断影子（是指一个无法识别中断的指令窗口，比如使用 STI 开启中断后的第一条指令就无法识别中断或特定的调试陷入）；
- IDTR、GDTR；
- DR6、DR7：guest 断点状态；
- V_TPR：guest 虚拟 TPR；
- V_IRQ：指定 guest 中那个虚拟中断正等待处理；
- CPL：实模式 guest 的 CPL 强制为 0，v86 模式 guest 强制为 3，其他模式则使用 VMCB 中保存的值。

### VMSAVE 和 VMLOAD

这两条指令在处理器和 guest VMCB 之间转移包括不可访问的隐藏部分的 guest 寄存器上下文，以实现比 VMRUN 或 VM Exit 更完整的上下文切换。需要时，VMLOAD 在 VMRUN 之前执行，而 VMSAVE 在 VM Exit 后执行。

VMCB 的物理地址保存在 RAX 中。这两条指令补充了 VMRUN 和 VM Exit 时的状态保存和恢复能力。使软件能够访问隐藏的处理器状态，以及额外的特权状态。

包括以下的寄存器状态：

- FS、GS、TR、LDTR：包括所有隐藏状态；
- KernelGSBase MSR;
- STAR、LSTAR、CSTAR、SFMASK；
- SYSENTER_CS、SYSENTER_ESP、SYSENTER_EIP。
