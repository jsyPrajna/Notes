# Platform Device

[Platform Devices and Drivers - Linux driver implementer's API guide](https://www.kernel.org/doc/html/latest/driver-api/driver-model/platform.html)

[Linux驱动之Platform device/driver](https://zhuanlan.zhihu.com/p/142951659)

!!! tldr

    所谓 platform device 是通常在系统中显示为自治实体的设备，包括传统的基于端口的设备和外设总线的主机桥，以及集成在 SoC 中的大多数控制器。它们的共同点是从 CPU 总线直接寻址。平台设备很少通过其他类型的总线连接，即使有，它的寄存器仍可以直接寻址。