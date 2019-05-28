## 常用命令

本文提供一些通过kad工具管理K8s集群的常用命令。

所有命令在`/opt/kad`目录下执行，并采用以下默认参数，如果不是默认参数，请自行修改：
- Inventory目录：`workspace/inventory`
- 命名空间：`ruijie-sourceid`


### K8s集群常用命令

K8s集群常用命令如下：

1. 删除集群
    ```
    ansible-playbook -i workspace/inventory/ playbooks/cluster/k8s-clean.yml -k
    ```

### SourceID常用命令

SourceID管理命令需要先执行过prepare命令（只需要执行一次）才能正常执行：
```
ansible-playbook -i workspace/inventory/ playbooks/sourceid/prepare.yml -k
```

SourceID常用命令如下：

1. 从K8s集群中删除SourceID各组件
    ```
    ansible-playbook -i workspace/inventory/ playbooks/sourceid/clean.yml -k
    ```
1. 单独部署SourceID组件
    ```
    ansible-playbook -i workspace/inventory/ playbooks/sourceid/setup.yml --tags sourceid -k
    ```
1. 从K8s集群中删除MongoDB（不会删除数据文件）
    ```
    kubectl delete -f workspace/ruijie-sourceid/yaml/mongo/
    ```
1. 单独部署MongoDB
    ```
    ansible-playbook -i workspace/inventory/ playbooks/sourceid/setup.yml --tags mongodb -k
    ```
1. 从K8s集群中删除RocketMQ（不会删除数据文件）
    ```
    kubectl delete -f workspace/ruijie-sourceid/yaml/rocketmq/
    ```
1. 单独部署RocketMQ
    ```
    ansible-playbook -i workspace/inventory/ playbooks/sourceid/setup.yml --tags rocketmq -k
    ```
1. 单独执行数据库初始化脚本
    ```
    ansible-playbook -i workspace/inventory/ playbooks/sourceid/setup.yml --tags initdata -k
    ```
1. 重新部署单个组件（以linkid为例，其他组件名称分别是：sso、gate、frontend、component）
    ```
    ansible-playbook -i workspace/inventory/ playbooks/sourceid/clean.yml --tags linkid -k
    ansible-playbook -i workspace/inventory/ playbooks/sourceid/setup.yml --tags linkid -k
    ```
1. 更新组件版本（以linkid为例）
    - 修改`workspace/ruijie-sourceid/kad.yml`文件的变量`SOURCEID_DOCKERS`中linkid的版本号
    - 按照上述“重新部署单个组件”的操作方法重新部署linkid
1. 修改组件配置文件（以linkid为例）
    - 修改`workspace/ruijie-sourceid/conf/sourceid/linkid/conf/`目录下的配置文件
    - 按照上述“重新部署单个组件”的操作方法重新部署linkid
1. 替换frontend资源文件
    - 资源文件目录复制到`workspace/ruijie-sourceid/conf/sourceid/frontend/`目录下
    - 按照上述“重新部署单个组件”的操作方法重新部署frontend
