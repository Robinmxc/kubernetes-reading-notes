# K8S自动化部署工具

基于[Kubeasz](https://github.com/gjmzj/kubeasz)开发。

## 使用方法

1. 准备一台CentOS主机作为部署主机，CentOS版本：7.6.1810
1. 在部署主机上安装Ansible
    ```bash
    yum install -y ansible
    ```
1. 在部署主机上下载自动化部署工具的安装包
    ```bash
    cd /opt
    wget http://192.168.54.24:8081/repository/maven-releases/com/ruijie/kad/0.1.0/kad-0.1.0.tar.gz
    ```
1. 解压自动化部署工具
    ```bash
    tar xzvf kad-0.1.0.tar.gz
    ```
1. 参考inventory目录下的例子，准备部署文件。下面以1个master节点+3个node节点为例：
    1. 部署环境如下
        - 部署主机：192.128.1.12
        - master节点：192.168.1.61
        - node节点：192.168.1.62, 192.168.1.63, 192.168.1.64
        - 各主机的root密码必须相同，包括部署主机
    1. 复制示例文件
        ```bash
        cd /opt/kad
        cp inventory/example/m1n3.ini inventory/my-cluster
        ```
    1. 编辑inventory/my-cluster，设置各节点IP地址为如下内容：
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
1. 执行部署命令（在/opt/kad目录下执行）
    ```bash
    ansible-playbook -i inventory/my-cluster -k playbooks/cluster/k8s-setup.yml
    ```
1. 出现如下输入密码的提示信息后，输入root用户的密码
    ```
    SSH password:
    ```
