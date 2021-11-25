# DMA and IOMMU

[IOMMU(一)-简单介绍 - 知乎](https://zhuanlan.zhihu.com/p/336616452)

[Intel IOMMU Introduction · kernelgo](https://kernelgo.org/intel_iommu.html)

[14. Linux IOMMU Support — The Linux Kernel documentation](https://www.kernel.org/doc/html/latest/x86/intel-iommu.html)

[Linux x86-64 IOMMU 详解（一）—— IOMMU 简介](https://blog.csdn.net/qq_34719392/article/details/114834467)

[Linux x86-64 IOMMU 详解（五）—— Intel IOMMU 初始化流程](https://blog.csdn.net/qq_34719392/article/details/117563480)

DMA & IOMMU 要点：

- DMA 是为了不用 CPU 传输数据，CPU 告知 DMA 引擎起始地址和数据大小，DMA 引擎传输完成后中断通知 CPU。DMA 下设备可以访问整个物理地址空间，存在安全隐患。

  ![](images/dma_and_iommu.assets/image-20211124163329.png)

- IOMMU 通过地址转换解决安全问题，可以实现用户态驱动和虚拟机设备直通。另外，可以将连续的虚拟地址映射到不连续的物理内存片段，在此之前设备访问的物理空间必须是连续的。

  ![](images/dma_and_iommu.assets/image-20211124162518.png)

  ![](images/dma_and_iommu.assets/image-20211124162632.png)

- 内核对 Intel IOMMU 初始化流程


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

