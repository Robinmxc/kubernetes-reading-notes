## 部署单Master集群

#### 1. 准备

##### 4台主机
- 4台集群主机（1台master + 3台node）
- 操作系统要求都是CentOS 7.6.1810
- 各主机的root密码必须相同（包括部署主机）

##### 联网

各主机需要能连接互联网，至少部署过程需要能连接。

#### 2. 安装部署工具

在master上按以下步骤操作：

1. 安装基础工具wget，如果wget已经存在可以跳过这一步
    ```bash
    yum install -y wget
    ```
1. 安装Ansible
    ```bash
    yum install -y ansible
    ```
1. 下载自动化部署工具的安装包
    ```bash
    cd /opt
    wget http://http://172.17.8.20:8081/repository/files/ruijie/kad/release/kad-0.7.0.tar.gz
    ```
1. 解压
    ```bash
    tar xzvf kad-0.7.0.tar.gz
    ```

#### 3. 准备配置文件

**注意：由于配置文件格式有较大改动，0.6.0以前版本的配置文件需要按照本节的操作步骤重新准备（不影响集群运行，只是各项配置参数需要重新输入）。**

参考inventory/example目录下的例子，准备部署文件。下面以1个master节点+3个node节点为例进行说明。

假设各主机IP地址如下：
- master节点：192.168.1.61
- node节点：192.168.1.62, 192.168.1.63, 192.168.1.64

按以下步骤操作：
1. 复制一个示例配置文件作为配置基础
    ```bash
    cd /opt/kad
    cp -rpf inventory/example/m1n3 inventory/my-cluster
    ```
1. 编辑inventory/my-cluster/hosts.ini，设置各节点IP地址：
    ```
    [deploy]
    192.168.1.61 NTP_ENABLED=no

    [etcd]
    192.168.1.61 NODE_NAME=etcd1
    192.168.1.62 NODE_NAME=etcd2
    192.168.1.63 NODE_NAME=etcd3

    [kube-master]
    192.168.1.61

    [kube-node]
    192.168.1.62
    192.168.1.63
    192.168.1.64
    ```

#### 4. 部署

按以下步骤操作：

1. 执行部署命令（在/opt/kad目录下执行）
    ```bash
    ansible-playbook -i inventory/my-cluster/hosts.ini -k playbooks/cluster/k8s-setup.yml
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
