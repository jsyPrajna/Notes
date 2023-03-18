# Linux Kernel Dmesg Output

!!! tldr

    如何设置内核启动参数实现将启动时的 dmesg 输出到各种想要的位置。

##　Multiple ouput targets

基本概念：

- tty：teletypes，终端设备的总称；
- pty：pesudo-tty，虚拟终端；
- pts：pesudo-terminal slave，pty 的实现方法。

Linux 的 /dev 目录下，终端设备有以下几种：

- ttySn：serial port terminal，串行端口终端；
- pty：pesudo-terminal，成对的逻辑终端设备，master 的操作会反映到 slave 上；
- tty：controlling terminal，控制终端；
- ttyn, console：console，控制台终端，tty0 是当前终端的别名；
- pts/n：Xwindows 模式下的伪终端。

## Redirect dmesg to targets

内核命令行参数 `earlyprintk` 和 `console` 可以指定日志输出的设备，下面通过几个测试确定到底应该如何配置。

对于一个 Linux（以 Ubuntu 20.04 server 为例）虚拟机，日志输出的目标有几个：图形控制台（一般为 VNC 或 Spice），文本控制台和串口设备。

其中图形控制台显示的是 tty1，文本控制台要与第一个串口设备绑定，第二个串口设备设置为重定向到文件，相关的 xml 配置如下：

```xml
<devices>
...
  <serial type="pty">
    <target type="isa-serial" port="0">
      <model name="isa-serial"/>
    </target>
  </serial>

  <serial type="file">
    <source path="/home/qhx/Workspace/qhx-linux/debug/vm.log"/>
    <target type="isa-serial" port="1">
      <model name="isa-serial"/>
    </target>
  </serial>

  <console type="pty">
    <target type="serial" port="0"/>
  </console>
...
</devices>
```

预期目标为：图形控制台能够正常使用（登录），在两个串口设备中显示从内核启动开始的所有 dmesg 信息（即包括 earlyprintk）。

相关测试结果如下，Y 表示有相关 dmesg 输出，N 表示没有。

首先是 `earlyprintk`，根据内核文档，只有 `ttyS0` 和 `ttyS1` 能否通过指定名字的方式使用，而其他的串口需要指定具体的端口地址，如 `earlyprintk=serial,0x1008,115200`，这里只测试 `ttyS0` 和 `ttyS1`。

| `earlyprintk` | 文本控制台（ttyS0） | vm.log 文件（ttyS1） |
| ------------- | ------------------- | -------------------- |
| None          | N                   | N                    |
| ttyS0         | Y                   | N                    |
| ttyS1         | N                   | Y                    |
| ttyS0 & ttyS1 | Y                   | N                    |
| ttyS1 & ttyS0 | N                   | Y                    |

要注意的是，如果指定了两个，那么只有第一个生效。另外，在指定的串口后加上 `,keep` 可以保持在后续的 console 启动后不禁用输出。

然后是 `console`，即系统启动后的控制台终端，默认为 tty1，。


| `console`     | 图形控制台（tty1） | 文本控制台（ttyS0） | vm.log 文件（ttyS1） |
| ------------- | ------------------ | ------------------- | -------------------- |
| None          | Y                  | N                   | N                    |
| ttyS0         | N                  | Y                   | N                    |
| ttyS1         | N                  | N                   | Y                    |
| ttyS0 & ttyS1 | N                  | Y                   | N                    |
| ttyS1 & ttyS0 | N                  | N                   | Y                    |

类似地，如果指定了两个，那么只有第一个生效。

所以，调试的时候，想要输出较多的信息，可以把两个结合起来，如 `earlyprintk=ttyS1,keep console=ttyS0`，将早期的 dmesg 和启动 console 之后的 dmesg 都保存到 vm.log 文件中，同时在 ttyS0 中可以看到后续的输出。