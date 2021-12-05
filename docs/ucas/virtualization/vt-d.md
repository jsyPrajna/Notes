

# Intel VT-d



[VT-d DMA Remapping · kernelgo](https://kernelgo.org/dma-remapping.html)

[Shared Virtual Memory for IOMMU](https://lwn.net/Articles/747230/)

[VT-d Interrupt Remapping · kernelgo](https://kernelgo.org/interrupt-remapping.html)

[VT-d Interrupt Remapping - L (liujunming.top)](http://liujunming.top/2020/10/10/VT-d-Interrupt-Remapping/)

[VT-d Posted Interrupt · kernelgo](https://kernelgo.org/posted-interrupt.html)

[VT-d Posted Interrupt - L (liujunming.top)](http://liujunming.top/2020/10/11/VT-d-Posted-Interrupt/)

[Intel VT-d (4) - Interrupt Posting - 知乎](https://zhuanlan.zhihu.com/p/51018597)

VT-d 要点：

- DMA 重映射：在 [dma_and_iommu](./dma_and_iommu.md) 中说明了 IOMMU 的原理，通过地址转换实现隔离和直通，设备使用 gPA 进行 DMA 操作，由 IOMMU 将其转换为 hPA。Intel VT-d 就是 IOMMU 的硬件实现。
  - DMA 请求按照是否包含 PASID（进程地址空间标志），分为 with-PASID 和 without-PASID。对于 PASID 相关信息会在之后单独讨论。下面只针对后者，也即是普通的 DMA 请求，仅包含请求类型、地址、大小和设备标识符。
  - VT-d 提供的 DMA 隔离是以 Domain 为单位的，虚拟化环境下可以认为一个 VM 就是一个 Domain。而直通设备的 DMA 地址空间可能是 VM 的 gPA 空间或其中某个进程的 gVA 空间或软件定义的抽象 IOVA。总之 DMA 重映射就是将设备发起的 DMA 请求转换到对应的 hPA 上。

  ![](images/vt-d.assets/image-20211201144613.png)

  - 使用 BDF 标志直通设备，引入 Root-table 和 Context-table，通过查询两个表就可以获得最后的 IO 页表。两个页表分别使用 BDF 的高、低八位作为索引。Root-table 的及地址存储在寄存器中，表项包括对应 Context-table 地址和存在标志位。而 Context-table 的表项中包含了标志位和用于 DMA 地址转换的页表地址，称为二级页表。多个设备可能分配到一个 Domain，通过通向二级页表就可实现。

  ![](images/vt-d.assets/image-20211201145255.png)

  - 一般的二级页表类似于 EPT，只不过只有设备分配到的 VM 的 HPA 范围。同时也有 IO-TLB 加速地址转换过程。

- 中断重映射：DMA 重映射解决了 DMA 的直通和隔离，而设备完成 DMA 操作之后要向 CPU 发送中断。而直通设备的 MSI 由 guest 分配，设备发送中断时的地址是 gPA，中断无法直接到达 guest。而中断重映射，IOMMU 截获中断，先将其映射到 host 的某个中断，然后再由 VMM 投递到 guest 内部。
  - 在没有中断重映射机制时，中断请求包括地址和数据字段，地址包含目标 CPU 的 APIC ID，数据包含中断向量号和投递方式。当地址字段的 bit-4 置位时，表示开启重映射。此时的地址字段不在包含目标 CPU APIC ID，而是一个 16 位的索引。bit-3 时 SHV 标志位，用于指示请求是否包含子索引。（引入子索引是为了兼容 MSI 支持对单个地址多个 data 的投递方式）
  - IOMMU 截获中断请求后，根据索引和子索引（如果有）计算重映射表的索引。每个表项 IRTE 为 16-byte，整个表占用 1M 空间。

  ![](images/vt-d.assets/image-20211201170500.png)

  - 之后要看中断重映射相关代码。

- Posted Interrupt：中断重映射改变了设备中断的投递方式，仅以 16 位的 interrupt_index 索引对应的 IRTE，中断处理更灵活。Intel 引入 Interrupt Posting 机制，从硬件层面实现中断隔离和中断自动迁移等特性。
  - 开启 posting 之后，新增了一个 64-byte Posted Interrupt Descriptor，被硬件使用来记录要求 post 的中断请求。描述符包括中断位图、目标 CPU 的 APIC ID、标志位等。
  - 当中断请求索引到的 IRTE 的 Mode 标志位置位，表示此请求按照 posting 方式处理。
  - 当直通设备投递一个中断后，中断请求会被IOMMU硬件截获，硬件首先会去查询 irq 对应的 IRTE 并从 IRTE 中提取记录的 Posted Interrupt Descriptor 地址和 vector 信息，然后更新 PIR 域和 ON 域，并且将 vector 信息写入到 VCPU 的 vAPIC Page 中，直接给处于 non-root 模式的 VCPU 注入一个中断，整个过程不需要 VMM 的介入从而十分高效。

  ![](images/vt-d.assets/image-20211202162412.png)

  - 硬件处理流程：当 VT-d 硬件接收到其下 I/O 设备传递过来的中断请求时，会先查看自己的中断重定向功能是否打开，如果没有打开则，直接上传给 LAPIC。如果中断重定向功能打开，则会查看中断请求的格式，如果是不可重定向格式，则直接将中断请求提交给 LAPIC。如果是可重定向的格式，则会根据算法计算 interrupt_index 值，对中断重定向表进行索引找到相应的 IRTE。然后，查看 IRTE 中的 interrupt mode，如果为0，则该 IRTE 的格式为 remapped，即立即根据 IRTE 的信息产生一个新的中断请求，提交到 LAPIC。如果 interrupt mode为 1，则表示该 IRTE 的格式为 posted，根据 IRTE 中提供的 PI 描述符的地址，读取内容，并根据其 ON、URG 和 SN 的设置判断是否需要立即产生一个 notification event，如果不需要，则只是将该中断信息记录到描述符位图中，等待 VMM 的后续处理。如果需要，则根据描述符（会提供目标 APIC ID、vector、传输模式和触发模式等信息）产生一个 notification event，同时将 ON 置位。

  ![](images/vt-d.assets/image-20211202164032.png)

  - VMM 需要为 posting 做一些额外的机制。之后具体看一下。