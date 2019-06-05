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

SourceID常用命令需要先执行过prepare命令（只需要执行一次）才能正常执行：
```
ansible-playbook -i workspace/inventory/ playbooks/sourceid/prepare.yml -k
```

SourceID常用命令如下：

1. 从K8s集群中删除SourceID各组件
    ```
    ansible-playbook -i workspace/inventory/ playbooks/sourceid/clean.yml -k
    ```
1. 单独部署全部SourceID组件
    ```
    ansible-playbook -i workspace/inventory/ playbooks/sourceid/setup.yml --tags sourceid -k
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
    - 资源文件目录（如：`zstu`）复制到`workspace/ruijie-sourceid/conf/sourceid/frontend/`目录下
    - 修改`workspace/inventory/group_vars/all.yml`文件中的`SOURCEID_FRONTEND_RES`变量为`zstu`
    - 按照上述“重新部署单个组件”的操作方法重新部署frontend
