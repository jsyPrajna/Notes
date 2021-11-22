# GCC Inline Assembly

[ucore_os_docs - GCC扩展内联汇编](https://chyyuu.gitbooks.io/ucore_os_docs/content/lab0/lab0_2_3_1_4_extend_gcc_asm.html)

## AT&T汇编基本语法

AT&T 格式的汇编，与 Intel 格式有一些不同。二者语法上主要有以下几个不同：
```assembly
* 寄存器命名原则
	AT&T: %eax                      Intel: eax
* 源/目的操作数顺序 
	AT&T: movl %eax, %ebx           Intel: mov ebx, eax
* 常数/立即数的格式　
	AT&T: movl $_value, %ebx        Intel: mov eax, _value
  把value的地址放入eax寄存器
	AT&T: movl $0xd00d, %ebx        Intel: mov ebx, 0xd00d
* 操作数长度标识 
	AT&T: movw %ax, %bx             Intel: mov bx, ax
* 寻址方式 
	AT&T:   immed32(basepointer, indexpointer, indexscale)
	Intel:  [basepointer + indexpointer × indexscale + imm32]
```
如果操作系统工作于保护模式下，用的是32位线性地址，所以在计算地址时不用考虑 segment:offset 的问题。上式中的地址应为：
```
imm32 + basepointer + indexpointer × indexscale
```
下面是一些例子：
```assembly
* 直接寻址 
        AT&T:  foo                         Intel: [foo]
        boo是一个全局变量。注意加上$是表示地址引用，不加是表示值引用。对于局部变量，可以通过堆栈指针引用。
        
* 寄存器间接寻址 
        AT&T: (%eax)                        Intel: [eax]
        
* 变址寻址 
        AT&T: _variable(%eax)               Intel: [eax + _variable]
        AT&T: _array( ,%eax, 4)             Intel: [eax × 4 + _array]
        AT&T: _array(%ebx, %eax,8)          Intel: [ebx + eax × 8 + _array]
```

## GCC基本内联汇编

GCC 提供了两类内联汇编语句（inline asm statements）：基本内联汇编语句（basic inline asm statement)和扩展内联汇编语句（extended inline asm statement）。

GCC基本内联汇编很简单，一般是按照下面的格式：
	
```
asm("statements");
```

例如：

```	
asm("nop"); asm("cli");
```

`asm` 和 `__asm__` 的含义是完全一样的。如果有多行汇编，则每一行都要加上 `\n\t`，换行符和 tab，是为了让 gcc 把内联汇编代码翻译成一般的汇编代码时能够保证换行和留有一定的空格。对于基本 asm 语句，GCC编译出来的汇编代码就是双引号里的内容。例如：

```c
asm("pushl %eax\n\t"
	"movl $0,%eax\n\t"
	"popl %eax"
);
```
实际上gcc在处理汇编时，是要把asm(...)的内容"打印"到汇编文件中，所以格式控制字符是必要的。再例如：
```c
asm("movl %eax, %ebx");
asm("xorl %ebx, %edx");
asm("movl $0, _boo);
```
在上面的例子中，由于我们在内联汇编中改变了 edx 和 ebx 的值，但是由于 gcc 的特殊的处理方法，即先形成汇编文件，再交给 GAS 去汇编，所以 GAS 并不知道我们已经改变了 edx和 ebx 的值，如果程序的上下文需要 edx 或 ebx 作其他内存单元或变量的暂存，就会产生没有预料的多次赋值，引起严重的后果。对于变量 `_boo` 也存在一样的问题。为了解决这个问题，就要用到扩展 GCC 内联汇编语法。

## GCC扩展内联汇编

使用GCC扩展内联汇编的例子如下：

```c
#define read_cr0() ({ \
unsigned int __dummy; \
__asm__( \
    "movl %%cr0,%0\n\t" \
    :"=r" (__dummy)); \
__dummy; \
})
```

它代表什么含义呢？这需要从其基本格式讲起。GCC扩展内联汇编的基本格式是：          

```c
asm [volatile] ( Assembler Template
   : Output Operands
   [ : Input Operands
   [ : Clobbers ] ])
```

其中，`__asm__` 表示汇编代码的开始，其后可以跟 `__volatile__`（这是可选项），其含义是避免 asm 指令被删除、移动或组合，在执行代码时，如果不希望汇编语句被 gcc 优化而改变位置，就需要在 asm 符号后添加 volatile 关键词：`asm volatile(...)`；或者更详细地说明为：`__asm__ __volatile__(...)`；然后就是小括弧，括弧中的内容是具体的内联汇编指令代码。 "<asm routine>" 为汇编指令部分，例如，"movl %%cr0,%0\n\t"。数字前加前缀 “％“，如％1，％2等表示使用寄存器的样板操作数。可以使用的操作数总数取决于具体CPU中通用寄存器的数 量，如Intel可以有8个。指令中有几个操作数，就说明有几个变量需要与寄存器结合，由gcc在编译时根据后面输出部分和输入部分的约束条件进行相应的处理。由于这些样板操作数的前缀使用了”％“，因此，在用到具体的寄存器时就在前面加**两个“％”**，如**%%cr0**。输出部分（output operand list），用以规定对输出变量（目标操作数）如何与寄存器结合的约束（constraint）,输出部分可以有多个约束，互相以逗号分开。每个约束以“＝”开头，接着用一个字母来表示操作数的类型，然后是关于变量结合的约束。例如，上例中：

```
:"=r" (__dummy)
```

`＝r` 表示相应的目标操作数（指令部分的%0）可以使用任何一个通用寄存器，并且变量__dummy 存放在这个寄存器中，但如果是：               

```
:"＝m"(__dummy)
```

`＝m` 就表示相应的目标操作数是存放在内存单元__dummy中。表示约束条件的字母很多，下表给出几个主要的约束字母及其含义：

<table>
	<tr><td>字母</td><td>含义</td></tr>
	<tr><td>m, v, o</td><td>内存单元</td></tr>
	<tr><td>R</td><td>任何通用寄存器</td>	</tr>
	<tr><td>Q</td><td>寄存器eax, ebx, ecx,edx之一</td></tr>
	<tr><td>I, h</td><td>直接操作数</td></tr>
	<tr><td>E, F</td><td>浮点数</td></tr>
	<tr><td>G</td><td>任意</td></tr>
	<tr><td>a, b, c, d</td><td>寄存器eax/ax/al, ebx/bx/bl, ecx/cx/cl或edx/dx/dl</td></tr>
	<tr><td>S, D</td><td>寄存器esi或edi</td></tr>
	<tr><td>I</td><td>常数（0～31）</td></tr>
</table>

输入部分（input  operand list）：输入部分与输出部分相似，但没有“＝”。如果输入部分一个操作数所要求使用的寄存器，与前面输出部分某个约束所要求的是同一个寄存器，那就把对应操作数的编号（如“1”，“2”等）放在约束条件中。在后面的例子中，可看到这种情况。修改部分（clobber list,也称 乱码列表）:这部分常常以“memory”为约束条件，以表示操作完成后内存中的内容已有改变，如果原来某个寄存器的内容来自内存，那么现在内存中这个单元的内容已经改变。乱码列表通知编译器，有些寄存器或内存因内联汇编块造成乱码，可隐式地破坏了条件寄存器的某些位（字段）。 注意，指令部分为必选项，而输入部分、输出部分及修改部分为可选项，当输入部分存在，而输出部分不存在时，冒号“：”要保留，当“memory”存在时，三个冒号都要保留，例如

```c
#define __cli() __asm__ __volatile__("cli": : :"memory")
```

下面是一个例子：

```c
int count=1;
int value=1;
int buf[10];
void main()
{
    asm(
        "cld \n\t"
        "rep \n\t"
        "stosl"
    :
    : "c" (count), "a" (value) , "D" (buf)
    );
}
```

得到的主要汇编代码为：

```assembly
movl count,%ecx
movl value,%eax
movl buf,%edi
#APP
cld
rep
stosl
#NO_APP
```

cld,rep,stos这几条语句的功能是向buf中写上count个value值。冒号后的语句指明输入，输出和被改变的寄存器。通过冒号以后的语句，编译器就知道你的指令需要和改变哪些寄存器，从而可以优化寄存器的分配。其中符号"c"(count)指示要把count的值放入ecx寄存器。类似的还有：

	a eax
	b ebx
	c ecx
	d edx
	S esi
	D edi
	I 常数值，(0 - 31)
	q,r 动态分配的寄存器
	g eax,ebx,ecx,edx或内存变量
	A 把eax和edx合成一个64位的寄存器(use long longs)

也可以让gcc自己选择合适的寄存器。如下面的例子：

```c
asm("leal (%1,%1,4),%0"
    : "=r" (x)
    : "0" (x)
);
```

这段代码到的主要汇编代码为：

```x86asm
movl x,%eax
#APP
leal (%eax,%eax,4),%eax
#NO_APP
movl %eax,x
```

几点说明：

* [1] 使用q指示编译器从eax, ebx, ecx, edx分配寄存器。
使用r指示编译器从eax, ebx, ecx, edx, esi, edi分配寄存器。
* [2] 不必把编译器分配的寄存器放入改变的寄存器列表，因为寄存器已经记住了它们。
* [3] "="是标示输出寄存器，必须这样用。
* [4] 数字%n的用法：数字表示的寄存器是按照出现和从左到右的顺序映射到用"r"或"q"请求的寄存器．如果要重用"r"或"q"请求的寄存器的话，就可以使用它们。
* [5] 如果强制使用固定的寄存器的话，如不用%1，而用ebx，则：

```c
asm("leal (%%ebx,%%ebx,4),%0"
    : "=r" (x)
    : "0" (x) 
);
```

> 注意要使用两个%,因为一个%的语法已经被%n用掉了。

参考：
- [GCC Manual， 版本为5.0.0 pre-release,6.43节（How to Use Inline Assembly Language in C Code）](https://gcc.gnu.org/onlinedocs/gcc.pdf)
- [GCC-Inline-Assembly-HOWTO](http://www.ibiblio.org/gferg/ldp/GCC-Inline-Assembly-HOWTO.html)

