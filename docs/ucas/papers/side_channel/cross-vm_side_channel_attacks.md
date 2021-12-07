## Cross-VM CSCAs

跨虚拟机实现缓存侧信道攻击

### taskset

设置或检索进程的 CPU 相关性。

CPU 相关性（*affinity*）是一个调度程序属性，可以将进程绑定到一组指定的 CPU 上，该进程不会在其他 CPU 上允许。

位掩码表示法，从低到高每位代表一个 CPU（省略 0x 也会按十六进制算）：

```
0x0001 
	is processor #0,
0x0003
	is processors #0 and #1,
32	(00110010b)
	is processors #1, #4 and #5
```

或者用 `-c, --cpu-list` 选项后的 CPU 列表：

```
-c 0-2, 6
	is processors #0, #1, #2 and #6,
-c 0-10:2
	is processors #0, #2, #4, #6, #8 and #10
```

默认行为是使用给定的掩码允许新命令：

```shell
$ taskset mask command [arguments]
```

检索已有任务的 CPU 相关性：

```shell
$ taskset -p pid
```

设置已有任务的 CPU 相关性“

```shell
$ taskset -p mask pid
```

### KSM

Kernel Samg-page Merging

[基于KSM的内存优化方法分析-技术开发专区 (it168.com)](http://tech.it168.com/a2016/1101/3005/000003005933.shtml)

[8.3. Kernel Same-page Merging (KSM) Red Hat Enterprise Linux 7 | Red Hat Customer Portal](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/virtualization_tuning_and_optimization_guide/chap-ksm)

使用 `ksmtuned` 控制 KSM 进行内存页扫描和合并

修改 *ksmtuned.conf* 调整 KSM 参数：

```
# Configuration file for ksmtuned.

# How long ksmtuned should sleep between tuning adjustments
# KSM_MONITOR_INTERVAL=60

# Millisecond sleep between ksm scans for 16Gb server.
# Smaller servers sleep more, bigger sleep less.
# KSM_SLEEP_MSEC=10

# KSM_NPAGES_BOOST=300
# KSM_NPAGES_DECAY=-50
# KSM_NPAGES_MIN=64
# KSM_NPAGES_MAX=1250

KSM_THRES_COEF=80
# KSM_THRES_CONST=2048

# uncomment the following if you want ksmtuned debug info

LOGFILE=/var/log/ksmtuned
DEBUG=1
```

关键在于 `KSM_THRES_COEF` 和 `KSM_THRES_CONST`，前者是阈值系数，KSM 将总内存乘系数的结果和后者之间的较大值作为阈值。当空闲内存小于阈值时，才会启动 KSM。

### 攻击代码

[yshalabi/covert-channel-tutorial](https://github.com/yshalabi/covert-channel-tutorial)

[IAIK/flush_flush](https://github.com/IAIK/flush_flush)

[Mastik](https://github.com/Secure-AI-Systems-Group/Mastik)

### rdtsc & rdtscp

