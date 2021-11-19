# Day2

> 实际是 day 4 还是 5 了都

## Mod 模块

模块是项的集合，项可以是：函数、结构体、trait、`impl` 块，甚至其他模块。

默认情况下， 模块中的项是私有的，加上 `pub` 修饰符使其可从模块外访问，`pub(crate)` 表示可以在当前 crate 的任何地方访问。

结构体字段默认也是私有的，在定义结构体的模块之外访问其字段需要加上 `pub` 修饰字段和结构体。

使用 `use as` 可以将一个完整路径绑定到新名字，方便访问。

在路径中使用 `super` 父级和 `self` 自身消除歧义并缩短硬编码。

模块可以分配到文件目录的层次结构中，使用 `mod my;` 声明会查找 *my.rs* 或 *my/mod.rs* 文件，然后将文件内容放到此作用域名为 `my` 的模块中。

## Crates 

crate 是 Rust 的编译单元，当文件含有 `mod` 声明时，模块文件内容会在编译前插入到 crate 文件的相应声明处，模块不会被单独编译。crate 可以编译成二进制可执行文件或库文件，可以使用 `--crate-type` 指定。

库没有入口函数，编译后的文件默认会加上 *lib* 前缀，可以使用 `--crate-name` 指定。

使用库时，使用 `rustc` 的 `--extern=<path/to/rlib>` 选项，所有项都会导入到与库同名的模块下，操作与其他模块相同。

## Cargo

cargo 是官方的包管理工具，包括依赖管理与 [crates.io](crates.io) 集成，方便地单元测试和基准测试。

```shell
$ cargo new foo  # cargo new --lib foo
$ tree foo
foo
├── Cargo.toml
└── src
    └── main.rs

1 directory, 2 files
```

*main.rs* 是新项目的入口源文件，*Cargo.toml* 是项目的 cargo 配置文件，包括项目名称（二进制文件名称）、版本号、作者、依赖等。

```toml
[package]
name = "foo"
version = "0.1.0"
authors = ["mark"]

[dependencies]
clap = "2.27.1" # 来自 crates.io
rand = { git = "https://github.com/rust-lang-nursery/rand" } # 来自网上仓库
bar = { path = "../bar" } # 来自本地文件系统的路径
```

cargo 支持来自 crates.io、网络和本地的依赖。

在项目目录的任何位置都可以执行 `cargo build` 构建项目， 此时会处理所有依赖，在需要时下载 crate，并构建所有内容。

一个项目可以有多个二进制文件，将文件放在 *src/bin* 目录下，编译运行时使用参数 `--bin` 指定。

将单元测试放在需要测试的模块中，并将集成测试放在 *tests/* 目录中，每个文件都是单独的集成测试。使用 `cargo test` 运行所有测试或指定测试。

在正常编译之前可能需要先决条件，可以在 *Cargo.toml* 中指定构建脚本。

```toml
[package]
...
build = "build.rs"
```

构建脚本只是另一个 rs 文件，它将在编译包内的其他内容之前优先编译调用，实现满足 crate 的先决条件。
