# Git Hooks

[Git Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)

[Git Hooks zh-CN](https://git-scm.com/book/zh/v2/%E8%87%AA%E5%AE%9A%E4%B9%89-Git-Git-%E9%92%A9%E5%AD%90)

Git 支持在特定的动作发生时触发自定义脚本，也就是 hook，分为 client 和 server 端。

具体的类型见上面的链接，这里只记录我的一个需求：

使用 mkdocs 部署文档需要修改 *mkdocs.yml*，如果我要添加文件，就要在 yml 中添加对应的项。为此，我写了一个简单的脚本扫描 *docs* 目录下的所有 *.md* 文件，以 yml 格式写到 *mkdocs.yml* 中。这样，只要不涉及具体配置的修改，执行这个脚本就可以了。

但问题来了，经常在 commit&push 之前忘记执行它，导致还得追加一个修改 yml 的 commit，很麻烦。所以这里就使用 git hook 中的 pre-commit hook，它在键入 commit messge 之前运行，如果该 hook 以非零值退出，git 将放弃此次提交。

具体来说就是在本地库的 *.git/hook* 目录下添加 *pre-commit* 文件，要设置为可执行。

以下就是我使用的 *pre-commit* hook：

```shell
#!/usr/bin/zsh

cd scripts
source ~/.zshrc
ca37
python generate_yml.py
git add diff_result.html mkdocs_old.yml ../mkdocs.yml
```

这里做的就是运行脚本生成一个新的 yml 文件，然后将其 git add，这样 hook 之后执行的 commit 就会把 yml 也给提交。

要注意的是，当在 *Notes* 目录下进行 git commit 时，这个 hook 的路径也是 *Notes*。

问题又来了，以上的 pre-commit hook 适用于 Linux 或 wsl 环境。而我习惯使用 vscode 进行 git 操作（git add 的时候比较方便），但是 vscode 是用的 Windows Git 的 bash 执行 pre-commit hook，当然也就没有 zsh。

不过好在是使用 git bash 执行，而不是 Windows powershell 或者 cmd，经过各种尝试，最终的 hook 脚本如下：

```shell
#!/usr/bin/bash
if [ "`pwd`" == "/mnt/c/path/to/my/notes" ]; then
    echo "Hook in Linux Git"
    zsh -c "source ~/.zshrc; conda activate py37; cd scripts ; python generate_yml.py; git add diff_result.html mkdocs_old.yml ../mkdocs.yml"
else
    echo "Hook in Windows Git"
    wsl -u qhx zsh -c "source ~/.zshrc; conda activate py37; cd scripts ; python generate_yml.py; git add diff_result.html mkdocs_old.yml ../mkdocs.yml"
fi;
```

其实原理也很简单，就利用 wsl 和 windows git bash 路径的不同，前者的 C 盘挂载在 /mnt 下，所以直接比较就可以判断当前是在哪个环境执行。