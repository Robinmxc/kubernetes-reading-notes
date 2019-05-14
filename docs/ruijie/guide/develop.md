## 开发环境的准备方法

按以下步骤准备开发环境

1. 安装Ansible
    ```bash
    yum install -y ansible
    ```
1. 下载代码（在/opt目录下执行）
    ```
    cd /opt
    git clone http://192.168.54.191/baseproject/kad.git
    ```
1. 下载运行部署脚本需要的二进制文件
    ```
    wget http://192.168.54.24:8081/repository/files/ruijie/kad/support/kad-support-files-0.7.0.tar.gz
    cd kad
    tar xzvf ../kad-support-files-0.7.0.tar.gz
    ```
