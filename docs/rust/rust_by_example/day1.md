[toc]

# Day1

## Hello World

文档注释 `///`，支持 markdown。

### 格式化输出

`std::fmt` 中的一系列宏：

- `format!` 格式化文本，返回到字符串
- `print!` 输出到控制台 stdout，`println!` 追加换行符
- `eprint!` 输出到标准错误 stderr，`eprintln!` 追加换行符

使用 `{}` 格式化字符串， 用法见文档 [std::fmt](https://doc.rust-lang.org/std/fmt/)。

```rust
let pi = 3.141592;
println!("Pi is roughly {:.3}", pi);

/*
Pi is roughly 3.142
*/
```

`std::fmt` 包含多种 `traits`（特征）控制文字显示，其中重要的两种 trait 的基本形式为：

- `fmt::Debug`：使用 `{:?}` 标记，格式化文本供调试使用
- `fmt::Display`：使用 `{}` 标记，更友好的格式化文本风格

所有类型要想使用 `std::fmt` 格式化输出，都要实现至少一个可打印的 trait。自动的实现只为一些类型提供，如 `std` 库中的类型。所有其他类型都必须手动实现。

而所有类型都能推导（derive，自动创建）`fmt::Debug` 的实现，但 `fmt::Display` 需要手动实现。Rust 通过 `{:#?}` 提供优化的输出功能（结构体自动换行等）。

实现 `fmt::Display` 可以自定义输出，手动实现 trait，实例如下：

```rust
use std::fmt;

struct Structure(i32);

impl fmt::Display for Structure {
    // Display trait 要求函数签名为 fmt
    fn fmt(&self, f:&mut fmt::Formatter) -> fmt::Result {
        // 将 self 的第一个元素写入到给定的输出流
        write！(f, "{}", self.0)
    }
}
```

对于 `Vec<T>` 这种泛型容器，标准库都没有实现，可以使用 `fmt::Debug`。而对任何非泛型的容器，`fmt::Display` 都能够实现。

格式化输出通过格式化字符串指定，如 `{:X}, {:o}` 等，格式化功能由 trait 实现，每种参数类型对应一种 trait。最常见的 trait 就是 Display，可以处理未指定参数类型的情况。参数类型和对应的 trait 见文档 [std::fmt](https://doc.rust-lang.org/std/fmt/#formatting-traits)。

## Primitives 原生类型

标量类型:

| 长度    | 有符号整型 | 无符号整型 | 浮点  | 字符   |
| ------- | ---------- | ---------- | ----- | ------ |
| 8-bit   | `i8`       | `u8`       |       |        |
| 16-bit  | `i16`      | `u16`      |       |        |
| 32-bit  | `i32`      | `u32`      | `f32` | `char` |
| 64-bit  | `i64`      | `u64`      | `f64` |        |
| 128-bit | `i128`     | `u128`     |       |        |
| arch    | `isize`    | `usize`    |       |        |

- `bool`，`true/false`

- 单元类型，唯一可能的值就是 `()` 这个空元组

复合类型：数组和元组

变量可以显式地指示类型。整型默认为 `i32`，浮点型默认为 `f64`，可以通过后缀方式声明字面值类型。Rust 还可以根据上下文推断类型。

### 元组

元组使用 `()` 构造，可以拥有任意多的值。

创建单元素元组需要加都要，以区分于被括号包含的字面量。

元组可以被解构，将值绑定给变量。

### 数组和切片

数组是相同类型对象的集合，在内存中连续存储。使用 `[]` 创建，数组的大小在编译时就被确定，类型标记为 `[T; size]`。

切片 *slice* 是一个双字对象，第一个字是指向数据的指针，第二个字是切片的长度。切片大小在编译时不确定。slice 可以用于借用数组的一部分，类型标记为 `$[T]`。

## Custom Types 自定义类型

结构体、枚举类型以及常量。

### 结构体

- 元组结构体，即具名元组
- C语言风格结构体
- 单元结构体，不带字段，在泛型中很有用

### 枚举

使用 `enum` 关键字创建一个从数个不同取值中选其一的枚举类型。变量名和类型共同指定了取值的种类，可以是单元结构体、元组结构体或普通的结构体。

```rust
enum WebEvent {
    PageLoad,										// 单元结构体
    PageUnload,
    KeyPress(char),									// 元组结构体		
    Paste(String),
    Click { x: i64, y: i64 }
}
```

使用枚举名加 `::` 获取枚举成员，可以使用 ` type` 关键字对枚举进行重命名。

使用 `use` 声明，就可以不写出名称的完整路径。

枚举可以类似 C 语言风格使用，转整型，隐式从 0 开始，也可以显式地赋值。

枚举的常见用法是创建链表，示例代码见 [enum.rs](./enum.rs)。

### 常量

Rust 有两种常量，都需要显式地声明。

- `const`：不可改变的值，常用。
- `static`：具有 `'static` 生命周期的，加上 `mut` 也可以是可变的。

## Variable Bindings 变量绑定

使用 `let` 将值绑定到变量，绑定时需要说明类型。多数情况下，编译器可以从上下文推导出变量类型。

未使用的变量绑定会 warning，可以在变量名前加 `_` 消除告警。

变量绑定默认是不可变的，使用 `mut` 关键是显式地标志其可变。

变量绑定有作用域，限定在代码块中生存。允许将变量名重绑定实现变量遮蔽。可以利用遮蔽在作用域中冻结可变变量。

可以先声明绑定，然后再初始化，但这样易导致使用未初始化的变量。

## Types 类型系统

Rust 不提供原生类型之间的隐式类型转换（coercion），可以使用 `as` 关键字显式地转换（casting）。

整型之间的转换，按位长截断，然后根据有符号或无符号计算值。

类型推断引擎，不只在初始化时看右值的类型，还根据变量之后如何使用推断类型。

```rust
let elem = 5u8;
let mut vec = Vec::new();
vec.push(elem);		// 根据插入元素的类型推断 Vec<T> 的类型
```

使用 `type` 关键字为已有的类型取别名。类型名要遵循驼峰命名法 `CamelCase`，否则会编译报错。

## Conversion 类型转换

原生类型通过 casting 实现类型转换，其他类型的转换需要通过 trait 实现，一般使用会使用 `From` 和 `Into` 两个 trait。其他情况比如涉及到 `String` 的类型转换还需要其他 trait。

### `From` 和 `Into`

`From` trait 允许类型定义如何从另一类型生成自身。

如将 `&str` 转换成 `String`，还可以为自定义类型定义转换机制。

```rust
// str 转换成 String
let my_str = "hello";
let my_string = String::from(mystr);
```

`Into` trait 定义如何转换成其他类型，也就是把 `From` 倒过来，实现了 `From` 之后就自动获得了 `Into`。通常要求指定转换到的类型，编译器大多时候无法推断。

```rust
use std::convert::From;

#[derive(Debug)]
struct Number {
    value: i32,
}

impl From<i32> for Number {
    fn from(item: i32) -> Self {
        Number { value: item }
    }
}

fn main() {
    let num = Number::from(30);
    println!("My number is {:?}", num);
    
    let int = 5;
    let num: Number = int.into();
    println!("My number is {:?}", num);
}
/*
My number is Number { value: 30 }
My number is Number { value: 5 }
*/
```

`TryFrom` 和 `TryInto` 也是类型转换的 trait，用于易出错的转换，返回值是 `Result` 类型，`Result` 是枚举类型，包括 `Ok(T)` 和 `Err(E)` 两个可能取值。

要将任何类型转换成 `String`，只需实现 `ToString` trait。但是不推荐，还是使用 `fmt::Display` trait，它会自动提供 `ToString`，还可以打印类型。

只要目标类型实现了 `FromStr` trait，就可以使用 `parse` 把字符串转换成目标类型。

## Expressions 表达式

绝大多数 Rust 程序由一系列语句构成，最普遍的语句有两种：绑定变量和表达式带分号。

代码块也是表达式，可以充当右值，代码块中最后一条表达式的值会赋给左值。如果代码块（实际执行的）最后一条表达式结尾有分号，则返回值会变成 `()`。

## Flow of Control 控制流

`if/else` 分支判断和其他语言类似，条件不需要加括号。`if/else` 是一个表达式，所有分支必须返回相同的类型。

使用 `loop` 关键字实现无限循环，支持 `break` 和 `continue`，可以使用标签直接 break/continue 外层循环。将值放在 `break` 之后即可被 `loop` 表达式返回。

```rust
'#![allow(unreachable_code)]

fn main() {
    'outer: loop {
        println!("Entered the outer loop");
        'inner: loop {
            println!("Entered the inner loop");
            //break;		// 这只是中断内部的循环       
            break 'outer;	// 这会中断外层循环
        }
        println!("This point will never be reached");
    }
    println!("Exited the outer loop");
}
/*
Entered the outer loop
Entered the inner loop
Exited the outer loop
*/
```

使用 `while` 创建条件循环，条件满足时循环。

`for ... in` 结构可以遍历迭代器，使用下面几个函数可以把集合转换成迭代器：

- `iter`：每次借用集合中的一个元素，集合本身不会改变。
- `into_iter`：每次会使用集合本身的数据，集合在循环中被 move。
- `iter_mut`：可变地借用集合元素，允许集合被就地修改。

### `match` 匹配

`match` 提供模式匹配，类似 `switch`，`match` 分支必须覆盖所有的可能性，`_` 通配符类似 `switch` 里的 default 分支。

```rust
match number {
	1 => println!("One!"),								   // 匹配单个值
	2 | 3 | 5 | 7 | 11 => println!("This is a prime"),  // 匹配多个值
	13..=19 => println!("A teen"), 				   		  // 匹配一个闭区间范围
	_ => println!("Ain't special"),						  // 处理其他情况
}
```

`match` 可以解构元组、枚举、指针和结构体。

与 C 不同的是，指针的解构（destructure）和解引用（dereference）是不一样的。解引用使用 `*`，解构使用 `&`、`ref` 和 `ref mut`。

```rust
let reference = &4;
//或者使用 ref 创建引用
let ref reference = 4;

match reference {
    &val => println!("val = {}", val),
}
// 或在匹配之前解引用
match *reference {
    val => println!("val = {}", val);,
}

let not_ref = 5;
let mut mut_not_ref = 10;

// 对于非引用变量，可以使用 ref 和 ref mut 获取引用
// 这里的 r 是引用，因为可以对它解引用（对整数不可以）
match not_ref {
    ref r => println!("r = {}, *r = {}", r, *r),
}

match mut_not_ref {
    ref mut r => {
        *r += 10;
        println!("r = {}, *r = {}", r, *r);
    },
}
```

使用 `match` 卫语句（guard）过滤分支，就是在分支中使用 `if` 条件。要注意的是，编译器不会检查卫语句是否包含了所有可能性，所以还是需要使用 `_`。

```rust
let pair = (2, -2);

match pair {
    (x, y) if x == y => ... ,
    (x, y) if x > y => ... ,
    (x, _) if x % 2 == 1 => ... ,
    _ => ... ,
}
```

在 `match` 中，如果间接地访问一个变量，不经重新绑定就无法在分支中在此使用它。`match` 提供 `@` 绑定变量到名称，也可用绑定解构 `enum`。（这里应该可以直接用卫语句）

```rust
fn age() -> u32 {
    15
}

match age() {
    n @ 1..=12 => ... ,
    n => ... ,
}
```

如果只想处理 `match` 中的一个分支，还需要些 `_`，此时使用 `if let` 语句更加简洁。`let` 用于解构，解构成功就会执行后续的语句，如果要指明失败情形，就使用 `else`。`if let` 也可以匹配枚举值，甚至是非参数化的枚举变量。

``` rust
enum Foo {
	Bar,
	Qux(u32),
}

let a = Foo::Bar;
let b = Foo::Qux(5);

// 如果使用 if Foo::Bar == a 就会报错，因为枚举的实例不具有可比性
// 而使用解构的方式就可以
if let Foo::Bar = a {
    ...
}

if let Foo:Qux(i) = b {
    ...
}
```

类似的，可以使用 `while let` 改写循环内的 `match`。

```rust
let mut optional = Some(0);
loop {
    match optional {
        Some(i) => {
            if i > 9 {
                optional = None;
            } else {
                optional = Some(i + 1);
            }
        }
        _ => break;
    }
}

// 使用 while let 改写
while let Some(i) = optional {
    if i > 9 {
        optional = None;
    }else {
        optional = Some(i + 1);
    }
}
```

## Function 函数

使用 `fn` 关键字声明函数，参数需要标志类型，使用 `->` 指定返回类型。函数最后的表达式将作为返回值，也可在函数内使用 `return` 语句提前返回值。

方法是依附于对象的函数，在 `impl` 代码块中定义。在方法中使用关键字 `self` 访问对象中的数据和其他方法。

### 闭包

闭包是一类能捕获周围作用域中变量的函数。调用闭包和调用函数相同，闭包的输入和返回类型都可以自动推导，但必须指明输入变量名。

闭包使用 `||` 代替 `()` 包裹参数列表，单个表达式可以不使用 `{}`。闭包是匿名的，可以将它们绑定到变量。

```rust
let closure_annotated = |i: i32| -> i32 { i + 1 };
let closure_inferred  = |i: i32|          i + 1  ;
```

闭包可以通过引用、可变引用和值的方式捕获变量，默认使用引用捕获。使用可变引用则使用 `let mut` 绑定。在 `|` 之前加 `move` 会强制必要取得被捕获变量的所有权（只能在闭包内使用变量，可以多次）。

如果使用闭包作为函数参数，需要指出闭包的完整类型。

使用几个 trait 指定，受限制程度递减为 `Fn`、`FnMut` 和 `FnOnce`，对应通过引用、可变引用和值方式捕获。使用 `FnOnce` 做类型说明的闭包，可以采取全部三种方式捕获，编译器根据使用情况决定捕获方式。但如果使用 `Fn` 类型说明，则只能使用引用方式捕获。

```rust
fn apply<F>(f: F) ->i32 where
	F: FnOnce(i32) -> i32 {
   	...
}

fn call<F: FnOnce(i32) -> i32>(f: F, x: i32) -> i32 {
    f(x)
}

let closure = | x | x * 2;
let i = 123;
call(closure, 123);
/*
call -> closure(123) -> 246
*/
```

使用闭包作为函数参数需要使用泛型，这是由闭包的定义方式决定的。闭包被定义时，编译器会隐式地创建一个匿名结构体，用于存储闭包捕获的变量，同时为这个未知类型实现 `Fn`、`FnMut` 和 `FnOnce` 中的一个功能。

这个新的未知类型在函数中的使用需要泛型，然而 `<T>` 并不明确，实现的 trait 约束足以确认类型。

既然闭包能作为输入参数，那么函数也可以。声明一个将闭包作为参数的函数后，所有满足该闭包的 trait 约束的函数都可以作为参数。

闭包也可以作为输出参数，而目前仅支持非泛型的闭包返回值。要使用 `impl Trait` 才能返回闭包，其中的 trait 是 `Fn`、`FnMut` 和 `FnOnce` 中的一个。此外，还需要使用 `move` 关键字指定通过值捕获，因为函数推出后引用会丢弃。

Rust 提供了高阶函数 Higher Order Function, HOF，即输入一个或多个函数，生成一个更有用的函数。（例子没看懂，之后再细看吧）。

发散函数永远不会返回，使用 `!` 标记，是一个空类型。可以转换为任意其他类型，`continue` 的值就是 `!`，`panic!` 也是 `!` 类型。

> 说是 day1 其实懒了好几天才看完
