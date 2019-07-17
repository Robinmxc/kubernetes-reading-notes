## SourceID单机部署步骤

**注意：以下操作只能在部署工具kad 1.0.0以上版本中执行**

1. 参考[SourceID标准部署](docs/ruijie/sourceid/getting-started.md)中的准备环节，准备部署环境
1. 修改`/opt/kad/workspace/k8s/conf/all.yml`文件，所有服务器组设置成同一IP。如下所示：
    ```
    KUBE_MASTER_HOSTS: ["192.168.1.61"]
    KUBE_NODE_HOSTS: ["192.168.1.62"]
    ```
1. 参考[SourceID标准部署](docs/ruijie/sourceid/getting-started.md)中的设置SourceID部署参数环节，设置SourceID参数
1. 执行部署命令（在`/opt/kad`目录下执行）
   ```bash
   cd /opt/kad
   ./sourceid-setup.sh
   ```
