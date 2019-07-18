## 内部测试环境配置和使用方法

内部测试时需要能更新组件版本号，并从镜像服务器下载docker镜像，本文介绍配置和使用方法。

### 配置测试环境

#### 1. 设置`CLUSTER_SCALE`参数，绕过硬件检测

部署工具默认会按照标准部署要求检测硬件资源，内部测试环境一般不能满足标准部署要求，把`CLUSTER_SCALE`参数为`small`可以避开检测。

修改`/opt/kad/workspace/k8s/conf/all.yml`，去掉`CLUSTER_SCALE`参数前面的注释符号，并把参数值修改为`small`：
```
CLUSTER_SCALE: "small"
```

#### 2. 配置镜像服务器

部署工具默认是下载具体产品的正式发布文件进行部署，在开发测试环境需要从Docker镜像服务器部署开发中的版本，配置镜像服务器参数之后才能实现这个目的。

修改`/opt/kad/workspace/k8s/conf/all.yml`，把以下配置参数添加到文件末尾：
```
PRIVATE_REGISTRY_ENABLED: "yes"
PRIVATE_INSECURE_REGISTRY: "id.ruijie.com.cn:25082"
PRIVATE_REGISTRY_USER: ""
PRIVATE_REGISTRY_PWD: ""
```
其中`PRIVATE_REGISTRY_USER`和`PRIVATE_REGISTRY_PWD`分别设置为镜像服务器登录账号和密码。

#### 3. 设置测试版本号

修改`/opt/kad/workspace/ruijie-sourceid/conf/all.yml`，修改`KAD_APP_VERSION`参数，随意设置一个测试版本号，例如：
```
KAD_APP_VERSION: "r1.6.0-test"
```

#### 4. 准备SourceID部署文件

根据上一步设置的版本号，准备SourceID部署文件目录。执行以下命令
```
cd /opt/kad/down/
unzip sourceid-kad-r1.5.1.zip -d sourceid-kad-r1.6.0-test
```
其中`sourceid-kad-r1.5.1.zip`是基础部署文件的压缩包，根据实际情况输入

### 使用

更新组件版本（以linkid为例）
- 修改`/opt/kad/down/sourceid-kad-r1.6.0-test/kad.yml`文件中变量`SOURCEID_DOCKERS`中linkid的版本号
- 依次执行以下命令（在`/opt/kad目录下执行`）：
    ```
    cd /op/kad
    kad-play playbooks/sourceid/reconfig.yml --tags linkid
    ```
