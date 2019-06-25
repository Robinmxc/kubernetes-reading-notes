## 常用命令

本文提供一些通过kad工具管理K8s集群的常用命令。

### K8s集群常用命令

K8s集群常用命令如下：

1. 删除集群
    ```
    ansible-playbook -i inventory/ playbooks/cluster/k8s-clean.yml -k
    ```

### SourceID常用命令

SourceID常用命令需要先执行过prepare命令（只需要执行一次）才能正常执行：
```
ansible-playbook -i inventory/ playbooks/sourceid/prepare.yml -k
```

SourceID常用命令如下：

1. 从K8s集群中删除SourceID全部组件（不包括mongodb和mq）
    ```
    ansible-playbook -i inventory/ playbooks/sourceid/clean.yml -k
    ```
1. 单独部署SourceID
    ```
    ansible-playbook -i inventory/ playbooks/sourceid/setup.yml -k
    ```
1. 重新部署单个组件（以linkid为例，其他组件名称分别是：sso、gate、frontend、component）
    ```
    ansible-playbook -i inventory/ playbooks/sourceid/clean.yml --tags linkid -k
    ansible-playbook -i inventory/ playbooks/sourceid/setup.yml --tags linkid -k
    ```
1. 更新组件版本（以linkid为例）
    - 从文件`down/sourceid-kad-r1.5.1/kad.yml`中复制变量`SOURCEID_DOCKERS`到`workspace/ruijie-sourceid/conf/all.yml`中
    - 修改`workspace/ruijie-sourceid/conf/all.yml`文件中变量`SOURCEID_DOCKERS`中linkid的版本号
    - 依次执行以下命令：
        ```
        ansible-playbook -i inventory/ playbooks/sourceid/clean.yml --tags linkid -k
        ansible-playbook -i inventory/ playbooks/sourceid/prepare.yml -k
        ansible-playbook -i inventory/ playbooks/sourceid/setup.yml --tags linkid -k
        ```
1. 修改组件配置文件（以linkid为例）
    - 修改`workspace/ruijie-sourceid/conf/sourceid/linkid/conf/`目录下的配置文件
    - 按照上述“重新部署单个组件”的操作方法重新部署linkid
1. 替换frontend资源文件
    - 资源文件目录（如：`zstu`）复制到`workspace/ruijie-sourceid/conf/sourceid/frontend/`目录下
    - 修改`workspace/ruijie-sourceid/conf/all.yml`文件中的`SOURCEID_FRONTEND_RES`变量为`zstu`
    - 按照上述“重新部署单个组件”的操作方法重新部署frontend
