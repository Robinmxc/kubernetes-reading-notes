#!/usr/bin/env python
#coding:utf8

import json
import sys
import yaml

def to_json(in_dict):
    return json.dumps(in_dict, sort_keys=True, indent=2)

def parse_host_data(filename):
    file = open(filename)
    config = yaml.load(file)
    master_hosts = config["KUBE_MASTER_HOSTS"]
    node_hosts = config["KUBE_NODE_HOSTS"]

    result = {
        "groups": {
            "kube-master": {"hosts": master_hosts},
            "kube-node": {"hosts": node_hosts},
            "etcd": {"hosts": node_hosts},
            "mongodb": {"hosts": node_hosts},
            "deploy": {"hosts": [master_hosts[0]]},
            "rocketmq": {"hosts": [node_hosts[len(node_hosts) - 1]]},
            "all": {
                "vars": {
                }
            }
        },
        "host_vars": {
        }
    }
    group_all_vars = result["groups"]["all"]["vars"]
    host_vars = result["host_vars"]

    # 设置K8S部署模式
    deploy_mode = "single-master"
    if (len(master_hosts) == 2):
        deploy_mode = "multi-master"
    elif (len(node_hosts) == 1 and node_hosts[0] == master_hosts[0]):
        deploy_mode = "allinone"
    group_all_vars["DEPLOY_MODE"] = deploy_mode

    if (deploy_mode == "multi-master"):
        # 设置负载均衡节点
        result["groups"]["lb"] = {"hosts": master_hosts}
        # 双Master部署模式设置为虚
        group_all_vars["MASTER_IP"] = config["KUBE_MASTER_VIP"]
        # 双Master部署模式设置端口为8443
        group_all_vars["KUBE_APISERVER"] = "https://{{ MASTER_IP }}:8443"
    else:
        group_all_vars["MASTER_IP"] = master_hosts[0]
        group_all_vars["KUBE_APISERVER"] = "https://{{ MASTER_IP }}:6443"

    # 初始化Host变量
    for ip in master_hosts:
        host_vars[ip] = {}
    for ip in node_hosts:
        host_vars[ip] = {}

    # 设置负载均衡角色
    if (deploy_mode == "multi-master"):
        host_vars[master_hosts[0]]["LB_ROLE"] = "master"
        host_vars[master_hosts[1]]["LB_ROLE"] = "backup"

    # 设置ETCD节点名称
    idx = 1
    for ip in node_hosts:
        host_vars[ip]["NODE_NAME"] = "etcd" + bytes(idx)
        idx = idx + 1

    return result

def main():
    host_data = parse_host_data("/opt/kad/workspace/inventory/group_vars/all.yml")
    if len(sys.argv) == 2 and (sys.argv[1] == "--list"):
        print(to_json(host_data["groups"]))
    elif len(sys.argv) == 3 and (sys.argv[1] == "--host"):
        ip = sys.argv[2]
        print(to_json(host_data["host_vars"][ip]))
    else:
        print("Usage: %s --list or --host <hostname>" % sys.argv[0])
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
