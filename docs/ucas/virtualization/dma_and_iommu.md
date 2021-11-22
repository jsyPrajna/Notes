# DMA and IOMMU

[IOMMU(一)-简单介绍](https://zhuanlan.zhihu.com/p/336616452)

[IOMMU(二)-从配置说起](https://zhuanlan.zhihu.com/p/365408539)

### Direct Memory Access, DMA

CPU 和外设速度的差距不允许用 CPU 传输数据，所以有了 DMA。CPU 告知 DMA 引擎起始地址和数据大小，DMA 引擎传输完成后中断 CPU。

CPU 使用虚拟地址访存，通过 MMU 转换成物理地址。而外设访存要用总线地址，由总线控制器把总线地址定位到物理内存。DMA 内存由 CPU 分配，CPU 需要把虚拟地址转换成总线地址，然后 DMA 引擎进行 DMA 操作，最后内存由 CPU 回收。DMA 的 Cache 一致性由体系结构保证。

DMA 只是外设的数据传输通道，外设驱动通过调用内核 DMA API 完成操作，内存映射、数据对齐、缓存一致性都由内核 DMA API 实现。

外设通过 DMA 将数据传输到内核，用户态再系统调用把数据传输到用户态，开销较大。想在用户态使用 DMA，首先要获取物理地址，可以通过 */proc/self/pagemap* 获取。另一个问题是如何保证虚拟地址对应的物理地址一定存在于内存中并且固定在内存中的同一个物理地址。特别是将虚拟地址固定到物理地址。

> [VFIO - “Virtual Function I/O” — The Linux Kernel documentation](https://www.kernel.org/doc/html/latest/driver-api/vfio.html)
>
> 将设备暴露到用户态

### IOMMU

类似于 MMU，对 DMA 做地址翻译，用来解决 DMA 的安全性问题。内核使用 IOMMU 可以限制设备可写的范围。

IOMMU 更大的用处在于用户态驱动，如 DPDK 和 qemu。Guest 发起 DMA 时设置的地址是 GPA，qemu 将其转换成 HVA，然后把两个地址和 DMA 长度通知 VFIO 建立映射，VFIO 找到对应的 HPA，pin 住，让 qemu 的虚拟地址始终对应到固定的物理内存，然后建立 IOMMU 表项。IOMMU 的 IOVA 就是 GPA，DMA 要和 GPA 交换数据，就和对应的 HPA 交换数据。

### IOMMU 配置

在 BIOS 中开启 VT-d。

内核启动参数中添加 `intel_iommu=on iommu.passthrough=1`。

Qemu VFIO 设备直通：

```c
// Linux 5.10.0-rc3+
vfio_iommu_type1_ioctl
 └─vfio_iommu_type1_map_dma
     └─vfio_dma_do_map
         └─vfio_pin_map_dma
             └─vfio_iommu_map
                 └─iommu_map // __iommu_map
                     └─intel_iommu_map (domain->iommu_ops->map)
                         └─domain_pfn_mapping

```

内核 i40e 代码：

```
// Linux 5.10.0-rc3+
i40e_alloc_mapped_page
  └─dma_map_page_attrs
      └─intel_map_page (dma_ops->map_page)
          └─__intel_map_single
              ├─intel_alloc_iova
              └─domain_pfn_mapping
```

配置了 `iommu.passthrough=1` 后，内核驱动不进行 DMA 重映射，性能提升。

实现的代码如下，首先根据内核参数设置 `iommu_def_domain_type` 的值，`IOMMU_DOMAIN_IDENTITY` 表示直通，`IOMMU_DOMAIN_DMA` 表示需要 IOMMU。对于直通的设备，会在探测设备时将 `dma_ops` 结构体设置为 NULL。

```c
static void intel_iommu_probe_finalize(struct device *dev)
{
	struct iommu_domain *domain;

	domain = iommu_get_domain_for_dev(dev);
	if (device_needs_bounce(dev))
		set_dma_ops(dev, &bounce_dma_ops);
	else if (domain && domain->type == IOMMU_DOMAIN_DMA)
		set_dma_ops(dev, &intel_dma_ops);
	else
		set_dma_ops(dev, NULL);
}
```

