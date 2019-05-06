## 部署双Master高可用集群

双Master节点高可用方案是用HAProxy+Keepalived实现的，配置过程和[单Master节点配置过程](getting-started.md)是一样的，只是在配置文件有一些差别。

#### 准备

1. 准备5台主机：
- 2台master + 3台node
- 操作系统要求都是CentOS 7.6.1810
- 各主机的root密码必须相同（包括部署主机）
2. 准备一个高可用集群的虚拟IP地址，在高可用方案下，访问API Server是能过这个虚地址

#### 准备配置文件

**注意：由于配置文件格式有较大改动，0.6.0以前版本的配置文件需要按照本节的操作步骤重新准备（不影响集群运行，只是各项配置参数需要重新输入）。**

假设集群部署规划如下：
- master节点：192.168.1.61,192.168.1.62
- node节点：192.168.1.63, 192.168.1.64, 192.168.1.65
- 虚地址：192.168.1.60

按以下步骤进行操作：
1. 复制示例配置文件作为配置基础
    ```bash
    cd /opt/kad
    cp -rpf inventory/example/m2n3 inventory/cluster-ha
    ```
1. 编辑inventory/cluster-ha/m2n3.ini，设置各节点IP地址：
    ```
    [deploy]
    192.168.1.61 NTP_ENABLED=no

    [etcd]
    192.168.1.61 NODE_NAME=etcd1
    192.168.1.62 NODE_NAME=etcd2
    192.168.1.63 NODE_NAME=etcd3

    [kube-master]
    192.168.1.61
    192.168.1.62

    [kube-node]
    192.168.1.63
    192.168.1.64
    192.168.1.65

    [lb]
    192.168.1.61 LB_ROLE=master
    192.168.1.62 LB_ROLE=backup

    [all:vars]
    DEPLOY_MODE=multi-master
    MASTER_IP="192.168.1.60"
    ```

#### 4. 部署

按以下步骤操作：

1. 执行部署命令（在/opt/kad目录下执行）
    ```bash
    ansible-playbook -i inventory/cluster-ha/hosts.ini playbooks/cluster/k8s-setup.yml -k
    ```
1. 出现如下输入密码的提示信息后，输入root用户的密码
    ```
    SSH password:
    ```
