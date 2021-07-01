# Shell 脚本

> 没系统学过 shell 脚本，用到的时候记录一下

大多数 UNIX 命令从终端接受输入并将产生的输出发送回终端，默认的输入输出是标准输入输出，文件描述符 0 通常是标准输入 stdin，1 是标准输出 stdout，2 是标准错误输出 stderr。重定向命令列表如下：

| Command             | Description                                        |
| ------------------- | -------------------------------------------------- |
| command > file      | 将标准输出重定向到 file。                          |
| command < file      | 将标准输入重定向到 file。                          |
| command >> file     | 将输出以追加的方式重定向到 file。                  |
| n > file            | 将文件描述符为 n 的文件重定向到 file。             |
| n >> file           | 将文件描述符为 n 的文件以追加的方式重定向到 file。 |
| n>& m               | 将输出文件 m 和 n 合并。                           |
| n<&m                | 将输入文件 m 和 n 合并。                           |
| << tag              | 将开始标记 tag 和结束标记 tag 之间的内容作为输入。 |
| commmand 2> file    | 将标准错误输出重定向到 file。                      |
| command > file 2>&1 | 将 stdout 和 stderr 合并后重定向到 file。          |

##### Here Document

```shell
command << delimiter
	document
delimiter
```

其中 delimiter（定界符）具体内容可以自定义，但是结尾的 delimiter 一定要顶格写，前后不能有任何字符。

```shell
$ wc -l << TEST
test here document
and use wc -l
to count line
TEST
3
```

##### /dev/null

任何写入 /dev/null 的内容都会被丢弃，如果希望屏蔽 stdout 和 stderr，可以写为

```shell
$ commmand > /dev/null 2>&1
```

这里的 `2>` 一体的时候才表示 stderr。
