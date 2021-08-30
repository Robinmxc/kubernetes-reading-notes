#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import os
import re
import sys
import yaml
Py_version = sys.version_info
Py_v_info = str(Py_version.major) + '.' + str(Py_version.minor) + '.' + str(Py_version.micro)
if Py_version >= (3, 0):
    import importlib

from ipaddress import IPv4Network

def to_json(in_dict):
    return json.dumps(in_dict, sort_keys=True, indent=2)

def is_IP(str):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    return p.match(str)

def read_yml(file_path):
    file = open(file_path)
    config = yaml.load(file)
    file.close()
    return config

def parse_module_config(workspace_dir):
    result = {}
    file_list = os.listdir(workspace_dir)
    for x in file_list:
        full_path = workspace_dir + "/" + x
        full_path = full_path.replace("//", "/")
        if (os.path.isdir(full_path)):
            conf_file = full_path + "/conf/all.yml"
            if (os.path.exists(conf_file)):
                result[x] = read_yml(conf_file)
    return result

def parse_host_data(workspace_dir):
    group_all_vars = {
        "base_dir": "/opt/kad",
        "temp_dir": "/opt/kad/temp",
        "img_download_dir": "/opt/kad/down",
        "img_copy_dir": "/opt/kube/images",
        "workspace_dir": "/opt/kad/workspace",
        "KAD_FILES_REPO": "",
        "CLUSTER_SCALE": "normal",
        "KUBE_MASTER_VIP": ""
    }
    host_vars = {}
    result = {
        "groups": {
            "all": {
                "vars": group_all_vars
            }
        },
        "host_vars": host_vars
    }

    kad_meta_info = read_yml("/opt/kad/meta-info.yml")
    for k in kad_meta_info:
        group_all_vars[k] = kad_meta_info[k]

    # Parse all module configs
    module_configs = parse_module_config(workspace_dir)
    group_all_vars["module_configs"] = module_configs

    # Copy k8s config to global
    k8s_config = module_configs["k8s"]
    for k in k8s_config:
        group_all_vars[k] = k8s_config[k]

    # Configure app namespace
    env = os.environ
    if ("KAD_APP_NAMESPACE" in env):
        app_namespace = os.environ["KAD_APP_NAMESPACE"]
    else:
        app_namespace = "ruijie-sourceid"
    group_all_vars["APP_NAMESPACE"] = app_namespace

    # Copy app config to global
    if app_namespace in module_configs:
        app_config = module_configs[app_namespace]
        for k in app_config:
            group_all_vars[k] = app_config[k]

    # Configure KAD_APP_NAME
    if ("KAD_APP_NAME" in group_all_vars):
        app_name = group_all_vars["KAD_APP_NAME"]
    else:
        app_name = "sourceid"
        group_all_vars["KAD_APP_NAME"] = app_name

    # Configure KAD_PACKAGE_NAME
    if ("KAD_PACKAGE_NAME" in group_all_vars):
        kad_package_name = group_all_vars["KAD_PACKAGE_NAME"]
    else:
        kad_package_name = app_name + "-kad-" + group_all_vars["KAD_APP_VERSION"]
        group_all_vars["KAD_PACKAGE_NAME"] = kad_package_name

    # Configure KAD_PACKAGE_DIR
    if ("KAD_PACKAGE_DIR" not in group_all_vars):
        kad_package_dir = "/opt/kad/down/" + kad_package_name
        if not os.path.exists(kad_package_dir):
            kad_package_dir2 = group_all_vars["temp_dir"] + "/"  + kad_package_name
            if os.path.exists(kad_package_dir2):
                kad_package_dir = kad_package_dir2
        group_all_vars["KAD_PACKAGE_DIR"] = kad_package_dir

    # Configure host groups
    master_hosts = k8s_config["KUBE_MASTER_HOSTS"]
    node_hosts = k8s_config["KUBE_NODE_HOSTS"]
    for ip in master_hosts:
        if not is_IP(ip):
            raise Exception(ip + u"不是有效的IP地址")
    for ip in node_hosts:
        if not is_IP(ip):
            raise Exception(ip + u"不是有效的IP地址")
    result["groups"]["kube_master"] = {"hosts": master_hosts}
    result["groups"]["kube_node"] = {"hosts": node_hosts}
    result["groups"]["etcd"] = {"hosts": node_hosts}
    result["groups"]["mongodb"] = {"hosts": node_hosts}
    result["groups"]["deploy"] = {"hosts": [master_hosts[0]]}
    result["groups"]["rocketmq"] = {"hosts": [node_hosts[len(node_hosts) - 1]]}
    result["groups"]["mgob"] = {"hosts": [node_hosts[len(node_hosts) - 1]]}
    result["groups"]["pgsql"] = {"hosts": [node_hosts[len(node_hosts) - 1]]}

    # 设置K8S部署模式
    deploy_mode = "single-master"
    if (len(master_hosts) == 2):
        deploy_mode = "multi-master"
    elif (len(node_hosts) == 1 and node_hosts[0] == master_hosts[0]):
        deploy_mode = "allinone"
    group_all_vars["DEPLOY_MODE"] = deploy_mode

    if (deploy_mode == "multi-master"):
        if not is_IP(k8s_config["KUBE_MASTER_VIP"]):
            raise Exception(k8s_config["KUBE_MASTER_VIP"] + u"不是有效的IP地址")
        # 设置负载均衡节点
        result["groups"]["lb"] = {"hosts": master_hosts}
        # 双Master部署模式设置为虚
        group_all_vars["MASTER_IP"] = k8s_config["KUBE_MASTER_VIP"]
        # 双Master部署模式设置端口为8443
        group_all_vars["KUBE_APISERVER"] = "https://{{ MASTER_IP }}:8443"
    else:
        result["groups"]["lb"] = {"hosts": []}
        group_all_vars["MASTER_IP"] = master_hosts[0]
        group_all_vars["KUBE_APISERVER"] = "https://{{ MASTER_IP }}:6443"

    # 计算服务网段
    if "SERVICE_CIDR" in k8s_config:
        config_value = k8s_config["SERVICE_CIDR"].decode("iso-8859-1")
        try:
            service_cidr = IPv4Network(config_value)
        except ValueError:
            raise Exception(config_value + u"不是有效的网络地址")
    else:
        config_value = k8s_config["CLUSTER_CIDR"].decode("iso-8859-1")
        try:
            cluster_cidr = IPv4Network(config_value)
        except ValueError:
            raise Exception(config_value + u"不是有效的网络地址")

        # POD网络位数是16~23时分别对应的服务网络位数。
        # 如：POD网络位数是20，对应的服务网络位数是24，可以有254个服务IP
        prefix_length_conf = [22, 23, 23, 23, 24, 24, 24, 24]
        calc_masks = [0x0000fc00, 0x00007e00, 0x00003e00, 0x00001e00, 0x00000f00, 0x00000700, 0x00000300, 0x00000100]
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

    if "ingress_mode" not in k8s_config:
        group_all_vars["ingress_mode"] = "http"

    if "CLUSTER_SCALE" not in k8s_config:
        if deploy_mode == "allinone":
            group_all_vars["CLUSTER_SCALE"] = "single"
        else:
            group_all_vars["CLUSTER_SCALE"] = "normal"

    if "MONGODB_NODEPORT" not in group_all_vars:
        group_all_vars["MONGODB_NODEPORT"] = ""

    # 初始化Host变量
    for ip in master_hosts:
        host_vars[ip] = {"K8S_ROLE": "master"}
    for ip in node_hosts:
        host_vars[ip] = {"K8S_ROLE": "node"}

    # 设置负载均衡角色
    if (deploy_mode == "multi-master"):
        host_vars[master_hosts[0]]["LB_ROLE"] = "master"
        host_vars[master_hosts[1]]["LB_ROLE"] = "backup"

    # 设置nodekeepalive角色
    idx = 1
    for ip in node_hosts:
        host_vars[ip]["NODE_LB_ID"] = str(100000 + idx)
        if idx == 1:
            host_vars[ip]["NODE_LB_ROLE"] = "MASTER"
        else:
            host_vars[ip]["NODE_LB_ROLE"] = "BACKUP"
        idx = idx + 1

    # 设置ETCD节点名称
    idx = 1
    for ip in node_hosts:
        host_vars[ip]["NODE_NAME"] = "etcd" + bytes(idx)
        idx = idx + 1

    # 设置mongodb节点名称
    idx = 1
    for ip in result["groups"]["mongodb"]["hosts"]:
        host_vars[ip]["MONGO_NODE_NAME"] = "mongo" + bytes(idx)
        idx = idx + 1

    # 设置pgsql节点名称
    idx = 0
    for ip in result["groups"]["pgsql"]["hosts"]:
        host_vars[ip]["PG_NODE_NAME"] = "postgresql-" + bytes(idx)
        idx = idx + 1

    parse_fdfs_config(result)

    parse_sourceid_gateway_config(result)

    parse_sourcedata_config(result)

    parse_eoms_config(result)

    parse_ldap_config(result)
    
    return result

# 处理Ldap配置参数
def parse_ldap_config(host_data):
    group_all_vars = host_data["groups"]["all"]["vars"]
    ldap_hosts =  group_all_vars["LDAP"]["LDAP_HOST"] if "LDAP" in group_all_vars and "LDAP_HOST" in group_all_vars["LDAP"] else []
    ldap_vip = group_all_vars["LDAP"]["LDAP_VIP"] if "LDAP" in group_all_vars and "LDAP_VIP" in group_all_vars["LDAP"] else []
    if "LDAP" in group_all_vars and "enable" in group_all_vars["LDAP"] and group_all_vars["LDAP"]["enable"]:
        if len(ldap_hosts) !=1 and len(ldap_hosts) !=2:
          raise Exception(ldap_hosts + u"必须配置一个或者两个IP")
        for ip in ldap_hosts:
            if not is_IP(ip):
                raise Exception(ip + u"不是有效的IP地址")
        if not is_IP(ldap_vip):
            raise Exception(ldap_vip + u"不是有效的IP地址")
        if len(ldap_hosts) == 2 and len(ldap_vip) == 0:
          raise Exception("双主模式必须配置LDAP_VIP")

        host_data["groups"]["ldap"] = ldap_hosts
        group_all_vars["LDAP_VIP"] = ldap_vip
        group_all_vars["LDAP_MODEL"] = "dual" if len(ldap_hosts) == 2 else "single"

        host_vars = host_data["host_vars"]
        idx = 1
        for ip in ldap_hosts:
            if ip not in host_vars:
                host_vars[ip] = {}
            host_vars[ip]["LDAP_HOST_ID"] = str(100000 + idx)
            if idx == 1:
                host_vars[ip]["LDAP_ROLE"] = "MASTER"
            else:
                host_vars[ip]["LDAP_ROLE"] = "BACKUP"
            idx = idx + 1

# 处理监控系统配置参数
def parse_eoms_config(host_data):
    group_all_vars = host_data["groups"]["all"]["vars"]

    eoms_hosts =  group_all_vars["EOMS"]["EOMS_STORAGE_HOST"] if "EOMS" in group_all_vars and "EOMS_STORAGE_HOST" in group_all_vars["EOMS"] else []
    if "EOMS" in group_all_vars and "enable" in group_all_vars["EOMS"] and group_all_vars["EOMS"]["enable"]:
        for ip in eoms_hosts:
            if not is_IP(ip):
                raise Exception(ip + u"不是有效的IP地址")
        host_data["groups"]["influxdb"] = eoms_hosts
        host_data["groups"]["eoms"] = eoms_hosts


# 处理SourceData配置参数
def parse_sourcedata_config(host_data):
    group_all_vars = host_data["groups"]["all"]["vars"]

    sourcedata_hosts =  group_all_vars["SOURCEDATA_HOSTS"] if "SOURCEDATA_HOSTS" in group_all_vars else []
    for ip in sourcedata_hosts:
        if not is_IP(ip):
            raise Exception(ip + u"不是有效的IP地址")
    host_data["groups"]["sourcedata"] = sourcedata_hosts

    host_data["groups"]["sourcedata_mysql"] = sourcedata_hosts


# 处理二次认证网关配置参数
def parse_sourceid_gateway_config(host_data):
    group_all_vars = host_data["groups"]["all"]["vars"]

    if "SOURCEID_GATEWAY_DEPLOY_MODE" not in group_all_vars:
        group_all_vars["SOURCEID_GATEWAY_DEPLOY_MODE"] = "none"
    gateway_mode = group_all_vars["SOURCEID_GATEWAY_DEPLOY_MODE"]

    if "none" == gateway_mode or "k8s" == gateway_mode:
        host_data["groups"]["gateway"] = []
        return

    gateway_hosts =  group_all_vars["SOURCEID_GATEWAY_HOSTS"] if "SOURCEID_GATEWAY_HOSTS" in group_all_vars else []
    if len(gateway_hosts) == 0:
        raise Exception(u"SOURCEID_GATEWAY_HOSTS参数没有设置")
    for ip in gateway_hosts:
        if not is_IP(ip):
            raise Exception(ip + u"不是有效的IP地址")
    host_data["groups"]["gateway"] = gateway_hosts
    is_dual_hosts = len(gateway_hosts) == 2

    if "SOURCEID_GATEWAY_VIP" not in group_all_vars:
        group_all_vars["SOURCEID_GATEWAY_VIP"] = ""
    if "" != group_all_vars["SOURCEID_GATEWAY_VIP"]:
        if not is_IP(group_all_vars["SOURCEID_GATEWAY_VIP"]):
            raise Exception(u"SOURCEID_GATEWAY_VIP不是有效的IP地址")
        if not is_dual_hosts:
            raise Exception(u"SOURCEID_GATEWAY_HOSTS需要设置两个地址")
    else:
        if is_dual_hosts:
            raise Exception(u"SOURCEID_GATEWAY_VIP没有设置")

    access_host = gateway_hosts[0]
    if "k8s" == gateway_mode:
        access_host = "rg-gateway." + group_all_vars["APP_NAMESPACE"] + ".svc"
    elif "standalone" == gateway_mode:
        if "" != group_all_vars["SOURCEID_GATEWAY_VIP"]:
            access_host = group_all_vars["SOURCEID_GATEWAY_VIP"]
        else:
            access_host = gateway_hosts[0]
    group_all_vars["SOURCEID_GATEWAY_URL"] = "http://" + access_host + "/gateway"

    # 节点ID和角色
    host_vars = host_data["host_vars"]
    idx = 1
    for ip in gateway_hosts:
        if ip not in host_vars:
            host_vars[ip] = {}
        if is_dual_hosts:
            host_vars[ip]["GATEWAY_HOST_ID"] = str(100000 + idx)
            if idx == 1:
                host_vars[ip]["GATEWAY_ROLE"] = "MASTER"
            else:
                host_vars[ip]["GATEWAY_ROLE"] = "BACKUP"


# 处理FDFS配置参数
def parse_fdfs_config(host_data):
    group_all_vars = host_data["groups"]["all"]["vars"]

    # 设置FDFS参数
    if "FDFS_MODE" in group_all_vars:
        fdfs_mode = group_all_vars["FDFS_MODE"]
    else:
        fdfs_mode = "none"
        group_all_vars["FDFS_MODE"] = fdfs_mode

    if "none" == fdfs_mode:
        group_all_vars["FDFS_ACCESS_IP"] = ""
        host_data["groups"]["fdfs_tracker"] = []
        host_data["groups"]["fdfs_storage"] = []
        return

    storage_hosts = group_all_vars["FDFS_STORAGE_HOSTS"] if "FDFS_STORAGE_HOSTS" in group_all_vars else []
    if len(storage_hosts) == 0:
        raise Exception(u"FDFS_STORAGE_HOSTS参数没有设置")
    for ip in storage_hosts:
        if not is_IP(ip):
            raise Exception(ip + u"不是有效的IP地址")
    host_data["groups"]["fdfs_storage"] = storage_hosts

    if "FDFS_TRACKER_HOSTS" in group_all_vars:
        tracker_hosts = group_all_vars["FDFS_TRACKER_HOSTS"]
    else:
        if "dual" == fdfs_mode or "single" == fdfs_mode:
            tracker_hosts = storage_hosts
        else:
            tracker_hosts = []

    if len(tracker_hosts) == 0:
        raise Exception(u"FDFS_TRACKER_HOSTS参数没有设置")
    for ip in tracker_hosts:
        if not is_IP(ip):
            raise Exception(ip + u"不是有效的IP地址")
    host_data["groups"]["fdfs_tracker"] = tracker_hosts

    if "single" == fdfs_mode:
        if len(tracker_hosts) != 1 or len(storage_hosts) != 1 or tracker_hosts[0] != storage_hosts[0]:
            raise Exception(u"FDFS单机部署只能配置一个IP地址")
        group_all_vars["FDFS_ACCESS_IP"] = storage_hosts[0]
    else:
        fdfs_vip = group_all_vars["FDFS_VIP"] if "FDFS_VIP" in group_all_vars else ""
        if "" == fdfs_vip:
            raise Exception(u"FDFS_VIP参数没有设置")
        if "" != fdfs_vip and not is_IP(fdfs_vip):
            raise Exception(u"FDFS_VIP不是有效的IP地址")
        group_all_vars["FDFS_ACCESS_IP"] = fdfs_vip

        if len(storage_hosts) < 2:
            raise Exception(u"FDFS_STORAGE_HOSTS必须配置两个IP地址")

    if "FDFS_TRACKER_PORT" not in group_all_vars:
        group_all_vars["FDFS_TRACKER_PORT"] = "22122"
    if "FDFS_STORAGE_PORT" not in group_all_vars:
        group_all_vars["FDFS_STORAGE_PORT"] = "23000"
    if "FDFS_ACCESS_PORT" not in group_all_vars:
        group_all_vars["FDFS_ACCESS_PORT"] = "80"
    if "FDFS_GROUP_NAME" not in group_all_vars:
        group_all_vars["FDFS_GROUP_NAME"] = "group1"
    if "FDFS_ACCESS_URL" not in group_all_vars:
        if "80" == group_all_vars["FDFS_ACCESS_PORT"]:
            group_all_vars["FDFS_ACCESS_URL"] = "http://" + group_all_vars["FDFS_ACCESS_IP"] + "/" + group_all_vars["FDFS_GROUP_NAME"]
        else:
            group_all_vars["FDFS_ACCESS_URL"] = "http://" + group_all_vars["FDFS_ACCESS_IP"] + ":" + group_all_vars["FDFS_ACCESS_PORT"] + "/" + group_all_vars["FDFS_GROUP_NAME"]

    tmp = []
    for ip in storage_hosts:
        tmp.append(ip + ":" + group_all_vars["FDFS_TRACKER_PORT"])
    group_all_vars["FDFS_TRACKER_SERVERS"] = ",".join(tmp)

    # 设置FDFS Storage节点ID和角色
    host_vars = host_data["host_vars"]
    idx = 1
    for ip in storage_hosts:
        if ip not in host_vars:
            host_vars[ip] = {}
        host_vars[ip]["FDFS_HOST_ID"] = str(100000 + idx)
        if idx == 1:
            host_vars[ip]["FDFS_ROLE"] = "MASTER"
        else:
            host_vars[ip]["FDFS_ROLE"] = "BACKUP"
        idx = idx + 1

def main():
    if Py_version < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf8')
    else:
        importlib.reload(sys)
    try:
        host_data = parse_host_data(os.getcwd() + "/workspace")
        if len(sys.argv) == 2 and (sys.argv[1] == "--check"):
            print ("ok")
            exit(0)
    except Exception as e:
        if len(sys.argv) == 2 and (sys.argv[1] == "--check"):
            print (str(e))
            exit(0)
        else:
            raise

    if len(sys.argv) == 2 and (sys.argv[1] == '--all'):
        print(to_json(host_data))
    elif len(sys.argv) == 2 and (sys.argv[1] == "--list"):
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
