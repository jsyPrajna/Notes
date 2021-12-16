# Makefile

[A Simple Makefile Tutorial](https://cs.colby.edu/maxwell/courses/tutorials/maketutor/)

[Makefile Tutorial](https://makefiletutorial.com/)

[Linux Kernel Makefiles](https://www.kernel.org/doc/html/latest/kbuild/makefiles.html)

!!! tldr

    长时间不写 Makefile，基础的语法不太记得，通过两个 tutorial 掌握基础语法。再看看 Linux 内核如何使用 Makefile。

## A Simple Makefile Tutorial

有以下三个示例文件：

=== "hellomake.c"

    ```c
    #include <hellomake.h>

    int main() {
      // call a function in another file
      myPrintHelloMake();

      return(0);
    }
    ```

=== "hellofunc.c"

    ```c
    #include <stdio.h>
    #include <hellomake.h>

    void myPrintHelloMake(void) {

      printf("Hello makefiles!\n");

      return;
    }
    ```

=== "hellomake.h"

    ```c
    /*
    example include file
    */

    void myPrintHelloMake(void);
    ```

编译这几个文件的命令为：

```shell
$ gcc -o hellomake hellomake.c hellofunc.c -I.
```

`-I.` 选项指定 gcc 从当前目录查找头文件。

这种方式有几个问题：

1. 敲命令比较麻烦
2. 每次都重新编译所有文件，效率低，理想情况应该是只重新编译最新修改的文件

而 Makefile 能解决这些问题。

首先，一个最简单的 Makefile 为：

```makefile
hellomake: hellomake.c hellofunc.c
    gcc -o hellomake hellomake.c hellofunc.c -I.
```

!!! attention

    这里要注意，Makefile 中的所有命令之前都必须有一个 tab，而不能用 4 个空格，否则 make 会报错。

将以上的规则加入到 Makefile 之后执行 `make`，就会执行在 makefile 中写的编译命令，不带参数就会执行第一个规则。

将命令依赖的文件列表放在 `:` 之后，make 就知道如果这些文件中的任意一个发生变化，就需要执行对应的规则。

现在已经解决了问题 1，每次编译不再需要敲很长的命令。但是并没有解决仅编译最新修改文件的问题。

为此，试一下下面的 Makefile：

```makefile
CC=gcc
CFLAGS=-I.

hellomake: hellomake.o hellofunc.o
     $(CC) -o hellomake hellomake.o hellofunc.o
```

定义了两个常量 `CC` 和 `CFLAGS`，通过这种方式可以告知 make 如何编译文件。`CC` 表示要使用的 C 编译器，CFLAGS 则是编译命令标志。

将目标文件 *hellomake.o* 和 *hellofunc.o* 放到依赖项和规则中，make 会先编译对应的 *.c* 文件，生成 *.o* 目标文件，然后再构建可执行文件 hellomake。

```shell
$ make
gcc -I.   -c -o hellomake.o hellomake.c
gcc -I.   -c -o hellofunc.o hellofunc.c
gcc -o hellomake hellomake.o hellofunc.o
```

对于小型项目可以这样写，但是这里并没有体现对头文件的依赖。如果修改头文件，make 也不会重新编译。为此，需要告知 make 所有 *.c* 文件依赖于指定的 *.h* 文件。

添加一个简单的规则：

```makefile
CC=gcc
CFLAGS=-I.
DEPS = hellomake.h

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

hellomake: hellomake.o hellofunc.o 
	$(CC) -o hellomake hellomake.o hellofunc.o 
```

加了一个宏 `DEPS`，表示 *.c* 文件依赖的 *.h* 集合。然后定义了一个适用于所有 *.o* 文件的规则，规则声明了 *.o* 文件依赖于其对应的 *.c* 文件和 `DEPS` 宏中的 *.h* 文件。

使用 `CC` 定义的编译器，`-c` 表示生成目标文件，`-o $@` 表示将编译的输出命名目标文件名（`:` 左侧的部分，即 `%.o`），`$<` 表示第一个依赖文件。

下面的例子中，将所有的头文件列在宏 `DEPS` 中，所有的目标文件都列在宏 `OBJ` 中。

```makefile
CC=gcc
CFLAGS=-I.
DEPS = hellomake.h
OBJ = hellomake.o hellofunc.o 

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

hellomake: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)
```

如果想把 *.h* 文件放到 *include* 目录，代码放到 *src* 目录，把库文件放在 *lib* 目录，同时要把所有的 *.o* 文件集中到一起，以免到处都是。

下面的 Makefile 定义了 *include* 目录和 *lib* 目录的路径，并将目标文件放在 *src* 目录的 *obj* 子目录中。还有一个宏 `LIBS` 定义了所有需要的库。此 Makefile 需要在 *src* 目录，还包含一个 `clean` 规则，用于清除目标文件，使用 `.PHONY` 规则避免 make 操作名为 clean 的文件。

```makefile
IDIR =../include
CC=gcc
CFLAGS=-I$(IDIR)

ODIR=obj
LDIR =../lib

LIBS=-lm

_DEPS = hellomake.h
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_OBJ = hellomake.o hellofunc.o 
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))


$(ODIR)/%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

hellomake: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ 
```

!!! note

    ```makefile
    $(patsubst <pattern>,<replacement>,<text>)
    ```

    查找 text 中与 pattern 匹配的以空白字符分割的单词，并将其替换为 replacement。

    这里的 pattern 可以包括 `%` 通配符，表示任意长度字符串。如果 replacement 也含 `%`，那么这个 `%` 是指 pattern 中 `%` 所匹配的字符串。

    上面的 Makefile 使用 patsubst 进行路径拼接，将 *.h* 和 *.o* 分别放在 *include* 和 *obj* 目录下。

## Makefile Turtorial

Makefile 用于帮助决定大型程序的哪些部分需要重新编译。一般用来编译 C 或 C++ 文件，其他语言有自己的工具，还可以在程序之外，根据改变的文件运行一系列指令。下面重点介绍 C/C++ 编译用例。

如果文件的依赖项发生变化，那么文件就需要重新编译。

Make 的替代品，其他的 C/C++ 构建系统有 SCons, CMake, Banzel, Ninja, MSVC 等。其他语言有自己的工具，如 java 的 Ant, Maven, Gradle 等。

### Makefile 语法

Makefile 由一系列规则组成，规则的格式如下：

```makefile
variable = value1 value2
targets: prerequisites
    command
    command
    ...
```

- targets 是文件名，使用空格分隔，通常每个规则只有一个
- commands 是生成目标文件要执行的一系列命令，以 tab 开头，不能是空格
- prerequisites 也是文件名，使用空格分隔，运行命令之前这些文件必须存在，也称为依赖
- 变量都是字符串，使用 `${}` 或 `$()` 引用变量

想一次运行多个 target，使用下面的语法。如果一个规则有多个 target，则命令会为每个 target 执行一次。

```makefile
all: file1 file2

file1 file2:
    echo $@

等价于：

```makefile
all: file1 file2

file1:
    echo $@
file2:
    echo $@ 
```

`*` 和 `%` 在 Makefile 中都是通配符，但意思不同。

`*` 用于搜索文件系统匹配文件名，推荐在 `wildcard` 函数中使用，否则可能造成一些问题。`*` 可用在 target, prerequisites 中。

!!! danger

    `*` 不能直接用于变量定义。

    当 `*` 没有匹配文件时，会留在原地。

```makefile
thing_wrong := *.o # Don't do this! '*' will not get expanded
thing_right := $(wildcard *.o)

all: one two three four

# Fails, because $(thing_wrong) is the string "*.o"
one: $(thing_wrong)

# Stays as *.o if there are no files that match this pattern :(
two: *.o 

# Works as you would expect! In this case, it does nothing.
three: $(thing_right)

# Same as rule three
four: $(wildcard *.o)
```

`%` 很有用，有多种使用场景。

- 在匹配模式下使用时，匹配字符串中的一个或多个字符，也称为 stem
- 在替换模式下使用，它表示匹配的 stem，并替换它
- `%` 最常用于规则定义和某些特定函数

Make 支持很多个自动变量，不过常用的就以下几个：

- `$@` 表示 targets
- `$?` 表示比 target 新的依赖文件
- `$^` 表示所有依赖文件
- `$<` 表示第一个依赖文件

### Fancy Rules

#### Implicit Rules

Make 有一些自动规则，称为隐式规则。

- 编译 C 程序：`n.o` 会由 `n.c` 自动生成，命令格式为 `$(CC) -c $(CPPFLAGS) $(CFLAGS)`
- 编译 C++ 程序：`n.o` 会有 `n.c` 或 `n.cpp` 自动生成，命令格式为 `$(CXX) -c $(CPPFLAGS) $(CXXFLAGS)`
- 链接单个目标文件：`n` 会由 `n.o` 自动生成，命令为 `$(CC) $(LDFLAGS) n.o $(LOADLIBES) $(LDLIBS)`

隐式规则中有一些重要的变量：

- `CC/CXX`：C/C++ 编译器，默认是 `cc/g++`
- `CFLAGS/CXXFLAGS`：给 C/C++ 编译器的额外标志
- `CPPFLAGS`：给 C 预处理器的额外标志
- `LDFLAGS` 当编译器调用链接器时的额外标志

下面的例子就使用隐式规则进行编译。

```makefile
CC = gcc
CFLAGS = -g

# Implicit rule #1: blah is built via the C linker implicit rule
# Implicit rule #2: blah.o is built via the C compilation implicit rule, because blah.c exists
blah: blah.o

blah.c:
    echo "int main() { return 0; }" > blah.c

clean:
    rm -f blah*
```

涉及两个隐式规则：

- *blah* 由 C 链接隐式规则生成
- *blah.o* 由 C 编译隐式规则生成，因为 *blah.c* 存在

#### Static Pattern rules

静态模式规则也可以让我们少写一点 Makefile。

```makefile
targets ...: target-pattern: prereq-patterns ...
    command
```

本质是给定 target 与 target-pattern 匹配，匹配的称为 stem，使用 stem 替换到 prereq-pattern，生成目标的依赖。

一个典型的用例就是要把所有的 *.c* 编译成 *.o* 文件，手动方式为：

```makefile
objects = foo.o bar.o all.o
all: $(objects)

# 这些文件由隐式规则生成
foo.o: foo.c
bar.o: bar.c
all.o: all.c

all.c:
    echo "int main() { return 0; }" > all.c

%.c:
    touch $@

clean:
    rm -f *.c *.o all
```

使用静态模式规则的更有效方式：

```makefile
objects = foo.o bar.o all.o
all: $(objects)

# 这些文件由隐式规则生成
$(objects): %.o: %.c

all.c:
    echo "int main() { return 0; }" > all.c

%.c:
    touch $@

clean:
    rm -f *.c *.o all
```

以第一个目标文件 *foo.o* 为例，匹配目标模式，stem 被设置为 foo，依赖模式中的 `%` 就会被替换为 stem。

静态模式规则可以与 `filter` 函数配合使用，`filter` 用于匹配文件。

```makefile
obj_files = foo.result bar.o lose.o
src_files = foo.raw bar.c lose.c

.PHONY: all
all: $(obj_files)

$(filter %.o,$(obj_files)): %.o: %.c
    echo "target: $@ prereq: $<"
$(filter %.result,$(obj_files)): %.result: %.raw
    echo "target: $@ prereq: $<" 

%.c %.raw:
    touch $@

clean:
    rm -f $(src_files)
```

```shell
$ make -f Makefile1
touch foo.raw
echo "target: foo.result prereq: foo.raw"
target: foo.result prereq: foo.raw
touch bar.c
echo "target: bar.o prereq: bar.c"
target: bar.o prereq: bar.c
touch lose.c
echo "target: lose.o prereq: lose.c"
target: lose.o prereq: lose.c
```

#### Pattern Rules

模式规则更常用，但也比较混乱，一般有两种使用方式：

- 定义自己的隐式规则，如定义编译 *.c* 文件生成 *.o* 文件的模式规则：

  ```makefile
  %.o : %.c
          $(CC) -c $(CFLAGS) $(CPPFLAGS) $< -o $@
  ```

- 更简单的静态模式规则

#### Double-Colon Rules

双冒号规则允许为相同目标定义多个规则，如果是单冒号，会 warning 且只有后面的 rule 灰白执行。

```makefile
all: blah

blah::
    echo "hello"

blah::
    echo "hello again"
```

### Commands and Execution

在命令之前加 `@`，执行时不输出命令。也可以使用 `-s` 选项相当于为所有命令添加 `@`。

每条命令都执行在一个新的 shell 里（至少从效果来看是这样），例如执行 `cd` 并不影响下一条命令。

默认的 shell 是 `/bin/sh`，可以通过变量 `SHELL` 修改。

使用 `-k` 选项，即使报错也会继续运行，可用于依次执行发现所有错误。

在命令之前添加 `-` 可以抑制错误（忽略）。

使用 `-i` 选项，相当于为每条命令添加 `-`。

当使用 `ctrl+c` 终止 make 时，会删除生成的新目标文件。

如果需要递归地使用，使用 `$(MAKE)` 而不是直接 make，这样可以传递 make 标志，且本身不受影响。

比如使用不同版本的 make，那么使用 `$(MAKE)` 可以让递归的 make 与最上层保持一致。

使用 `export` 指令加一个变量，使递归的 sub-make 可以访问该变量。

还可以 export 变量，使其在 shell 中可用。

```makefile
one=this will only work locally
export two=we can run subcommands with this

all: 
    @echo $(one)
    @echo $$one
    @echo $(two)
    @echo $$two
```

```shell
$ make -f Makefile1
this will only work locally

we can run subcommands with this
we can run subcommands with this
```

使用 `.EXPORT_ALL_VARIABLES:` 可以导出所有变量。

make 可以运行多个目标 `make target1 target2`。

### Variables Pt.2

有两种风格的变量：

- `=`：递归，仅在命令使用时查找变量，而不是在定义时
- `:=`：简单地扩展，只扩展目前为止定义的，赋当前位置的值

```makefile
# Recursive variable. This will print "later" below
one = one ${later_variable}
# Simply expanded variable. This will not print "later" below
two := two ${later_variable}

later_variable = later

all: 
    echo $(one)
    echo $(two)
```

其中 `one` 是递归变量，输出时会有 later，而 `two` 是扩展变量，不会输出 later。

使用 `:=` 允许附加变量，而 `=` 会导致无限循环错误。

```makefile
one = hello
one := ${one} there
# 使用 = 会报错，因为会无限循环地搜索 one 变量
# one = ${one} there

all: 
	echo $(one)
```

`?=` 仅在变量不存在时设置变量。

行末的空格不会被 strip，但开头的会。要生成一个值为空格的变量，可以使用以下的语法：

```makefile
with_spaces = hello   # with_spaces has many spaces after "hello"
after = $(with_spaces)there

nullstring =
space = $(nullstring) # Make a variable with a single space.

all: 
    echo "$(after)"
    echo start"$(space)"end
```

这里的 `nullstring` 就是定义的一个空变量，其实也可以去掉，因为未定义的变量就是空字符串。

使用 `+=` 附加值，但会自动在两个值之间加空格。

可以使用 `override` 覆盖从命令行传来的变量。

`define` 是命令列表，并不是函数，与命令之间的分号不同，每个命令还是在单独的 shell 运行。

变量还可以分配给特定目标或目标模式。

```makefile
all: one = cool

all: 
    echo one is defined: $(one)

other:
    echo one is nothing: $(one)
```

### Conditional part of Makefiles

条件语句有以下几种：

- `ifeq/ifneq(a, b)`：判断 a, b 是否相等
- `ifdef/ifndef a`：判断 a 是否已被定义

```makefile
nullstring =
foo = $(nullstring) # end of line; there is a space here

all::
ifeq ($(strip $(foo)),)
	echo "foo is empty after being stripped"
endif
ifeq ($(nullstring),)
	echo "nullstring doesn't even have spaces"
endif

bar =
foo = $(bar)

all::
ifdef foo
	echo "foo is defined"
endif
ifndef bar
	echo "but bar is not"
endif
```

`ifdef` 不会扩展变量引用，只会看是否定义，上例中的 `foo` 虽然也是空，但是定义了。

下面这个例子使用 `findstring` 函数和 `MAKEFLAGS` 宏判断 `make -i` 标志是否存在。

```makefile
all:

ifneq (,$(findstring i, $(MAKEFLAGS)))
    echo "i was passed to MAKEFLAGS"
endif
```

### Functions

函数主要用于文本处理，调用格式为 `$(fn args)` 或 `${fn args}`。可以使用 `call` 内置函数生成自己的函数。

!!! attention

    参数之间不要包含空格，否则会被当作字符串的一部分。

#### String Substitution

```makefile
comma := ,
empty:=
space := $(empty) $(empty)
foo := a b c
bar := $(subst $(space), $(comma) , $(foo))

all: 
    @echo -$(bar)-
```

`$(subst from,to,text)` 函数为字符串替换，将 text 中的 from 替换为 to。上例中的三个参数分别为：`_`、`_,_` 和 `_a_b_c`。text 中的三个空格都被替换，最终结果为 `_,_a_,_b_,_c`。（`_` 表示空格）

`$(patsubst pattern,replacement,text)` 也是字符串替换。查找 text 中与 pattern 匹配的空格分隔的单词，并将其替换为 replacement。如果 replacement 包含一个 `%`，它将被替换为与 pattern 中 `%` 匹配的文本。只有 pattern 中的第一个 `%` 会这样处理。

有两种简写方式：

- `$(text:pattern=replacement)`
- `$(text:suffix=replacement)`，省略了 `%` 通配符。

```makefile
foo := a.o b.o l.a c.o
one := $(patsubst %.o,%.c,$(foo))
# 第一种简写
two := $(foo:%.o=%.c)
# 只有后缀的简写
three := $(foo:.o=.c)

all:
    echo $(one)
    echo $(two)
    echo $(three)
```

#### The `foreach` function

`$(forearch var,list,text)` 函数将一个由空格分隔的单词列表转换成其他的内容。var 是列表中的单词，text 为每个单词的扩展。

```makefile
foo := who are you
# 对 foo 中的每个 word，输出相同的后接感叹号的 word
bar := $(foreach wrd,$(foo),$(wrd)!)

all:
    # Output is "who! are! you!"
    @echo $(bar)
```

#### The `if` function

`$(if condition,then-part[,else-part])` 函数，类似 C 中的三目运算符。如果 condition 为 true（非空）则返回 then-part，否则返回 else-part。

#### The `call` function

Make 支持创建基本的函数，通过创建变量就可以定义函数，通过 `$(0)`、`$(1)` 的方式使用参数。然后就可以通过 `$(call variable,param,param,...)` 函数调用自定义的函数，`$(0)` 是 variable，`$(1)`、`$(2)` 等都是参数。

#### The `shell` function

`$(shell command)` 函数就是执行 shell 命令，但是它将换行符替换为空格。

### Other Features

`include filenames...` 指令告诉 make 读取其他的 Makefile。

当编译器标志 `-M` 创建基于源 Makefile 时。例如，如果一些 c 文件包含一个标题，标题会被添加到由 gcc 写的 Makefile。

!!! todo

    gcc 的某些选项可以生成 Makefile 规则，用于描述源文件的依赖。

    如 `-M`、`-MMD`、`-MP` 等，之后可以详细看一下。

`vpath <pattern> <dir_list>` 指令可以指定某些依赖存在的位置，dir_list 是由空格或冒号分隔的目录列表。意思就是对于不在当前目录中的依赖，可以使用 vpath 指令声明，某些与 pattern 匹配的依赖可以去指定的位置去搜索。使用 vpath 指令不加路径可以清除设置。

还可以使用 `VPATH` 变量指定路径，与 vpath 指令不同的是，没有了 pattern，所以可以在指定的路径中搜索所有文件。当然，当前目录永远是最高优先搜索的地方。

使用续行符反斜杠 `\` 可以可以在命令太长时使用多行。

对目标使用 `.PHONY` 可以避免 make 将 phony 目标和文件名混淆。比如，创建一个 *clean* 文件，使用 `.PHONY` 才能保证 `make clean` 正常执行。

```makefile
some_file:
    touch some_file
    touch clean

.PHONY: clean
clean:
    rm -f some_file
    rm -f clean
```

```shell
$ make -f Makefile1
touch some_file
touch clean
$ make -f Makefile1 clean
rm -f some_file
rm -f clean
# 如果没有 .PHONY
$ make -f Makefile1 clean
make: 'clean' is up to date.
```

当命令返回非零状态时，make 会停止运行并返回到依赖。使用 `.DELTE_ON_ERROR:` 会在规则失败时删除目标。会作用于所有目标，而不是像 `.PHONY` 只作用于后面一个。

### Makefile Cookbook

文章的最后给出了一个适用于中型项目的例子。它做的就是自动确定依赖关系，你要做的就是把所有的 C/C++ 文件放到 *src* 目录。

这里就用到了使用编译器为源文件生成 makefile 规则。

```makefile
TARGET_EXEC := final_program

BUILD_DIR := ./build
SRC_DIRS := ./src

# Find all the C and C++ files we want to compile
# Note the single quotes around the * expressions. Make will incorrectly expand these otherwise.
SRCS := $(shell find $(SRC_DIRS) -name '*.cpp' -or -name '*.c' -or -name '*.s')

# String substitution for every C/C++ file.
# As an example, hello.cpp turns into ./build/hello.cpp.o
OBJS := $(SRCS:%=$(BUILD_DIR)/%.o)

# String substitution (suffix version without %).
# As an example, ./build/hello.cpp.o turns into ./build/hello.cpp.d
DEPS := $(OBJS:.o=.d)

# Every folder in ./src will need to be passed to GCC so that it can find header files
INC_DIRS := $(shell find $(SRC_DIRS) -type d)
# Add a prefix to INC_DIRS. So moduleA would become -ImoduleA. GCC understands this -I flag
INC_FLAGS := $(addprefix -I,$(INC_DIRS))

# The -MMD and -MP flags together generate Makefiles for us!
# These files will have .d instead of .o as the output.
CPPFLAGS := $(INC_FLAGS) -MMD -MP

# The final build step.
$(BUILD_DIR)/$(TARGET_EXEC): $(OBJS)
    $(CC) $(OBJS) -o $@ $(LDFLAGS)

# Build step for C source
$(BUILD_DIR)/%.c.o: %.c
    mkdir -p $(dir $@)
    $(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

# Build step for C++ source
$(BUILD_DIR)/%.cpp.o: %.cpp
    mkdir -p $(dir $@)
    $(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@


.PHONY: clean
clean:
    rm -r $(BUILD_DIR)

# Include the .d makefiles. The - at the front suppresses the errors of missing
# Makefiles. Initially, all the .d files will be missing, and we don't want those
# errors to show up.
-include $(DEPS)
```