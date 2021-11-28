# Linux initcall 机制

[Linux 内核：initcall 机制与 module_init](https://www.cnblogs.com/schips/p/linux_kernel_initcall_and_module_init.html)

!!! info

    在看 iommu 初始化时，发现从 start_kernel 到 pci_iommu_init 的调用链极其长且复杂，根本不知道是怎么过去的。经过一番搜索，才知道 Linux 的 initcall 机制。

### Motivation

Linux 模块可以静态编译进内核或动态加载两种方式。对于动态加载，通常使用 `insmod` 加载到内核。而静态编译进内核的模块，会在启动时初始化。

不管是那种，都需要提供一个 init 函数。动态编译的模块使用 `module_init` 注册初始化函数。而静态编译模块的 init 函数应该如何添加？最简单的想法就是在内核 init 程序中添加对 init 函数的调用。但这并不适用于 Linux 这种大型 OS。

Linux 的解决方法就是 initcall 机制：

1. 源码编译时，告知编译器链接，自定义一个专门用来存放这些初始化函数的地址段，将对应的函数入口统一放在一起；
2. 开发者使用内核提供的宏定义 `xxx_initcall` 修饰自定义的 `init_func`，函数就会被编译器添加到上述的段中；
3. 内核启动后统一扫描这个段，按照顺序执行所有被添加的初始化。

模块之间可能存在一定的依赖关系，需要按序初始化，Linux 对此做了分级处理。

下面就根据基于源码探究 Linux(5.15.rc2) 的 initcall 机制。

initcall 和 module_init 相关的定义在 *include/linux/init.h* 和 *include/linux/module.h* 中。

```c
#ifndef MODULE
  ...   // static load
#else /* MODULE */
  ...   // dynamic load
#endif
```

静态还是动态加载可以由 Makefile 配置，指定是 `obj-y` 还是 `obj-m`。

!!! todo

    还需要看看内核如何使用 Makefile [Linux Kernel Makefiles](https://www.kernel.org/doc/html/latest/kbuild/makefiles.html)

### 静态加载：initcall 与分级

#### 定义

```c
// include/linux/init.h
/*
 * Early initcalls run before initializing SMP.
 *
 * Only for built-in code, not modules.
 */
#define early_initcall(fn)		__define_initcall(fn, early)

/*
 * A "pure" initcall has no dependencies on anything else, and purely
 * initializes variables that couldn't be statically initialized.
 *
 * This only exists for built-in code, not for modules.
 * Keep main.c:initcall_level_names[] in sync.
 */
#define pure_initcall(fn)		__define_initcall(fn, 0)

#define core_initcall(fn)		__define_initcall(fn, 1)
#define core_initcall_sync(fn)		__define_initcall(fn, 1s)
#define postcore_initcall(fn)		__define_initcall(fn, 2)
#define postcore_initcall_sync(fn)	__define_initcall(fn, 2s)
#define arch_initcall(fn)		__define_initcall(fn, 3)
#define arch_initcall_sync(fn)		__define_initcall(fn, 3s)
#define subsys_initcall(fn)		__define_initcall(fn, 4)
#define subsys_initcall_sync(fn)	__define_initcall(fn, 4s)
#define fs_initcall(fn)			__define_initcall(fn, 5)
#define fs_initcall_sync(fn)		__define_initcall(fn, 5s)
#define rootfs_initcall(fn)		__define_initcall(fn, rootfs)
#define device_initcall(fn)		__define_initcall(fn, 6)
#define device_initcall_sync(fn)	__define_initcall(fn, 6s)
#define late_initcall(fn)		__define_initcall(fn, 7)
#define late_initcall_sync(fn)		__define_initcall(fn, 7s)

#define __initcall(fn) device_initcall(fn)

// include/linux/module.h
#define module_init(x)	__initcall(x);
```

所有 `xxx_initcall` 都是 `__define_initcall(fn, id)`，其中 id 是数字或数字加 `s`，表示函数的执行优先级，数字越小，优先级越高，带 `s` 的优先级要低于不带 `s` 的优先级。

同时，可以看到，静态加载的模块可以可以使用 `module_init` 宏修饰自定义的初始化函数，最后其实就是 `device_initcall`。

!!! question

    这里 `rootfs_initcall` 对应的 id 是 `rootfs` ？

具体定义如下：

```c

#define ____define_initcall(fn, __unused, __name, __sec)	\
	static initcall_t __name __used 			\
		__attribute__((__section__(__sec))) = fn;

#define __unique_initcall(fn, id, __sec, __iid)			\
	____define_initcall(fn,					\
		__initcall_stub(fn, __iid, id),			\
		__initcall_name(initcall, __iid, id),		\
		__initcall_section(__sec, __iid))

#define ___define_initcall(fn, id, __sec)			\
	__unique_initcall(fn, id, __sec, __initcall_id(fn))

#define __define_initcall(fn, id) ___define_initcall(fn, id, .initcall##id)
```

!!! hint

    C 语言宏定义中的符号：

    - `##` 连接操作符，连接两个参数
    - `#@` 参数字符化，返回 `const char`，参数超过 4 字节会报错
    - `#` 参数字符串化
    - `\` 续行符
    - `__VA_ARGS__` 接受不定数量的参数，前面加 `##` 可以省略参数输入

以 `rootfs_initcall(pci_iommu_init)` 为例，展开这些宏定义：

```c
static initcall __initcall_name(initcall, __initcall_id(pci_iommu_init), rootfs) __used __attribute__((__section__(".initcallrootf.init"))) = pci_iommu_init;
```

- 定义了一个名字很复杂的函数指针变量，值为 `pci_iommu_init`。
- 使用 `__used` 宏，告知编译器这个符号在编译时即使没有使用也要保留。
- 使用 GNU 扩展语法 `__attribute__`，用来指定变量或结构位域的特殊属性，语法为 `__attribute__((attr_list))`，通常放在声明尾部。
- 此处的用法为 `_attribute__((__section__("section_name")))`，将目标符号放到指定的段中。
- `initcall_t` 为函数指针类型 `int *(void)`。

#### 调用

下面就分析内核启动时如何调用这些 initcall 完成一系列初始化工作。

```c
// init/main.c
start_kernel ->
  ...
  arch_call_rest_init ->
    rest_init ->
      kernel_thread(kernel_init, NULL, CLONE_FS) -> 
      kernel_init ->
        kernel_init_freeable ->
          do_basic_setup ->             
            do_initcalls ->
```

`do_initcalls` 中会执行所有 initcall 声明的函数：

```c
static initcall_entry_t *initcall_levels[] __initdata = {
	__initcall0_start,
	__initcall1_start,
	__initcall2_start,
	__initcall3_start,
	__initcall4_start,
	__initcall5_start,
	__initcall6_start,
	__initcall7_start,
	__initcall_end,
};

static void __init do_initcall_level(int level, char *command_line)
{
	initcall_entry_t *fn;

	parse_args(initcall_level_names[level],
		   command_line, __start___param,
		   __stop___param - __start___param,
		   level, level,
		   NULL, ignore_unknown_bootoption);

	trace_initcall_level(initcall_level_names[level]);
	for (fn = initcall_levels[level]; fn < initcall_levels[level+1]; fn++)
		do_one_initcall(initcall_from_entry(fn));
}

static void __init do_initcalls(void)
{
	int level;
	size_t len = strlen(saved_command_line) + 1;
	char *command_line;

	command_line = kzalloc(len, GFP_KERNEL);
	if (!command_line)
		panic("%s: Failed to allocate %zu bytes\n", __func__, len);

	for (level = 0; level < ARRAY_SIZE(initcall_levels) - 1; level++) {
		/* Parser modifies command_line, restore it each time */
		strcpy(command_line, saved_command_line);
		do_initcall_level(level, command_line);
	}

	kfree(command_line);
}
```

- 首先是静态指针数组 `initcall_levels`，每个元素都是一个 `initcall_entry_t` 指针。
- `do_initcalls` 在循环中调用 `do_initcall_level`，level 就是优先级数字。
- `do_initcall_level` 会遍历每个 level 对应的函数指针，调用 `do_one_initcall`，就是执行对应的函数。

问题来了，之前定义的时候是把各种 initcall 放到 `.initcall<level>.init`，但这里却直接从 `initcall_levels` 中取出，是怎么指过来的呢。而且这里面为什么没有 `rootfs` 的函数？

经过一番搜索，终于在 *include/asm-generic/vmlinux.lds.h* 里找到：

```c
#define INIT_CALLS_LEVEL(level)						\
		__initcall##level##_start = .;				\
		KEEP(*(.initcall##level##.init))			\
		KEEP(*(.initcall##level##s.init))			\

#define INIT_CALLS							\
		__initcall_start = .;					\
		KEEP(*(.initcallearly.init))				\
		INIT_CALLS_LEVEL(0)					\
		INIT_CALLS_LEVEL(1)					\
		INIT_CALLS_LEVEL(2)					\
		INIT_CALLS_LEVEL(3)					\
		INIT_CALLS_LEVEL(4)					\
		INIT_CALLS_LEVEL(5)					\
		INIT_CALLS_LEVEL(rootfs)				\
		INIT_CALLS_LEVEL(6)					\
		INIT_CALLS_LEVEL(7)					\
		__initcall_end = .;

#define INIT_DATA_SECTION(initsetup_align)				\
	.init.data : AT(ADDR(.init.data) - LOAD_OFFSET) {		\
		INIT_DATA						\
		INIT_SETUP(initsetup_align)				\
		INIT_CALLS						\
		CON_INITCALL						\
		INIT_RAM_FS						\
	}
```

- 首先定义了 `__initcall_start`，将其关联到 `.initcallearly.init` 段。
- 为每个 level 定义了一个 `__initcall##level##start`，关联到 `.initcall##level##.init` 和 `.initcall_levels.init` 段。
- 所以就可以遍历 `initcall_levels[level]` 中的所有函数指针并执行。

到此也就了解了 Linux 的 initcall 机制。

### 动态加载：module_init

顺带看一下动态加载的模块。

对于内核中的模块，编译时可以配置对应的 config 项是 `y` 还是 `m` 指定是要静态编译进内核还是动态加载。对应的 config 项最终在 Makefile 中组成了 `obj-y/obj-m`。

`ko` 文件被加载重定位到内核后，其作用域和静态链接的代码是完全等价的。

此时 *include/linux/module.h* 中的相关定义：

```c
/* Each module must use one module_init(). */
#define module_init(initfn)					\
	static inline initcall_t __maybe_unused __inittest(void)		\
	{ return initfn; }					\
	int init_module(void) __copy(initfn)			\
		__attribute__((alias(#initfn)));		\
	__CFI_ADDRESSABLE(init_module, __initdata);

/* This is only required if you want to be unloadable. */
#define module_exit(exitfn)					\
	static inline exitcall_t __maybe_unused __exittest(void)		\
	{ return exitfn; }					\
	void cleanup_module(void) __copy(exitfn)		\
		__attribute__((alias(#exitfn)));		\
	__CFI_ADDRESSABLE(cleanup_module, __exitdata);
```

- `__inittest` 用于检测定义的函数是否符合 `initcall_t` 类型，如果不是则会在编译时报错。
- 然后使用扩展语法 `__attribute__((alias(#initfn)))` 定义 `init_module` 为 `initfn` 的别名。所以写模块的时候也可以直接使用 `init_module` 作为初始化函数名。

自定义动态模块编译之后会生成 `name.mod.c` 文件，其中定义了一个 module 类型的 `__this_module` 变量，链接到 `.gnu.linkonce.this_module` 段。

使用 `insmod` 命令加载模块时，最终会调用 `init_module` 系统调用。

```c
SYSCALL_DEFINE3(init_module, ...) ->
  load_module ->
    do_init_module(mod) ->
      do_one_initcall(mod->init)
```

最后执行模块自定义的初始化。