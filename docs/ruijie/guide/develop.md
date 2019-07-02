## 开发环境的准备方法

按以下步骤准备开发环境

1. 安装Ansible
    ```bash
    yum install -y ansible
    ```
1. 安装Git
    ```bash
    yum install -y git
    ```
1. 下载代码（在/opt目录下执行）
    ```
    cd /opt
    git clone http://192.168.54.191/baseproject/kad.git
    ```
1. 下载运行部署脚本需要的二进制文件
    ```
    cd /opt/kad
    wget http://172.17.8.20:8081/repository/files/ruijie/kad/support/kad-support-files-0.7.0.tar.gz
    tar xzvf kad-support-files-0.7.0.tar.gz
    ```
1. 下载SourceID 镜像
    ```
    cd /opt/kad/down/
    wget http://172.17.8.20:8081/repository/files/ruijie/sourceid/images/sourceid-images-r1.5.1.tar.gz
    tar zxvf sourceid-images-r1.5.1.tar.gz
    ```
1. 下载SourceID安装包
    ```
    cd /opt/kad/down/
    wget http://172.17.8.20:8081/repository/files/ruijie/sourceid/kad/sourceid-kad-r1.5.1.zip
    ```
1. 准备workspace
    ```
    cp -rpf /opt/kad/example/workspace /opt/kad/workspace
    ```
