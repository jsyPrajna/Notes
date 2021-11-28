# On Glitch to Rule Them All: Fault Injection Attacks Against AMD's Secure Encrypted Virtualization

[pdf]([CCS%202021]%20One%20Glitch%20to%20Rule%20Them%20All%20Fault%20Injection%20Attacks%20Against%20AMD‘s%20Secure%20Encrypted%20Virtualization.pdf)

AMD SEV 将安全敏感操作放到 AMD-SP 上，本文介绍了通过针对 AMD-SP 来攻击 SEV VM 的方式，一种电压故障攻击，攻击者可以在 AMD-SP 上执行 payload。攻击者可以部署自定义 SEV 固件，可以解密 VM 内存、提取 CPU 认证密钥，从而伪造认证报告。同时逆向了 SEV-SNP 引入的 Versioned Chip Endorsement Key, VCEK 机制，它将认证密钥与 TCB 组件固件版本绑定，攻击者可以导出 VCEK。

## Introduction

之前的研究[^1][^2][^3] 证明 AMD-SP 是 SEV 的 Single Point of Failure 单点故障，但仅限于特定的 CPU 类型。

故障攻击 fault attacks 不依赖与软件问题，而是迫使正常代码进入非预期状态，[^4] 对 Intel SGX 进行攻击。

鉴于 AMD-SP 在 SEV 中的重要地位，针对 AMD-SP 的攻击可能会绕过所有安全保证。本文要研究的就是对 AMD-SP 的故障注入攻击对 SEV 有何影响。

首先分析了 SEV 对针对 AMD-SP 物理攻击的敏感性，通过控制 SoC 电压，导致 AMD-SP ROM bootloader 执行错误，从而完全控制可信根。在此能力上，可以提取 SEV 相关秘密信息，如芯片认证密钥 CEK，可用于装载不需要物理访问权限的软件攻击。SEV-SNP 引入的 VCEK 机制将 TCB 版本与 CEK 绑定，攻击者可以提取 VCEK 种子，从而为所有可能的固件版本生成有效的 VCEK。

初始化阶段确定 CPU 相关的故障参数，如降压的长度和深度，之后就可以实施全自动攻击。在所有架构的 EPYC 上都能成功。

攻击通过欺骗 AMD-SP ROM bootloader 接受攻击者控制的公钥来在 AMD-SP 上执行任意代码。AMD-SP 使用公钥验证固件组件真实性。基于此能力，攻击者可以泄露影响 SEV 系统的密钥或部署自定义的  SEV 固件。

## Related Work

针对 CPU 安全敏感操作的电压故障攻击受到广泛的关注，之前的攻击主要集中在小型嵌入式系统和 SoC。近期报道了一些针对 Intel 桌面和服务器 CPU 的电压故障攻击，使用稳压器的接口导致供电故障。通过基于软件的电压调节接口注入故障，可以破坏 SGX 的完整性，甚至可以提取 enclave 中的密钥。

与本文工作最相关的是[^4]，Chen 等人展示了第一个针对 SGX enclave 的物理攻击，称为 VoltPillager。提高了基于软件的故障攻击的事件精度，利用直接访问稳压器注入故障。

对 SEV 的攻击都依赖于写 guest 的加密内存、访问 guest 通用寄存器或修改 gPA 到 sPA 映射。SEV-ES 和 SEV-SNP 缓解了这些攻击。[^5] 则从另一个方向研究，通过修改 cpuid 指令的结果，攻击者欺骗 guest 不启用 SEV。SEV-SNP 引入可信 CPUID 功能。[^2] 分析了 SEV 的远程认证机制，揭示了 AMD-SP 固件的安全问题，使攻击者能够自定义 SEV 固件并提取远程认证使用的密钥。但只在 Zen 1 上有效。

## Backgroud

SEV 提供的运行时保护和远程认证都需要 hypervisor 使用 AMD-SP 固件提供的接口。

### AMD-SP 启动过程

在[^2]中分析了 EPYC ZEN1 上的 AMD-SP 启动过程。首先从一个不可更新的 ROM bootloader 执行，从一个可修改的 SPI flash 加载并验证 RSA 公钥。公钥负责验证后续从 SPI flash 加载文件的完整性，而公钥本身使用存在 bootloader 中的哈希验证。公钥其实就是 AMD Root Key, ARK。

![image-20211123100112384](images/fault_injection.assets/image-20211123100112384.png)

然后进入下一个启动阶段，启动 SPI flash 上的 PSP OS 和 SEV 固件，都是用 ROM bootloader 加载的公钥验证。而在 Zen3 中，PSP OS 和 SEV 固件都加密，且使用 PSP OS 中的公钥验证。

### 电压故障注入

集成电路需要在特定条件下运行，受电源电压、时钟稳定性、温度和电磁场等影响。供压线上的故障，可能导致 CMOS 产生计算错误，位反转、指令损坏、跳过指令等错误。而在执行加密算法期间触发这些错误就可能泄露密钥或铭文信息。也可能绕过安全检查，获得代码执行等。

## Attack Scenario

攻击者有物理权限，或能访问云服务提供商的维护接口。基于这样的能力，展示以下的两种方法访问 SEV 保护的 VM 数据。

SEV API 提供调试功能，允许加密或解密 VM 内存。正常情况下需要在初始部署时显式地开启。而攻击者可以覆盖策略强制开启调试功能，替换 SEV 固件。或者可以把目标 VM 迁移到另一个系统，然后使用调试 API 解密内存。

攻击者还可以提取 CPU 特定的认证密钥，签名任意的 SEV 认证报告，欺骗 VM 所有者接受一个恶意的迁移代理 MA。而 MA 也是 TCB 的一部分，可以访问 VM 的离线加密密钥 OEK，从而解密内存。

而以上两个场景都需要获取 AMD-SP 上的代码执行，本文中是通过电压故障注入实现的。








[^1]: https://media.ccc.de/v/36c3-10942-uncover_understand_own_-_regaining_control_over_your_amd_cpu
[^2]: Robert Buhren, Christian Werling, and Jean-Pierre Seifert. Insecure Until Proven Updated Analyzing AMD SEV's Remote Attestation. CCS 2019.
[^3]: [CVE - CVE-2019-9836 (mitre.org)](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-9836)
[^4]: Zitai Chen, Georgios Vasilakis, Kit Murdock, Edward Dean, David Oswald, and Flavio D. Garcia. VoltPillager: Hardware-based fault injection attacks against Intel SGX Enclaves using the SVID voltage scaling interface. USENIX 2021.
[^5]: Martin Radev and Mathias Morbitzer. Exploiting Interfaces of Secure Encrypted Virtual Machines. ROOT 2020.
