## 处理异常情况

1. 如果没有部署成功，执行以下命令清除集群环境，然后重新执行部署过程
    ```
    ansible-playbook -i workspace/inventory playbooks/cluster/k8s-clean.yml -k
    ```

1. 在部署成功后的集群节点上执行kubectl相关命令时，如果报“未找到命令”这个错误，重新登录即可解决。因为部署过程中对PATH环境变量的修改不会对已经登录的用户生效。
