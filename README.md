# K8S自动化部署工具

基于[Kubeasz](https://github.com/gjmzj/kubeasz)开发。

## 使用方法

#### 1. 准备主机

按以下要求准备5台主机：

- 1台主机作为部署主机，4台集群主机（1台master + 3台node）
- 操作系统要求都是CentOS 7.6.1810
- 各主机的root密码必须相同（包括部署主机）

#### 2. 安装部署工具

在部署主机上按以下步骤操作：

1. 安装Ansible
    ```bash
    yum install -y ansible
    ```
1. 下载自动化部署工具的安装包
    ```bash
    cd /opt
    wget http://192.168.54.24:8081/repository/files/ruijie/kad/release/kad-0.1.1.tar.gz
    ```
1. 解压
    ```bash
    tar xzvf kad-0.1.1.tar.gz
    ```

#### 3. 准备配置文件

参考inventory目录下的例子，准备部署文件。下面以1个master节点+3个node节点为例进行说明。

假设各主机IP地址如下：
- 部署主机：192.128.1.12
- master节点：192.168.1.61
- node节点：192.168.1.62, 192.168.1.63, 192.168.1.64

按以下步骤操作：
1. 复制一个示例配置文件作为配置基础
    ```bash
    cd /opt/kad
    cp inventory/example/m1n3.ini inventory/my-cluster
    ```
1. 编辑inventory/my-cluster，设置各节点IP地址：
    ```
    [deploy]
    192.168.1.12 NTP_ENABLED=no

    [master]
    192.168.1.61

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
    ansible-playbook -i inventory/my-cluster -k playbooks/cluster/k8s-setup.yml
    ```
1. 出现如下输入密码的提示信息后，输入root用户的密码
    ```
    SSH password:
    ```
1. 等待脚本运行完成。部署成功会显示如下信息
    ```
    PLAY RECAP *************************************************************
    192.168.1.12            : ok=xx   changed=xx   unreachable=0    failed=0
    192.168.1.61            : ok=xx   changed=xx   unreachable=0    failed=0
    192.168.1.62            : ok=xx   changed=xx   unreachable=0    failed=0
    192.168.1.63            : ok=xx   changed=xx   unreachable=0    failed=0
    192.168.1.64            : ok=xx   changed=xx   unreachable=0    failed=0
    ```

## 处理异常情况

1. 如果没有部署成功，执行以下命令清除集群环境，然后重新执行部署过程
    ```
    ansible-playbook -i inventory/my-cluster -k playbooks/cluster/k8s-clean.yml
    ```
