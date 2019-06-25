#!/usr/bin/env python
#coding:utf8

import json
import sys
import yaml
import os
from ipaddress import IPv4Network

def to_json(in_dict):
    return json.dumps(in_dict, sort_keys=True, indent=2)

def read_yml(file_path):
    file = open(file_path)
    config = yaml.load(file)
    file.close()
    return config

def parse_module_config(dir):
    result = {}
    file_list = os.listdir(dir)
    for x in file_list:
        full_path = dir + "/" + x
        full_path = full_path.replace("//", "/")
        if (os.path.isdir(full_path)):
            conf_file = full_path + "/conf/all.yml"
            if (os.path.exists(conf_file)):
                result[x] = read_yml(conf_file)
    return result

def parse_host_data(dir):
    group_all_vars = {}
    host_vars = {}

    kad_meta_info = read_yml("/opt/kad/meta-info.yml")
    for k in kad_meta_info:
        group_all_vars[k] = kad_meta_info[k]

    module_configs = parse_module_config(dir)
    group_all_vars["module_configs"] = module_configs

    # k8s config
    k8s_config = module_configs["k8s"]
    for k in k8s_config:
        group_all_vars[k] = k8s_config[k]

    # app config
    env = os.environ
    if ("KAD_APP_NAMESPACE" in env):
        app_namespace = os.environ["KAD_APP_NAMESPACE"]
    else:
        app_namespace = "ruijie-sourceid"
    group_all_vars["APP_NAMESPACE"] = app_namespace
    if app_namespace in module_configs:
        app_config = module_configs[app_namespace]
        for k in app_config:
            group_all_vars[k] = app_config[k]

    # sourceid-kad package config
    filename = "/opt/kad/down/sourceid-kad-" + group_all_vars["SOURCEID_KAD_VERSION"] + "/kad.yml"
    if os.path.exists(filename):
        sourceid_kad_conf = read_yml(filename)
        for k in sourceid_kad_conf:
            if (k not in group_all_vars):
                group_all_vars[k] = sourceid_kad_conf[k]

    master_hosts = k8s_config["KUBE_MASTER_HOSTS"]
    node_hosts = k8s_config["KUBE_NODE_HOSTS"]
    result = {
        "groups": {
            "kube_master": {"hosts": master_hosts},
            "kube_node": {"hosts": node_hosts},
            "etcd": {"hosts": node_hosts},
            "mongodb": {"hosts": node_hosts},
            "deploy": {"hosts": [master_hosts[0]]},
            "rocketmq": {"hosts": [node_hosts[len(node_hosts) - 1]]},
            "all": {
                "vars": group_all_vars
            }
        },
        "host_vars": host_vars
    }

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
        group_all_vars["MASTER_IP"] = k8s_config["KUBE_MASTER_VIP"]
        # 双Master部署模式设置端口为8443
        group_all_vars["KUBE_APISERVER"] = "https://{{ MASTER_IP }}:8443"
    else:
        group_all_vars["MASTER_IP"] = master_hosts[0]
        group_all_vars["KUBE_APISERVER"] = "https://{{ MASTER_IP }}:6443"

    # 计算服务网段
    if "SERVICE_CIDR" in k8s_config:
        service_cidr = IPv4Network(k8s_config["SERVICE_CIDR"].decode("iso-8859-1"))
    else:
        cluster_cidr = IPv4Network(k8s_config["CLUSTER_CIDR"].decode("iso-8859-1"))
        # POD网络位数是16~20时分别对应的服务网络位数。
        # 如：POD网络位数是20，对应的服务网络位数是24，可以有254个服务IP
        prefix_length_conf = [22, 23, 23, 23, 24]
        calc_masks = [0x0000fc00, 0x00007c00, 0x00003e00, 0x00001e00, 0x00000f00]
        idx = cluster_cidr.prefixlen - 16
        if (idx < 0):
            idx = 0
        service_cidr_addr = (int(cluster_cidr.network_address) & 0xffffff00) | calc_masks[idx]
        service_cidr = IPv4Network((service_cidr_addr, prefix_length_conf[idx]))
        group_all_vars["SERVICE_CIDR"] = str(service_cidr)

    # kubernetes服务IP默认分配为服务网段一个IP
    if "CLUSTER_KUBERNETES_SVC_IP" not in k8s_config:
        group_all_vars["CLUSTER_KUBERNETES_SVC_IP"] = str(service_cidr.network_address + 1)

    # DNS服务IP默认分配为服务网段第2个IP
    if "CLUSTER_DNS_SVC_IP" not in k8s_config:
        group_all_vars["CLUSTER_DNS_SVC_IP"] = str(service_cidr.network_address + 2)

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
    host_data = parse_host_data(os.getcwd() + "/workspace")
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
