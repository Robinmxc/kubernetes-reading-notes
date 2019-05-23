## HTTPS服务的配置方法

本文以[基础配置](getting-started.md)的示例环境为基础，说明如何配置HTTPS服务。

配置过程以需要通过HTTPS访问的域名是`com.ruijie`为例，并且`com.ruijie`已经配置了HTTP的Ingress（即`http://com.ruijie/`已经可以正常访问）。

#### 准备证书文件

把证书文件放到部署主机的`/etc/kubernetes/ssl`目录下，证书文件按以下规则命名：
- 证书文件：com.ruijie.pem
- 私钥文件：com.ruijie-key.pem

#### 修改配置文件

在配置文件末尾添加以下内容：
```
traefik_ssl_names=["ruijie.com"]
```

可以配置多个域名，例如：
```
traefik_ssl_names=["ruijie.com", "abc.com", "def.com"]
```
注意：各个域名的证书都要按照前面的要求放到`/etc/kubernetes/ssl`目录下。

#### 部署到K8S

执行以下命令完成部署：
```
cd /opt/kad
kubectl delete daemonset -n kube-system traefik-ingress
ansible-playbook -i workspace/inventory/ playbooks/cluster/traefik-https.yml -k
```

#### 验证

在hosts中设置：
```
192.168.1.62  com.ruijie
```
其中`192.168.1.62`是任意一个node节点的IP。

用浏览器访问：`https://com.ruijie/`。

