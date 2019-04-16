## 设置时间同步服务器

集群采用chrony实现时间同步，同步方案为：
- 第1个Master节点和外部时间服务器保持同步
- 其它节点和第1个Master节点保持同步

默认外部时间服务器是`ntp1.aliyun.com`。如需要修改（例如改为`0.centos.pool.ntp.org`），在配置文件末尾添加以下内容即可：
```
ntp_server="0.centos.pool.ntp.org"
```
