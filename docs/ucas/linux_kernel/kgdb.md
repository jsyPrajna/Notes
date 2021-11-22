# KGDB

[Using kgdb, kdb and the kernel debugger internals — The Linux Kernel documentation](https://www.kernel.org/doc/html/v5.0/dev-tools/kgdb.html)

[Linux Magic System Request Key Hacks — The Linux Kernel documentation](https://www.kernel.org/doc/html/v5.0/admin-guide/sysrq.html)

KGDB 是集成在 Linux 内核中的源码级调试器，可以与 gdb 配合调试 Linux 内核。使用 KGDB 需要搭建双机调试环境，目标机器上允许要调试的内核，调试机器上有包含符号表的 vmlinux 文件，使用 gdb 连接到目标机器进行调试。

### 内核编译配置

开启 KGDB、支持 gdb 调试，需要设置以下几项：

```
# CONFIG_STRICT_KERNEL_RWX is not set
CONFIG_FRAME_POINTER=y
CONFIG_KGDB=y
CONFIG_DEBUG_INFO=y
CONFIG_KGDB_SERIAL_CONSOLE=y
CONFIG_MAGIC_SYSRQ=y
CONFIG_MAGIC_SYSRQ_DEFAULT_ENABLE=1
CONFIG_GDB_SCRIPTS=y
# CONFIG_DEBUG_INFO_REDUCE is not set
```

### 内核启动参数

编译安装内核后，需要在 */etc/default/grub* 的 `GRUB_CMDLINE_LINUX` 中添加内核启动参数 `kgdboc=ttyS0,115200 nokaslr`。

或在内核启动后执行：

```shell
$ echo ttyS0 > /sys/module/kgdboc/parameters/kgdboc
```

### 连接 GDB

启动目标机器，允许内核，接下来就需要停止内核执行，这里使用 sysrq 快捷键，前面的内核编译选项 `CONFIG_MAGIC_SYSRQ=y` 就是启用 sysrq 支持。

首先要确认 */proc/sys/kernel/sysrq* 的值：

> - 0 - disable sysrq completely
>
> - 1 - enable all functions of sysrq
>
> - \>1 - bitmask of allowed sysrq functions (see below for detailed function description):
>
>   ```
>     2 =   0x2 - enable control of console logging level
>     4 =   0x4 - enable control of keyboard (SAK, unraw)
>     8 =   0x8 - enable debugging dumps of processes etc.
>    16 =  0x10 - enable sync command
>    32 =  0x20 - enable remount read-only
>    64 =  0x40 - enable signalling of processes (term, kill, oom-kill)
>   128 =  0x80 - allow reboot/poweroff
>   256 = 0x100 - allow nicing of all RT tasks
>   ```

然后使用 `ALT-SysRq-<commandkey>` 的组合键实现功能，这里要用到的就是 `SysRq-G`，按下后内核会暂停等待 gdb 接入。

下面就可以将调试机器用串口线连接到目标机器，启动 gdb：

```shell
$ gdb ./vmlinux
(gdb) set serial baud 115200
(gdb) target remote /dev/ttyUSB0 (这里选择与目标机器连接的串口，此处使用 USB0)
```

连接后就可以使用 gdb 调试，用 `c` 命令可以让目标机器继续运行，可以通过打断点中断或使用 `SysRq-G`。

这里要调试 kvm 模块，所以需要继续加载 kvm 的符号表，在目标机器中查看模块的段地址：

```shell
$ cat /sys/module/kvm/sections/{.text,.data,.bss}
0xffffffffc05cb000
0xffffffffc0637000
0xffffffffc064bac0
```

然后在  gdb 中添加符号表：

```shell
(gdb) add-symbol-file /path/to/module -s <section_name> <section_address>
```

加载符号表之后就可以设置源码断点进一步调试。
