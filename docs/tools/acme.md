# acme.sh

[使用 acme.sh 生成域名证书](https://github.com/acmesh-official/acme.sh/wiki/%E8%AF%B4%E6%98%8E)

以 nginx 为例，为 caijiqhx.top 正常主域名和泛域名证书。

这里选择手动 dns 方式，手动在域名添加一条 txt 解析记录，验证域名所有权。[dnsapi 用法](https://github.com/acmesh-official/acme.sh/wiki/dnsapi)

在阿里云控制台 -> 访问控制 -> 身份管理 -> 用户 创建一个用户，并创建对应的 AccessKey ID，**保存 Key 和 Secret**。

首先设置 acme 默认 CA 为 LetsEncrypt，然后经 Key 和 Secret 设置为环境变量，开始生成证书。

```shell
$ acme.sh --set-default-ca --server letsencrypt
$ export Ali_Key=<your-key>
$ export Ali_Secret=<your-secret>
$ acme.sh --issue --dns dns_ali -d caijiqhx.top -d "*.caijiqhx.top"
$ acme.sh --issue --dns dns_ali -d caijiqhx.top -d "*.caijiqhx.top" --keylength ec-256
```

然后通过安装证书，即将其复制到指定的目录：

```shell
$ acme.sh --install-cert -d caijiqhx.top \
3375 --key-file /path/to/key.pem \
3376 --fullchain-file /path/to/cert.pem \
3377 --reloadcmd "systemctl force-reload nginx"
```

这里用的是 force-reload，reload 不会重载证书。