# Python 命令行参数

[Python 命令行参数 | 菜鸟教程](https://www.runoob.com/python/python-command-line-arguments.html)

python 使用 sys.argv 获取命令行参数。

```python
# test.py
import sys
print(sys.argv)
```

```shell
$ python test.py arg1 arg2 --arg3 arg3_value
['test.py', 'arg1', 'arg2', '--arg3', 'arg3_value']
```


python 提供 getopt 模块处理命令行参数，可以获取命令行选项和参数。

```python
getopt.getopt(args, options[, long_options])
```

- args 是要解析的命令行参数列表
- options 字符串定义，option 后加 `:` 表示该选项需要附加参数
- long_options 列表定义，long_option 后加 `=` 表示该长选项需要附加参数
- 返回值
  - (option, value) 元组列表
  - 无参数选项列表

没有找到参数列表，或选项需要的参数为空时触发 `getopt.GetoptError` 异常。

```python

```