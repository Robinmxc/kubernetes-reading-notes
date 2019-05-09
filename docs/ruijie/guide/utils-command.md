## 常用命令

本文提供一些通过kad工具管理K8s集群的常用命令。

所有命令在`/opt/kad`目录下执行，并采用以下默认参数，如果不是默认参数，请自行修改：
- Inventory目录：`inventory/my-cluster`
- 命名空间：`ruijie-sourceid`


### K8s集群常用命令

1. 删除集群
    ```
    ansible-playbook -i inventory/my-cluster/hosts.ini playbooks/cluster/k8s-clean.yml -k
    ```

### SourceID常用命令

SourceID管理命令需要先执行过prepare命令（只需要执行一次）才能正常执行：
```
ansible-playbook -i inventory/my-cluster/hosts.ini playbooks/sourceid/prepare.yml -k
```

1. 从K8s集群中删除SourceID各组件
    ```
    ansible-playbook -i inventory/my-cluster/hosts.ini playbooks/sourceid/clean.yml -k
    ```
1. 单独部署SourceID组件
    ```
    ansible-playbook -i inventory/my-cluster/hosts.ini playbooks/sourceid/setup.yml --tags sourceid -k
    ```
1. 从K8s集群中删除MongoDB（不会删除数据文件）
    ```
    kubectl delete -f workspace/ruijie-sourceid/yaml/mongo/
    ```
1. 单独部署MongoDB
    ```
    ansible-playbook -i inventory/my-cluster/hosts.ini playbooks/sourceid/setup.yml --tags mongodb -k
    ```
1. 从K8s集群中删除RocketMQ（不会删除数据文件）
    ```
    kubectl delete -f workspace/ruijie-sourceid/yaml/rocketmq/
    ```
1. 单独部署RocketMQ
    ```
    ansible-playbook -i inventory/my-cluster/hosts.ini playbooks/sourceid/setup.yml --tags rocketmq -k
    ```
1. 单独执行数据库初始化脚本
    ```
    ansible-playbook -i inventory/my-cluster/hosts.ini playbooks/sourceid/setup.yml --tags initdata -k
    ```
