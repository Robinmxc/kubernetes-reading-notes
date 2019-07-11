## 常用命令

本文提供一些通过kad工具管理K8s集群的常用命令。

### K8s集群常用命令

K8s集群常用命令如下：

1. 删除集群
    ```
    kad-play playbooks/cluster/k8s-clean.yml
    ```

### SourceID常用命令

SourceID常用命令如下：

1. 删除SourceID全部组件（不包括mongodb和mq）
    ```
    kad-play playbooks/sourceid/clean.yml
    ```

1. 重新部署SourceID
    ```
    kad-play playbooks/sourceid/reconfig.yml
    ```

1. 重新部署单个组件（以linkid为例，其他组件名称分别是：sso、gate、frontend、component、license）
    ```
    kad-play playbooks/sourceid/reconfig.yml --tags linkid
    ```

1. 更新组件配置文件（以linkid为例）
    - 修改`workspace/ruijie-sourceid/conf/sourceid/linkid/conf/`目录下的配置文件
    - 执行命令：
      ```
      kad-play playbooks/sourceid/reconfig.yml --tags linkid
      ```

1. 替换frontend资源文件
    - 资源文件目录（如：`zstu`）复制到`workspace/ruijie-sourceid/conf/sourceid/frontend/`目录下
    - 修改`workspace/ruijie-sourceid/conf/all.yml`文件中的`SOURCEID_FRONTEND_RES`变量为`zstu`
    - 执行命令：
      ```
      kad-play playbooks/sourceid/reconfig.yml --tags frontend
      ```

1. 更新组件版本：见[内部测试环境配置和使用方法](debug-env.md)
