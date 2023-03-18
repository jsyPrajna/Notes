# Nested Kernel Implementation on Linux Kernel

!!! tldr

    记录在 Linux 内核上实现嵌套内核架构的过程。

嵌套内核架构的实现包括以下几个方面：

- 控制页表相关操作，所有页表页只读，仅支持使用接口修改页表；
- 控制敏感指令，相关寄存器，CR0、CR3、CR4、MSR 等，要替换为对应的嵌套内核接口；
- 控制流保护，控制中断和异常处理，进入和离开嵌套内核需要经过调用门；
- 嵌套内核数据段保护，包括栈，通过预留内存方式。

与 KVM（AMD SVM）结合的嵌套内核架构还包括以下几方面：

- 控制嵌套页表相关操作，类似对内核页表页，将嵌套页表页设为只读，KVM 只能使用接口修改；
- 控制虚拟化相关指令，VMRUN、VMLOAD、VMSAVE 等；
- 控制流保护，将 VM Entry 和 VM Exit 相关代码放在嵌套内核中。

> 下面所说的内核指的是应用了嵌套内核之后的 outer kernel。

## 嵌套内核接口

相关函数定义位置如下，新增 *nested_kernel.c*，需要在 Makefile 中添加 *nested_kernel.o*：

- *arch/x86/mm/nested_kernel.c*
- *arch/x86/include/asm/pgtable_64.h*
- *arch/x86/include/asm/pgtable.h*
- *arch/x86/include/asm/pgalloc.h*
- *arch/x86/kernel/setup.c*
- *arch/x86/mm/pgtable.c*
- *arch/x86/mm/init.c*
- *arch/x86/mm/fault.c*
- *init/main.c*
- *mm/memory.c*

> *arch/x86/mm/init.c* 中的 `probe_page_size_mask` 负责探测能否使用大页（2M，1G）进行直接映射，在内核启动参数中添加 `nogbpages` 即可禁用 1G 大页，让内核在直接映射时最多只映射到 2M 大页，方便设置页表页。

相关数据结构和变量：

- `ptp_t`：页表页信息结构体，包含页表页地址和页表页对应的页表项地址；
- `struct ptp_info`：页表页数组结构体，包含数组基地址和数组中页表页数量；
- `pgt_pages[PGD_LEVEL]`：页表页数组，每个等级的页表页填入对应的数组；
- `nk_page_info_t`：嵌套内核维护的页信息结构体，其中的 type 成员标识页的用途；
- `nk_mem_map`：系统页表信息数组，每个物理页都有一个对应的 `nk_page_info_t` 结构体。 

相关辅助函数：

- `rebuild_page_table_for_ptp`：为页表页重构页表；
- `get_pte_for_ptp`：获取页表页对应的页表项；
- `save_ptp_info`：保存页表页信息；
- `remove_ptp_info`：移除页表页信息；
- `walk_through_ptp`：递归遍历制定等级的页表页；
- `walk_pgtable`：根据地址遍历页表，获取页表项地址、等级和内容；
- `set_ptp_read_only`：设置页表页只读；
- `int3_in_target_rip`：处理页表页 PF 导致的 INT3 中断；
- `save_rip_info`：保存触发页表页 PF 的 RIP 信息；
- `fault_in_ptp`：判断 PF 是否由写页表页触发；
- `do_ptp_page_fault`：处理页表页 PF。

嵌套内核接口：

- `NESTED_KERNEL_ENTRY`：嵌套内核入口门，关中断、关 WP、切换到独立的嵌套内核栈；
- `NESTED_KERNEL_EXIT`：嵌套内核退出门，切栈、开 WP、使用循环检查确保启用 WP、开中断；
- `NESTED_KERNEL_WRAPPER`：嵌套内核接口定义宏，使用入口和出口门包装接口操作；
- `nested_kernel_write_pte`: 写页表项，判断页表项地址和内容；
- `nested_kernel_get_and_clear_pte`：使用 XCHG 指令修改页表项并获取旧值；
- `nested_kernel_declare_ptp`：声明页表页，将页表页设置为只读；
- `nested_kernel_undeclare_ptp`：取消声明页表页，将页表页恢复为可写；
- `nested_kernel_load_cr3`：加载顶级页目录表物理地址到 CR3，判断是否为声明过的顶级页目录表；
- `nested_kernel_load_cr0/cr4/msr`：加载控制寄存器，判断关键标志位是否置位；
- `nested_kernel_idtentry`：统一的中断处理入口，先关闭 WP 后在跳转到内核的中断处理执行。

虚拟化安全模块接口：

- `vsm_vm_entry`：VSM VM Entry ，KVM 调用此接口运行虚拟机；
- `vsm_nptp_alloc`：VSM 分配 NPT 页表页；
- `vsm_nptp_free`：VSM 释放 NPT 页表页；
- `vsm_set_npte`：VSM 写 NPT 表项，判断映射和标志位。

## 页表相关

控制内核空间的页表，包括直接映射（基址 `0xffff888000000000`）、内核代码段数据段（基址 `0xffffffff80000000`）以及后续按需设置的内核空间页表。

> 对于用户页表，虽然存在内核将用户页表设置为特权模式（页表项 U/S 位清零）绕过 SMAP、SMEP 的可能，但是正常的内核里并没有这样的代码。因此只要保证内核代码完整性，就可以确保避免此类攻击。因此嵌套内核不会去检查顶级页表页前半部分（用户地址空间）设置。对于其他的类似问题（指存在攻击可能但是正常的内核中没有这样的逻辑），嵌套内核也不会做特殊检查。

> 通过 per-page 结构体中的 page type 成员在 set pte 时判断目标物理地址是否是嵌套内核内存/页表页，可实施安全策略。

内核初始化后使用的顶级页表为 `swapper_pg_dir`，即 `init_top_pgt`，详情可见 [内核页表演进过程](./kernel_page_table.md)。

控制页表相关操作，主要包括以下几个方面：

- 收集所有的页表页（Page Table Pages, PTPs）：
  - 在页表初始化 `init_mem_mapping` 中，设置内核直接映射之后，遍历以 `init_top_pgt` 为顶级页目录表的页表，记录所有的页表页和对应的页表等级；
  - 对于此后新加入的页表页，通过在页表页分配操作 `pgd/pud/pmd/pte_alloc` 中调用嵌套内核接口 `nested_kernel_declare_ptp`，向嵌套内核声明页表页；
  - 同时在页表页释放操作 `pgd/pud/pmd/pte_free` 中调用嵌套内核接口 `nested_kernel_undeclare_ptp`，向嵌套内核声明删除页表页。
- 找到页表页对应的页表项，并设为只读（清除 R/W 标志位）：
  - 根据页表页的虚拟地址（除了在内核数据段的顶级页表页，内核访问所有页表页都是通过直接映射的虚拟地址），调用 `walk_pgtable` 遍历整个页表，即可找到对应的页表项；
  - 存在问题：内核代码数据和直接映射大多使用 2M 或 1G 大页映射，遍历页表找到的页表项其实是管理 2M/1G 的空间，如果直接设置为只读，则会使对这部分区域其他地址的写访问触发 page fault, PF，特别是对内核数据段的设置，容易导致内核崩溃；
  - 解决方案：根据页表页地址遍历页表找到的页表项及其页表等级，如果是大页（页表等级为 2 或 3，对应 2M 和 1G 大页），则调用 `rebuild_page_table_for_ptp` 为当前页表页重构页表，将大页拆分为 4K 页，并返回新的 4K 页表项地址。对于 2M 大页，需要新增一个页表页，将原来的 2M 页表项指向新的页表页，并填充新页表页内容，覆盖原来的 2M 内存区域。对于 1G 大页，需要新增两个页表页，过程类似。对于重构页表过程中新增的页表页，也要调用嵌套内核接口声明。
- 页表页 PF 处理：
  - 在 PF 处理程序 `do_page_fault` 中添加对因设置页表页只读触发的 PF 处理，通过 `fault_in_ptp` 判断当前 PF 是否为内核写页表页触发，是则由 `do_ptp_page_fault` 处理；
  - 为快速收集所有设计页表页修改的内核代码，需要在触发 PF 时记录 RIP 和符号信息，并放行本次操作（为了让系统能继续运行）。放行的操作主要分两种：设置页表项为可写、关闭 CR0.WP，前者将导致对本页表页的后续写操作不会触发 PF 而无法捕获，后者则会放行让系统中所有的页表页写操作。理想的情况是在 PF 处理返回后重新执行当前指令，在其执行后关闭 WP，因此将下一条指令的第一个字节改为 INT3，当前指令执行后继续执行会触发 INT3 中断，进入对应的处理程序 `do_int3`，而在其中通过判断本次 INT3 是否为页表页 PF 导致，是则恢复指令，开启 WP，继续执行。
- 将页表页修改操作修改为对嵌套内核接口的调用：
  - 修改内核原有的页表页修改操作 `set_pte/pmd/pud/p4d/pgd`，调用嵌套内核接口 `nested_kernel_write_pte`，其中会对要设置的页表项地址和内容进行判断，包括地址是否属于嵌套内核中记录的页表页、页表项覆盖地址范围是否包含敏感数据以及页表项标志位等；
  - 对于极少部分不使用 `set_xxx` 接口修改页表页的内核代码，如 `vunmap_page_range` 中使用 XCHG 指令修改页表项，也要将其替换为嵌套内核接口。

控制 KVM 嵌套页表相关操作，与嵌套内核类似：

- 在嵌套页表页分配和释放操作 `kvm_mmu_alloc/free_page` 中调用嵌套内核接口 `nested_kernel_declare/undeclare_ptp`；
- 将嵌套页表项修改操作 `__set_spte` 等改为调用嵌套内核接口 `nested_kernel_set_pte`。

## 敏感指令

| 敏感指令   | 描述/影响                                                 | 策略（处理方式）                            |
| ---------- | --------------------------------------------------------- | ------------------------------------------- |
| MOV-to-CR0 | WP 控制写保护，PG 控制分页，PE 控制保护模式               | 禁止置零相关标志位（指令执行后检查）        |
| MOV-to-CR4 | SMAP 和 SMEP 控制特权模式对用户页的访问权限               | 禁止置零相关标志位（指令执行后检查）        |
| WRMSR EFER | LME 控制长模式，NXE 控制不可执行权限，SVME 控制虚拟化扩展 | 禁止置零相关标志位（指令执行后检查）        |
| MOV-to-CR3 | 切换内存地址空间                                          | 仅允许设置为已声明的顶级页表页 （按需映射） |
| LIDT       | 设置 IDT 基址                                             | 禁止修改 IDT                                |

与 KVM 结合，还需要将虚拟化指令加入到敏感指令序列，AMD 平台上的指令包括 VMRUN、VMLOAD、VMSAVE、VMMCALL、STGI/CLGI 等。

控制敏感指令的方法：

- 内核本身封装了对特殊寄存器的修改和访问操作 `native_write_cr0/cr3/cr4/msr`，将这些接口改为调用嵌套内核的接口即可；
- 对于汇编源代码文件中的相关指令，也需要替换为嵌套内核接口，防止内核跳转到此处执行；
- 对于 MOV-to-CR0/CR4, WRMSR 这种敏感指令，可以在执行后通过循环检查相关标志位是否合法；
- 对于 MOV-to-CR3, LIDT 这种执行后可能会改变控制流的指令（执行后直接切换地址空间），需要取消其内存映射，按需映射，并在映射前检查指令参数；
- 扫描编译生成的内核二进制文件，确保内核中没有敏感指令实例，包括未对齐边界的指令。

## 控制流保护

- 一部分控制流的保护要依赖敏感指令的保护，如 `MOV-to-CR3` 以及虚拟化指令；
- 控制 IDT，中断和异常处理要先通过嵌套内核，确保开启 WP；
- 嵌套内核操作要由入口门和出口门包装。

## 嵌套内核数据保护

- 嵌套内核的数据结构需要与内核隔离，可以通过预留内存的方式实现；
- 执行嵌套内核操作需要切换到独立的栈。

相关相关操作如下：

使用内核参数 `memmap=4M\$0x140000000` 保留内存，直接影响 e820 表，保留的内存不会出现在 memblock 中，也不会映射在直接映射页表中。

`e820_table` 内容如下，可以看到 5G 开始的 4M 空间被标记为保留。

```c
 [qhx]: print e820 table
 [qhx]: [mem 0x0000000000000000-0x0000000000000fff] reserved
 [qhx]: [mem 0x0000000000001000-0x000000000009fbff] usable
 [qhx]: [mem 0x000000000009fc00-0x000000000009ffff] reserved
 [qhx]: [mem 0x00000000000f0000-0x00000000000fffff] reserved
 [qhx]: [mem 0x0000000000100000-0x000000007ffdefff] usable
 [qhx]: [mem 0x000000007ffdf000-0x000000007fffffff] reserved
 [qhx]: [mem 0x00000000b0000000-0x00000000bfffffff] reserved
 [qhx]: [mem 0x00000000fed1c000-0x00000000fed1ffff] reserved
 [qhx]: [mem 0x00000000feffc000-0x00000000feffffff] reserved
 [qhx]: [mem 0x00000000fffc0000-0x00000000ffffffff] reserved
 [qhx]: [mem 0x0000000100000000-0x000000013fffffff] usable  
 [qhx]: [mem 0x0000000140000000-0x00000001403fffff] reserved  // 保留的内存，5G 开始 4M  
 [qhx]: [mem 0x0000000140400000-0x000000027fffffff] usable
```

memblock 信息如下，`[0x0000000140000000-0x00000001403fffff]` 保留的内存区域不在 memblock 中。

```c
MEMBLOCK configuration:
 memory size = 0x00000001ffb7dc00 reserved size = 0x0000000002759000
 memory.cnt  = 0x4
 memory[0x0]	[0x0000000000001000-0x000000000009efff], 0x000000000009e000 bytes on node 0 flags: 0x0
 memory[0x1]	[0x0000000000100000-0x000000007ffdefff], 0x000000007fedf000 bytes on node 0 flags: 0x0
 memory[0x2]	[0x0000000100000000-0x000000013fffffff], 0x0000000040000000 bytes on node 0 flags: 0x0
//            [0x0000000140000000-0x00000001403fffff] 保留的内存区域不再 memblock 中
 memory[0x3]	[0x0000000140400000-0x000000027fffffff], 0x000000013fc00000 bytes on node 0 flags: 0x0
 reserved.cnt  = 0x6
 reserved[0x0]	[0x0000000000000000-0x000000000000ffff], 0x0000000000010000 bytes on node 0 flags: 0x0
 reserved[0x1]	[0x0000000000099000-0x00000000000fffff], 0x0000000000067000 bytes on node 0 flags: 0x0
 reserved[0x2]	[0x0000000001000000-0x000000000340cfff], 0x000000000240d000 bytes on node 0 flags: 0x0
 reserved[0x3]	[0x000000007fd2b000-0x000000007ffcffff], 0x00000000002a5000 bytes on node 0 flags: 0x0
 reserved[0x4]	[0x000000027ffd0000-0x000000027fff9fff], 0x000000000002a000 bytes flags: 0x0
 reserved[0x5]	[0x000000027fffa000-0x000000027fffffff], 0x0000000000006000 bytes on node 0 flags: 0x0
```

内核直接映射页表如下，可以看到指定的保留内存区域未被映射。

```c
 pgd[273] = 3401067 [P R/W U/S A]
 pud-ptp_addr: va = ffff888003401000 pa = 3401000
	 pud[0] = 3402067 [P R/W U/S A]
        ...
	 pud[1] = 27ffff067 [P R/W U/S A]
        ...
	 pud[4] = 80000001000000e3 [1G NX P R/W A D PAT/PSE]
	 pud[5] = 3404067 [P R/W U/S A]
	 pmd-ptp_addr: va = ffff888003404000 pa = 3404000
     // pmd[0] 和 pmd[1] 应该是覆盖 [0x0000000140000000-0x00000001403fffff] 的连个
		 pmd[2] = 80000001404000e3 [2M NX P R/W A D PAT/PSE]
```

