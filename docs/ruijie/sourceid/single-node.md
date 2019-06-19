## SourceID单机部署步骤

***注意：部署工具kad 0.10.0以上版本才支持单机部署***

1. 参考[SourceID标准部署](docs/ruijie/sourceid/getting-started.md)中的准备环节，准备部署环境
1. 修改`workspace/inventory/hosts.ini`文件，所有服务器组设置成同一IP，如下所示：
    ```
    [kube_master]
    192.168.1.61

    [kube_node]
    192.168.1.61

    [deploy]
    192.168.1.61

    [etcd]
    192.168.1.61 NODE_NAME=etcd1

    [mongodb]
    192.168.1.61

    [rocketmq]
    192.168.1.61
    ```
1. 修改`workspace/inventory/group_vars/all.yml`，设置
    ```
    DEPLOY_MODE: allinone
    CLUSTER_SCALE: single
    ```
1. 参考[SourceID标准部署](docs/ruijie/sourceid/getting-started.md)中的设置SourceID部署参数环节，设置SourceID参数
1. 执行部署命令（在`/opt/kad`目录下执行）
   ```bash
   ansible-playbook -i workspace/inventory/ playbooks/sourceid/0-all.yml -k
   ```