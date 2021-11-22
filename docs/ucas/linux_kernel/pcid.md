# PCID in Linux Kernel

[PCID & 与PTI的结合 (happyseeker.github.io)](http://happyseeker.github.io/kernel/2018/05/04/pti-and-pcid.html)

[17. Page Table Isolation (PTI) — The Linux Kernel documentation](https://www.kernel.org/doc/html/latest/x86/pti.html)

[Intel SDM Volume3 4.10.1 PCID]()

### PCID

Process-Context IDentifiers, PCID 进程上下文标识符，12 位标识符，位于 CR3 寄存器的第 12 位。

> AMD 称为 ASID，手册里并没有说 ASID 大小。而且在虚拟化方案中，AMD 仍使用 ASID 标记 VCPU，而 Intel 使用 VPID。

没有 PCID 的环境中，进程切换后要刷新所有的 TLB；引入 PCID 后，使用它作为 TLB 条目标签，进程间互不干扰。进程切换后就可以不刷新 TLB 或之刷新自身 PCID 对应的条目，提升性能。

全局页，在 PTE 的 bit-8 全局标志位置位后，相应的 TLB 条目视为全局，进程切换时不会被刷新，不关联 PCID。

### why KPTI

CPU 在很久之前就支持 PCID，而 Linux 只是在 4.15 之后才使用。主要是因为 Meltdown 的软件缓解措施 KPTI 内核页表隔离启用后，进程从用户态切换到内核态也需要切换页表，刷新 TLB，带来较大的性能开销。所以利用 PCID 减少 TLB 刷新，降低开销。

使用 PCID 存在一些问题：

- PCID 是 12 位，最多 4096 个，而如果要给每个进程分配一个 PCID，进程数超过 4096 之后就只能重新分配。
- 将 TLB 条目按 PCID 划分，而 TLB 大小有限，PCID 数越多，每个 PCID 分到的条目越少，也会增加 TLB miss 的概率。
- 引入 PCID 后，并不意味着进程切换不需要刷新，一般是刷新当前 PCID 对应的条目。

当前内核中只使用 6 个 PCID，内核记录最近使用的 PCID，控制进程切换时是否要刷新，如果是最近使用过的 PCID（说明进程刚切走不久又切换回来），就可以直接使用 TLB 条目。

### Code

初始化

```c
start_kernel
  setup_arch
    init_mem_mapping
      setup_pcid
```

分配新 PCID

```c
switch_mm
  switch_mm_irqs_off
    choose_new_asid
```

PCID 的分配和使用策略完全由软件控制，硬件只提供框架和机制，机制与策略分离。

