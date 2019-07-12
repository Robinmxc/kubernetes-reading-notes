## SourceID 非80端口部署模式

SourceID非80端口部署有两种部署模式：

- 原生模式：原生模式指要使用的端口开启在SourceID服务器上，SourceID域名直接解析到服务器
- NAT模式：NAT模式指SourceID服务器仍开启80端口，通过在网关设备做NAT映射来支持80以外端口访问，SourceID域名解析到网关设备

### NAT模式

下面以8000端口为例，说明怎样配置SourceID运行在非80端口。

1. 用以下yaml脚本部署一个运行在8000端口的sso服务，并绑定服务IP为`172.30.31.5`
    ```
    apiVersion: v1
    kind: Service
    metadata:
      name: rg-sso-8000
      namespace: ruijie-sourceid
    spec:
      selector:
        service: rg-sso
      clusterIP: 172.30.31.5
      ports:
      - port: 8000
        targetPort: 80
    ```
    **注意：服务IP必须在`CLUSTER_CIDR`参数所定义的网段的最后一个C类子网中分配，且主机地址必须大于3。**
    **例如：`CLUSTER_CIDR=172.30.16.0/20`，则最后一个C类子网是`172.30.31.0/24`，分配地址`172.30.31.5`。**

1. 修改`/opt/kad/workspace/ruijie-sourceid/conf/all.yml`，设置以下参数：
    ```
    SOURCEID_SSO_URL: "http://id.example.com:8000"
    SOURCEID_FRONTEND_URL: "http://id-self.example.com:8000"
    SOURCEID_SSO_HOST_ALIAS: "172.30.31.5"
    ```
    其中`172.30.31.5`是sso组件8000端口服务所绑定的IP

1. 重新部署SourceID
    ```
    kad-play playbooks/sourceid/reconfig.yml
    ```

### 原生模式

暂不支持原生模式的非80端口部署。
