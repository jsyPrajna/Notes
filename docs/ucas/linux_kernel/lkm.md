# Linux Kernel Module

## Hello World

一个最简单的内核模块如下：

```c
// lkm_test.c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

static int __init test_init(void) {
 printk(KERN_INFO "Hello, World!\n");
 return 0;
}
static void __exit test_exit(void) {
 printk(KERN_INFO "Goodbye, World!\n");
}
module_init(test_init);
module_exit(test_exit);

MODULE_LICENSE("GPL");
```

```makefile
obj-m:=lkm_test.o

KDIR=/lib/modules/$(shell uname -r)/build

default:
	$(MAKE) -C $(KDIR) M=$(shell pwd) modules

clean:
	$(MAKE) -C $(KDIR) M=$(shell pwd) clean

```

## 自定义内核下 LKM 编译报错问题。

使用 make-kpkg 编译生成 Linux v5.15 的 kernel_image 和 kernel_headers deb 包，安装内核后，编译内核模块报错。

尝试更换内核版本和编译器版本，都无法解决。

编译、安装内核和编译内核模块的命令如下。

```shell
# compile linux kernel
$ sudo make-kpkg --jobs 32 --initrd --revision=5.15.32 kernel_image kernel headers
# install kernel deb-pkg
$ sudo dpkg -i linux-image-5.15.32_5.15.32_amd64.deb  linux-headers-5.15.32_5.15.32_amd64.deb

Selecting previously unselected package linux-image-5.15.32.
(Reading database ... 270138 files and directories currently installed.)
Preparing to unpack linux-image-5.15.32_5.15.32_amd64.deb ...
Examining /etc/kernel/preinst.d/
run-parts: executing /etc/kernel/preinst.d/intel-microcode 5.15.32 /boot/vmlinuz-5.15.32
Done.
Unpacking linux-image-5.15.32 (5.15.32) ...
Selecting previously unselected package linux-headers-5.15.32.
Preparing to unpack linux-headers-5.15.32_5.15.32_amd64.deb ...
Unpacking linux-headers-5.15.32 (5.15.32) ...
Setting up linux-image-5.15.32 (5.15.32) ...

 Hmm. There is a symbolic link /lib/modules/5.15.32/build
 However, I can not read it: No such file or directory
 Therefore, I am deleting /lib/modules/5.15.32/build


 Hmm. The package shipped with a symbolic link /lib/modules/5.15.32/source
 However, I can not read the target: No such file or directory
 Therefore, I am deleting /lib/modules/5.15.32/source

Running depmod.
...

# compile module on custom kernel
$ make
make -C /lib/modules/5.15.32/build M=/home/ubuntu/Dev/trace modules
make[1]: Entering directory '/usr/src/linux-headers-5.15.32'
make[2]: *** No rule to make target '/home/ubuntu/Dev/trace/lkm_test.o', needed by '/home/ubuntu/Dev/trace/lkm_test.mod'.  Stop.
make[1]: *** [Makefile:1868: /home/ubuntu/Dev/trace] Error 2
make[1]: Leaving directory '/usr/src/linux-headers-5.15.32'
make: *** [Makefile:7: default] Error 2
```

报错提示 No rule to make target，搜了很久也没找到解决方案。（有说要重新安装 linux-headers 包的，但是重新编译并安装了很多遍都没有用。）

最后，发现是编译命令问题，不应使用 make-kpkg，而是要用 make bindev-pkg，后者是 debian 官方提供的 deb 包生成方式。[二者的区别](https://unix.stackexchange.com/questions/238469/difference-between-make-kpkg-and-make-deb-pkg)

## LKM 添加 include 路径

[Building External Modules](https://docs.kernel.org/kbuild/modules.html)

问题描述：使用 ftrace hook KVM 中的函数，要正常使用 KVM 中定义的结构体，需要引用 KVM 相关头文件。如 vcpu_svm 结构体定义在 *arch/x86/include/asm/svm.h* 头文件中，如何引用这一头文件？

在 Makefile 中添加：

```makefile
ccflags-y := -Iarch/x86/include
```

在内核模块源码中引用 *svm.h* :

```c
#include <asm/svm.h>
```

## LKMPG

内核模块开发参考：

[Book: The Linux Kernel Module Programming Guide](https://sysprog21.github.io/lkmpg/)

[Github: LKMPG](https://github.com/sysprog21/lkmpg)