## 配置SourceID的HTTPS访问模式

本文以说明如何配置SourceID的HTTPS访问模式。

系统支持两种HTTPS部署模式：

- 普通模式。普通模式是指HTTPS证书部署在Ingress服务上，由Ingress负责HTTPS的加/解密
- Offload模式。Offload模式是指由第三方服务负责HTTPS加/解密

### 普通模式部署步骤

1. 准备证书文件

目前只支持pem格式的证书。

把证书文件放到部署主机的`/etc/kubernetes/ssl`目录下，证书文件按以下规则命名：

- 证书文件：example.com.pem
- 私钥文件：example.com-key.pem

其中example.com是域名。

2. 修改配置文件

- 修改`/opt/kad/workspace/k8s/conf/all.yml`文件，设置以下参数：

    ```
    traefik_mode: "https"
    traefik_ssl_names: ["example.com"]
    ```

    可以配置多个域名，例如：

    ```
    traefik_ssl_names: ["example.com", "abc.com", "def.com"]
    ```

    各个域名的证书都要按照前面的要求放到`/etc/kubernetes/ssl`目录下。

- 修改`/opt/kad/workspace/ruijie-sourceid/conf/all.yml`文件，设置以下参数：

    ```
    SOURCEID_HTTPS_MODE: "normal"
    ```

3. 部署

执行以下命令完成部署：

```
cd /opt/kad
kubectl delete daemonset -n kube-system traefik-ingress
kad-play playbooks/cluster/ingress.yml
kad-play playbooks/sourceid/reconfig.yml
```

### Offload模式部署步骤

操作步骤如下 ：
1. 修改`/opt/kad/workspace/k8s/conf/all.yml`文件，设置以下参数：
    ```
    traefik_mode: "http"
    ```
1. 修改`/opt/kad/workspace/ruijie-sourceid/conf/all.yml`文件，设置以下参数：
    ```
    SOURCEID_HTTPS_MODE: "offload"
    ```
1. 执行以下命令完成部署：
    ```
    kubectl delete daemonset -n kube-system traefik-ingress
    kad-play playbooks/cluster/ingress.yml
    kad-play playbooks/sourceid/reconfig.yml
    ```

### 还原为HTTP模式

操作步骤如下：
1. 修改`/opt/kad/workspace/k8s/conf/all.yml`文件，设置以下参数：
    ```
    traefik_mode: "http"
    ```
1. 修改`/opt/kad/workspace/ruijie-sourceid/conf/all.yml`文件，设置以下参数：
    ```
    SOURCEID_HTTPS_MODE: "none"
    ```
1. 执行以下命令完成部署：
    ```
    kubectl delete daemonset -n kube-system traefik-ingress
    kad-play playbooks/cluster/ingress.yml
    kad-play playbooks/sourceid/reconfig.yml
    ```
