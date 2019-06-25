## SourceID部署步骤

本文以SourceID 1.5.1为例描述在开发、测试环境部署SourceID的步骤，生产环境部署请使用《SourceID部署操作说明.docx》。

#### 1. 准备

1. 安装基础工具wget，如果wget已经存在可以跳过这一步
    ```bash
    yum install -y wget
    ```
1. 安装Ansible
    ```bash
    yum install -y ansible
    ```
1. 安装部署工具
    ```bash
    cd /opt
    wget http://172.17.8.20:8081/repository/files/ruijie/kad/release/kad-1.0.0-1.x86_64.rpm
    rpm -ivh kad-1.0.0-1.x86_64.rpm
    ```

#### 2. 设置K8S部署参数

修改`/opt/kad/workspace/k8s/conf/all.yml`文件，根据文件提示修改以下参数：

```
# Master节点IP
KUBE_MASTER_HOSTS: ["192.168.1.61"]

# Node节点IP
KUBE_NODE_HOSTS: ["192.168.1.62", "192.168.1.63", "192.168.1.64"]

# 部署规模：small, normal, single。normal为标准规模，small主要用于开发、测试，single为单机
CLUSTER_SCALE: "small"

# POD 网段 (Cluster CIDR），不要与内网已有网段冲突，网络位数不能大于20
CLUSTER_CIDR: "172.30.16.0/20"

# 双Master部署模式时使用的虚IP
KUBE_MASTER_VIP: ""

# 文件下载服务器，开发/测试环境请修改为内部地址
KAD_FILES_REPO: "http://172.17.8.20:8081/repository/files/ruijie/"
```

**注意：**
- 开发和UAT测试环境需要额外设置以下参数（内存占用少）：
    ```
    CLUSTER_SCALE="small"
    ```
- 开发/测试环境请把文件下载服务器设置为内部地址，默认的阿里云地址下载速度慢并且会收费
    ```
    KAD_FILES_REPO: "http://172.17.8.20:8081/repository/files/ruijie/"
    ```

#### 3. 设置SourceID部署参数

修改`/opt/kad/workspace/ruijie-sourceid/conf/all.yml`文件，根据文件提示修改以下参数：

```
#部署模式：dev, prd。dev模式下会多一些和开发、测试有关的配置参数，比如sso服务器的hostAlias
SOURCEID_DEPLOY_PROFILE: "dev"

#SourceId发布版本号
SOURCEID_RELEASE_VERSION="r1.5.1"

#SSO域名
SOURCEID_SSO_DOMAIN="id.example.com"

#自助和管理端域名
SOURCEID_GATE_DOMAIN="id-self.example.com"

#二次认证网关地址
SOURCEID_GATEWAY_URL="http://gateway.example.com"

#登录成功后的跳转地址
SOURCEID_REDIRECT_URL="http://www.baidu.com"

#数据库管理员账号，只能由大/小写字母、数字、下划线组成，长度3~16字符
MONGODB_ADMIN_USER="admin"

#数据库管理员密码，只能由大/小写字母、数字、下划线组成，至少1个大写字母，1个小写字母和1个数字，长度6~16字符
MONGODB_ADMIN_PWD=""
```

**注意：**
- `SOURCEID_RELEASE_VERSION`参数是产品发布版本号，不是Docker镜像的版本号，必须根据产品发布文档进行设置

#### 4. 执行部署

按以下步骤操作：

1. 执行部署命令（在`/opt/kad`目录下执行）
    ```bash
    cd /opt/kad
    ./sourceid-setup.sh
    ```
1. 出现如下输入密码的提示信息后，输入root用户的密码
    ```
    SSH password:
    ```
1. 等待脚本运行完成。部署成功会显示如下信息
    ```
    PLAY RECAP *************************************************************
    192.168.1.61            : ok=xx   changed=xx   unreachable=0    failed=0
    192.168.1.62            : ok=xx   changed=xx   unreachable=0    failed=0
    192.168.1.63            : ok=xx   changed=xx   unreachable=0    failed=0
    192.168.1.64            : ok=xx   changed=xx   unreachable=0    failed=0
    ```
