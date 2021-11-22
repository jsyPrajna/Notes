# Device Virtualization

## Overview

完全虚拟化、半虚拟化（如 Virtio）再到硬件辅助虚拟化。

- 完全虚拟化，软件模拟，对 guest 透明，效率低，Vhost。
- 半虚拟化，Virtio，驱动与模拟设备交互不再使用寄存器等传统的 I/O 方式，而是采用 Virtqueue
- 硬件辅助虚拟化，VT-d 将设备整个透传给虚拟机，SR-IOV 从硬件层面虚拟

## PCI

Peripheral Component Interconnect, PCI 外设组件互联标准

PCI 约定，每个 PCI 设备都需要实现一个称为配置空间的结构，实际就是若干寄存器的集合，其大小为 256 bytes，包括预定义头 64 bytes 和设备相关部分。预定义头部定义了 PCI 设备的基本信息以及通用控制相关部分，包括 Vender ID、Device ID 等。设备驱动根据这两个 ID 匹配设备。之后的设备相关部分包括如存储设备的能力 Capabilities，如支持 MSI(X) 中断机制，就是利用这部分存储中断信息。操作系统初始化中断时将为 PCI 设备分配的中断信息写入 PCI 配置空间的设备相关部分。系统初始化后，BIOS 或 UEFI 将把 PCI 设备的配置空间映射到处理器的 I/O 地址空间，OS 通过 I/O 端口访问配置空间的寄存器。PCIE 将配置空间扩展到 4096 bytes，处理器使用 MMIO 访问配置空间。

PCI 设备还有板上存储空间，处理器需要将这些空间映射到地址空间访问。PCI 设备通过配置空间的 6 个Base Address Registers, BAR 指定所需空间大小以及映射方式，由 BIOS 或 UEFI 在系统初始化时访问 BAR，统一为 PCI 设备划分地址空间。

PCI 设备连接在 PCI 总线上，PCI 总线通过 PCI Host Bridge 与 CPU 总线相连。PCI Host Bridge 内部有两个寄存器用于系统软件访问 PCI 设备的配置空间，先访问 CONFIG_ADDRESS 设置地址，再对 CONDIF_DATA 发起访问操作。CONFIG_ADDRESS 包括总线号、设备号、功能号和寄存器地址。