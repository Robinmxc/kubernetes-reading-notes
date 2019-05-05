## SourceID部署步骤

本文描述在K8s集群中部署SourceID的步骤，部署工具需要kad-0.6.0以上版本。

部署SourceID需要在K8s集群的Master节点上进行操作，本文以[单Master集群](../guide/getting-started.md)环境为例。

#### 1. 准备

**注意：由于集群配置文件格式有较大改动，0.6.0以前版本的配置文件需要按照[单Master集群](../guide/getting-started.md)中第3节的操作步骤重新准备（不影响集群运行，只是各项配置参数需要重新输入）。**

执行以下命令准备SourceID部署环境：

```bash
cd /opt/kad
ansible-playbook -i inventory/my-cluster/hosts.ini playbooks/sourceid/prepare.yml -k
```

#### 2. 设置MongoDB和RocketMQ部署参数

修改`inventory/my-cluster/hosts.ini`文件，设置部署MongoDB和RocketMQ的主机（参考`inventory/example/m1n3/hosts.ini`）：

```
[mongodb]
192.168.1.62
192.168.1.63
192.168.1.64

[rocketmq]
192.168.1.63
```

#### 3. 设置SourceID部署参数

修改`inventory/my-cluster/hosts.ini`文件，根据文件提示修改以下参数：

```
#SourceId发布版本号
SOURCEID_RELEASE_VERSION="dlmu.r1.3"

#SSO域名
SOURCEID_SSO_DOMAIN="id.example.com"

#自助和管理端域名
SOURCEID_GATE_DOMAIN="id-self.example.com"

#二次认证网关地址
SOURCEID_GATEWAY_URL="http://gateway.example.com"

#登录成功后的跳转地址
SOURCEID_REDIRECT_URL="http://www.baidu.com"

#cas数据库密码
SOURCEID_CAS_DB_PWD=""

#gate数据库密码
SOURCEID_GATE_DB_PWD=""

#linkid数据库密码
SOURCEID_LINKID_DB_PWD=""

#component数据库密码
COMPONENT_DB_PWD=""
```

注意：
- `SOURCEID_RELEASE_VERSION`参数是产品发布版本号，不是Docker镜像的版本号，必须根据产品发布文档进行设置
- 数据库密码长度必须介于6到16字符之间，必须包含大、小写字母和数字
- 开发和UAT测试环境需要额外设置以下参数（内存占用少，开启测试开关）：
    ```
    CLUSTER_SCALE="small"
    SOURCEID_DEPLOY_PROFILE="dev"
    ```
- 性能测试环境需要额外设置以下参数（标准部署，开启测试开关）：
    ```
    CLUSTER_SCALE="normal"
    SOURCEID_DEPLOY_PROFILE="dev"
    ```

#### 4. 修改SouceID配置文件（可选）

SourceID配置文件在`workspace/ruijie-sourceid/conf`目录下，根据需要进行修改（如果采用默认部署，不需要修改）。

#### 5. 执行部署

按以下步骤操作：

1. 执行部署命令（在`/opt/kad`目录下执行）
    ```bash
    ansible-playbook -i inventory/my-cluster/hosts.ini playbooks/sourceid/setup.yml -k
    ```
1. 出现如下输入密码的提示信息后，输入root用户的密码
    ```
    SSH password:
    ```
1. 等待脚本运行完成。部署成功会显示如下信息
    ```
    PLAY RECAP *************************************************************
    192.168.1.62            : ok=xx   changed=xx   unreachable=0    failed=0
    192.168.1.63            : ok=xx   changed=xx   unreachable=0    failed=0
    192.168.1.64            : ok=xx   changed=xx   unreachable=0    failed=0
    ```
