#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import subprocess
import sys
import re
import ssl
import flask, json
import time
import yaml
import pexpect
from IPy import IP
from flask import Flask, jsonify, request
from threading import Thread
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    filename='/var/log/kadapi.log'
)

server = flask.Flask(__name__)  # 把app.python文件当做一个server


def read_yml(file_path):
    try:
        file = open(file_path)
        config = yaml.load(file, Loader=yaml.SafeLoader)
        file.close()
        return config
    except Exception as e:
        logging.error(e)
    return {}


api_config = read_yml('/etc/kad/api/kadapi.yaml')
kad_config = read_yml('/opt/kad/workspace/k8s/conf/all.yml')
smp_config = read_yml('/opt/kad/workspace/ruijie-smpplus/conf/all.yml')


# 获取token

#
@server.route('/kadapi/systemConfig/certs/getExpiryDate', methods=['get', 'post'])
def get_expiry_date():
    result = {
        "code": 200,
        "message": "ok",
        "result": True,
        "data": {}
    }
    data = json.loads(request.get_data(as_text=True))
    logging.debug("certificate expiryDate request parameter:" + str(data))
    if "certNames" not in data.keys():
        result["result"] = False
        result["code"] = 204
        result["message"] = 'Parameter illegal'
        return result
    cert_names = list(data["certNames"])
    if len(cert_names) < 1:
        result["result"] = False
        result["code"] = 204
        result["message"] = 'certNames is empty'
        return result

    expiry_dates = {}
    data_dir = str(os.popen("cat /etc/kad/config.yml |awk -F ' ' '{print $2}'|tr -d '\"'").readline()).replace(" ",
                                                                                                               "").replace(
        "\n", "")
    logging.debug("data_dir:" + data_dir)
    if len(data_dir) < 1:
        result["result"] = False
        result["code"] = 204
        result["message"] = 'data_dir is empty'
        return result

    for cert_name in cert_names:
        time_stamp = validity_calculation(data_dir, cert_name)
        expiry_dates[cert_name] = time_stamp
    result["data"] = expiry_dates

    return result


def validity_calculation(data_dir, cert_name):
    # 证书路径
    cert_path = data_dir + "/ruijie/ruijie-smpplus/share/certs/" + cert_name
    try:
        output = str(os.popen("certDate=$(echo |openssl x509 -in " + cert_path +
                              " -noout -dates |grep notAfter | awk -F '=' '{print $2}');certTime=$(date -d \"${certDate}\" "
                              "+'%s');echo $certTime").readline().replace(" ", "").replace("\n", ""))
        logging.debug("validity_calculation-->output:" + output)
        if len(output) < 1:
            logging.info("validity calculation is empty")
            return 0
        return output
    except Exception as e:
        logging.error(e)
        return 0


@server.route('/kadapi/systemConfig/certs/enabled', methods=['get', 'post'])
def certs_enabled():
    result = {
        "code": 200,
        "message": "ok",
        "result": True,
        "data": {}
    }
    data = json.loads(request.get_data(as_text=True))
    logging.debug("certificate validity request parameter:" + str(data))
    keys = ['oldCertName', "oldCertPriKeyPWD", 'certName', 'certPriKeyPWD', ]
    if all(t not in data.keys() for t in keys):
        result["result"] = False
        result["code"] = 204
        result["message"] = 'Parameter illegal'
        return result
    data_dir = str(
        os.popen("cat /etc/kad/config.yml |awk -F ' ' '{print $2}'|tr -d '\"'").readline().replace(" ", "").replace(
            "\n", ""))
    logging.debug("data_dir:" + data_dir)
    if len(data_dir) < 1:
        result["result"] = False
        result["code"] = 204
        result["message"] = 'data_dir is empty'
        return result

    # 1.copy certs
    # 2.restart freeradius pod
    cert_name = data["certName"]
    old_cert_name = data["oldCertName"]
    cert_private_key_pwd = data["certPriKeyPWD"]
    old_cert_private_key_pwd = data["oldCertPriKeyPWD"]
    certs_path = data_dir + "/ruijie/ruijie-smpplus/share/certs/" + cert_name
    logging.debug("prepare to copy cert. certs_path:" + certs_path)
    copy_result_1 = int(
        os.system("\\cp -f " + certs_path + "  /opt/kad/workspace/ruijie-smpplus/conf/freeradius/certs/" + cert_name))
    copy_result_2 = int(
        os.system("\\cp -f " + certs_path + "  " + data_dir + "/ruijie/ruijie-smpplus/freeradius/certs/" + cert_name))
    if not copy_result_1 == 0 or not copy_result_2 == 0:
        result["result"] = False
        result["code"] = 204
        result["message"] = 'copy certs fail'
        return result
    logging.debug("prepare to replace related args")
    # 3.replace certName and certPriKeyPWD
    effect_certs_config_file = data_dir + "/ruijie/ruijie-smpplus/freeradius/mods-available/eap"
    kad_certs_config_file = "/opt/kad/workspace/ruijie-smpplus/conf/freeradius/mods-available/eap"
    freeradius_yml_file = "/opt/kad/workspace/ruijie-smpplus/yaml/freeradius/freeradius.yml"
    freeradius_yml_role_file = "/opt/kad/roles/ruijie/smpplus/freeradius/templates/freeradius.yaml.j2"

    effect_result_pwd = int(os.system(
        "sed -i '/^.*private_key_password = /s/" + old_cert_private_key_pwd + "/" + cert_private_key_pwd + "/' " + effect_certs_config_file))
    effect_result_file_1 = int(os.system(
        "sed -i '/^.*private_key_file = /s/" + old_cert_name + "/" + cert_name + "/' " + effect_certs_config_file))
    effect_result_file_2 = int(os.system(
        "sed -i '/^.*certificate_file = /s/" + old_cert_name + "/" + cert_name + "/' " + effect_certs_config_file))

    kad_result_pwd = int(os.system(
        "sed -i '/^.*private_key_password = /s/" + old_cert_private_key_pwd + "/" + cert_private_key_pwd + "/' " + kad_certs_config_file))
    kad_result_file_1 = int(os.system(
        "sed -i '/^.*private_key_file = /s/" + old_cert_name + "/" + cert_name + "/' " + kad_certs_config_file))
    kad_result_file_2 = int(os.system(
        "sed -i '/^.*certificate_file = /s/" + old_cert_name + "/" + cert_name + "/' " + kad_certs_config_file))

    freeradius_yml_result_1 = int(os.system(
        "sed -i '/^.*mountPath: \/usr\/local\/etc\/raddb\/certs/s/" + old_cert_name + "/" + cert_name + "/' " + freeradius_yml_file))
    freeradius_yml_result_2 = int(
        os.system("sed -i '/^.*subPath:/s/" + old_cert_name + "/" + cert_name + "/' " + freeradius_yml_file))

    freeradius_yml_role_result_1 = int(os.system(
        "sed -i '/^.*mountPath: \/usr\/local\/etc\/raddb\/certs/s/" + old_cert_name + "/" + cert_name + "/' " + freeradius_yml_role_file))
    freeradius_yml_role_result_2 = int(
        os.system("sed -i '/^.*subPath:/s/" + old_cert_name + "/" + cert_name + "/' " + freeradius_yml_role_file))

    if not effect_result_pwd == 0 or not effect_result_file_1 == 0 or not effect_result_file_2 == 0:
        result["result"] = False
        result["code"] = 204
        result["message"] = 'replace effect certName and certPriKeyPWD fail'
        return result

    if not kad_result_pwd == 0 or not kad_result_file_1 == 0 or not kad_result_file_2 == 0:
        result["result"] = False
        result["code"] = 204
        result["message"] = 'replace kad certName and certPriKeyPWD fail'
        return result

    if not freeradius_yml_result_1 == 0 or not freeradius_yml_result_2 == 0:
        result["result"] = False
        result["code"] = 204
        result["message"] = 'replace freeradius_yml certName fail'
        return result

    if not freeradius_yml_role_result_1 == 0 or not freeradius_yml_role_result_2 == 0:
        result["result"] = False
        result["code"] = 204
        result["message"] = 'replace freeradius_yml_role certName fail'
        return result

    logging.debug("replace file and args success, preparing to restart freeradius")
    restart_pod = int(
        os.system("cd /opt/kad/workspace/ruijie-smpplus/yaml/freeradius;kubectl delete -f freeradius.yml && "
                  "kubectl create -f freeradius.yml"))
    if not restart_pod == 0:
        result["result"] = False
        result["code"] = 204
        result["message"] = 'restart freeradius pod fail'
        return result
    # 4.rm old certs
    if not cert_name == old_cert_name:
        logging.debug("preparing to delete old_cert. old_cert_name:" + old_cert_name)
        os.system("rm -rf /opt/kad/workspace/ruijie-smpplus/conf/freeradius/certs/" + old_cert_name)
        os.system("rm -rf  " + data_dir + "/ruijie/ruijie-smpplus/freeradius/certs/" + old_cert_name)

    return result


@server.route('/kadapi/systemConfig/certs/getFreeradiusStatus', methods=['get', 'post'])
def get_freeradius_status():
    result = {
        "code": 200,
        "message": "ok",
        "result": False,
        "data": {
        }
    }
    try:
        output = os.popen('kubectl get pod -A')
        for line in output.readlines():
            if ('rg-freeradius' in line and 'Running' in line):
                result["result"] = True
                logging.debug("the freeradius pod is running")
                break
    except Exception as e:
        logging.error(e)
        result["result"] = False
        result["code"] = 204
        result["message"] = 'get_freeradius_status exception'
        return result
    return result


@server.route('/kadapi/systemConfig/networkConfig/serverPwdCheck', methods=['get', 'post'])
def server_pwd_check():
    result = {
        "code": 200,
        "message": "ok",
        "result": True,
        "data": {
        }
    }

    data = json.loads(request.get_data(as_text=True))
    logging.debug("server_pwd_check request parameter:" + str(data))
    keys = ['serverUser', "serverPwd", 'hostIp', ]
    if all(t not in data.keys() for t in keys):
        result["result"] = False
        result["code"] = 204
        result["message"] = 'Parameter illegal'
        return result

    serverUser = str(data["serverUser"])
    result["serverUser"] = serverUser
    serverPwd = str(data["serverPwd"])
    hostIp = str(data["hostIp"])
    result["hostIp"] = hostIp
    if not pwd_verify_new(hostIp, serverUser, serverPwd):
        result["result"] = False
        result["code"] = 204
        result["message"] = 'pwd_verify_new is fail.'
        return result

    return result


@server.route('/kadapi/systemConfig/networkConfig/ipAddrCheck', methods=['get', 'post'])
def idaddr_check():
    result = {
        "code": 200,
        "message": "ok",
        "result": True,
        "date": {
            "ipParagraphPrompt": "196.200.192.0/20"
        }
    }

    data = json.loads(request.get_data(as_text=True))
    if "ipAddress" not in data.keys():
        result["result"] = False
        result["code"] = 204
        result["message"] = 'ipAddress NotFound'
        return result

    ip_address = str(data["ipAddress"])
    result["ipAddress"] = ip_address
    if not is_ip(ip_address):
        result["result"] = False
        result["code"] = 204
        result["message"] = 'ipAddress format was invalid'
        return result

    if ip_address in IP('196.200.192.0/20'):
        result["result"] = False
        result["code"] = 204
        result["message"] = 'ipAddress in 196.200.192.0/20'
        return result
    return result


@server.route('/kadapi/systemConfig/networkConfig/save', methods=['get', 'post'])
def save_ip():
    result = {
        "code": 200,
        "message": "ok",
        "result": True,
        "date": {}
    }
    data = json.loads(request.get_data(as_text=True))
    keys = ['ipAddress', 'subnetMask', 'defaultGateway', 'firstDnsServer', 'spareDnsServer', 'ipParagraphPrompt', ]
    if all(t not in data.keys() for t in keys):
        result["result"] = False
        result["code"] = 204
        result["message"] = 'Parameter illegal'
        return result

    keys = ['accessMode', 'certName', 'certKeyName', 'adminDomainName', 'portalDomainName', 'serverUser', 'serverPwd', ]
    if all(t not in data.keys() for t in keys):
        result["result"] = False
        result["code"] = 204
        result["message"] = 'access mode Parameter illegal'
        return result

    if not is_ip(data['ipAddress']) or not is_ip(data['firstDnsServer']) or not is_ip(data['subnetMask']):
        result["result"] = False
        result["code"] = 204
        result["message"] = 'Parameter illegal'
        return result

    old_ip = prase_netfile()["date"]["ipAddress"]
    if not is_ip(old_ip):
        result["result"] = False
        result["code"] = 204
        result["message"] = '未获取到原IP'
        logging.error("can not get old IP from " + api_config['networkfile'])
        return result

    t = Thread(target=changeip_thread, args=(data,))
    t.start()
    return result


def changeip_thread(data):
    logging.info(data)
    logging.info("changeip: start changeip_thread.")
    current_net_info = prase_netfile()
    old_ip = current_net_info["date"]["ipAddress"]
    new_ip = data["ipAddress"]

    #模式切换对应的操作
    access_mode_change(current_net_info, data)
    logging.info("changeip: The access_mode_change conversion operation is complete.")
    output_uname= subprocess.check_output("uname -r", shell=True).decode("utf-8")
    output_uname=output_uname.replace("\n","")
    output_uname=output_uname.replace(" ","")
    edit_netfile(data)
    if (old_ip == new_ip):
        logging.info("changeip: old_ip equals new_ip, only restart network")
        if ".an8" in output_uname or  ".oe2203" in output_uname :
            os.system('systemctl restart NetworkManager.service && sleep 2 && nmcli networking off && sleep 2 && nmcli networking on  &&  systemctl restart docker')
        else:
            os.system('systemctl restart network')    
        return

    logging.info("changeip: old_ip is not equal to new_ip. old_ip: " + old_ip + " new_ip: " + new_ip)
    file_list = api_config['filelist']
    for filepath in file_list:
        time.sleep(0.2)
        logging.info("changeip:start change file-->" + filepath)
        status_code = int(os.system('sed -i "s/' + old_ip + '/' + new_ip + '/g" ' + filepath))
        logging.info("changeip:end change file-->" + filepath + "execution return status code-->" + str(status_code))

    # logging.info("changeip: start replacing mongofile")
    # filepath = api_config['mongofile']
    #
    # os.system('cp ' + filepath + ' ' + filepath + 'temp')
    # os.system('sed -i "s/oldIp/' + old_ip + '/g" ' + filepath)
    # os.system('sed -i "s/newIp/' + new_ip + '/g" ' + filepath)
    logging.info("changeip: restart network start."+output_uname)
    if ".an8" in output_uname or  ".oe2203" in output_uname :
        logging.info("changeip: restart network start. nmcli networking off && nmcli networking on")
        restart_network_status_code = int(os.system('systemctl restart NetworkManager.service && sleep 2 && nmcli networking off && sleep 2 && nmcli networking on &&  systemctl restart docker'))
    else:
        logging.info("changeip: restart network start. nmcli networking off && nmcli networking on")
        restart_network_status_code = int(os.system('systemctl restart network'))   
 
    logging.info("changeip: restart_network_status_code ---->" + str(restart_network_status_code))
    logging.info("changeip: restart network end.")
    time.sleep(5)

    maintenance_shell_script = "smpplus-oper.sh"
    maintenance_shell_script_path = "/opt/kube/maintenance/script/smpplus-oper.sh"
    if os.path.isfile(maintenance_shell_script_path):
        logging.info("changeip:start stop maintenance-related shell script")
        stop_script_status_code = int(os.system("sed -i '/" + maintenance_shell_script + "/d' /var/spool/cron/root"))
        logging.info("changeip:end stop maintenance-related shell script" + "execution return status code-->" + str(
            stop_script_status_code))
    #serverUser = submit_info['serverUser']
    serverPwd = data['serverPwd']
    serverUser = data['serverUser']
    logging.info("changeip: start shell_change_ip.")
    #os.system('sh /etc/kad/api/changeip.sh ' + old_ip + ' ' + new_ip)
    shell_change_ip(serverUser,serverPwd, old_ip, new_ip)
    logging.info("changeip: end shell_change_ip.")
    # change_mongoip = True
    # while change_mongoip:
    #     try:
    #         output = os.popen('kubectl get pod -A')
    #         for line in output.readlines():
    #             if ('mongo1-0' in line and 'Running' in line):
    #                 change_mongoip = False
    #                 break
    #     except Exception as e:
    #         time.sleep(5)
    #         logging.error(e)
    #
    # change_mongoip = True
    # while change_mongoip:
    #     try:
    #         change_mongoip = False
    #         output = os.popen('kubectl exec -n ruijie-smpplus mongo1-0 -- mongo -u admin -p ' + smp_config[
    #             'MONGODB_ADMIN_PWD'] + '  --authenticationDatabase admin  /ruijie/init/smpplus/rg-init-db/update-replset.js')
    #         for line in output.readlines():
    #             if ('fail' in line):
    #                 change_mongoip = True
    #                 logging.error("update mongo fail: " + line)
    #                 time.sleep(0.5)
    #                 break
    #     except Exception as e:
    #         change_mongoip = True
    #         time.sleep(0.5)
    #         logging.error(e)
    #
    # os.system('mv -f ' + filepath + 'temp ' + filepath)
    # logging.info("changeip: success update mongo")
    #
    # if os.path.isfile(maintenance_shell_script_path):
    #     logging.info("changeip: start startup maintenance-related shell script")
    #     stop_script_status_code = int(os.system(
    #         "echo '*/1 * * * * sh " + maintenance_shell_script_path + " >/dev/null 2>&1'  >> /var/spool/cron/root"))
    #     logging.info("changeip: end startup maintenance-related shell script" + "execution return status code-->" + str(
    #         stop_script_status_code))

    logging.info("changeip: task executed successfully")

    logging.info("changeip: start restart the kadapi service. This operation will affect the kadapi service.")
    os.system('systemctl daemon-reload && systemctl restart kadapi')

@server.route('/kadapi/systemConfig/networkConfig/get', methods=['get', 'post'])
def get_network_config():
    return prase_netfile()


def prase_netfile():
    result = {
        "code": 200,
        "message": "ok",
        "date": {
            "ipAddress": "",
            "subnetMask": "",
            "defaultGateway": "",
            "firstDnsServer": "",
            "spareDnsServer": "",
            "ipParagraphPrompt": "",
            "accessMode": "1",
            "certName": "",
            "certKeyName": "",
            "adminDomainName": "",
            "portalDomainName": ""
        }
    }

    try:
        # 获取访问模式及其相关数据
        access_mode_related_template = access_mode_data()
        result["date"]["accessMode"] = access_mode_related_template.get("accessMode", "1")
        result["date"]["certName"] = access_mode_related_template.get("certName", "")
        result["date"]["certKeyName"] = access_mode_related_template.get("certKeyName", "")
        result["date"]["adminDomainName"] = access_mode_related_template.get("adminDomainName", "")
        result["date"]["portalDomainName"] = access_mode_related_template.get("portalDomainName", "")
        eth0_data = {}
        file = open(api_config['networkfile'])
        for line in file:
            a = line.strip()
            if len(a) == 0:
                continue
            if a.startswith('#'):
                continue
            if a.find("=") == -1:
                continue
            key = str(line.split('=')[0]).strip()
            value = str(line.split('=')[1]).strip()
            value = value.replace('\"', '')
            eth0_data[key] = value
        if 'NETMASK' in eth0_data.keys() and 'PREFIX' not in eth0_data.keys():
            eth0_data['PREFIX'] = exchange_intmask(eth0_data.get('NETMASK', ""))
        # 不配置子网，默认24位
        if 'PREFIX' not in eth0_data.keys():
            eth0_data['PREFIX'] = 24
        result["date"]["ipAddress"] = eth0_data.get('IPADDR', "")
        result["date"]["subnetMask"] = exchange_maskint(int(eth0_data.get('PREFIX', "")))
        result["date"]["defaultGateway"] = eth0_data.get('GATEWAY', "")
        result["date"]["firstDnsServer"] = eth0_data.get('DNS1', "")
        result["date"]["spareDnsServer"] = eth0_data.get('DNS2', "")
        result["date"]["ipParagraphPrompt"] = kad_config.get('CLUSTER_CIDR', "")
        return result
    except Exception as e:
        result["code"] = 204
        result["message"] = 'get network message error: ' + str(e)
        logging.error('get network message error: ' + str(e))
        return result


def edit_netfile(conf):
    try:
        file_data = ""
        cover_map = {'IPADDR': 'ipAddress', 'GATEWAY': 'defaultGateway', 'DNS1': 'firstDnsServer',
                     'DNS2': 'spareDnsServer', 'PREFIX': 'subnetMask'}
        eth0_data = {}
        conf['subnetMask'] = exchange_intmask(conf['subnetMask'])
        with open(api_config['networkfile'], "r") as file:
            for line in file:
                if ('=' not in line):
                    continue
                key = str(line.split('=')[0])
                if (key in cover_map.keys()):
                    line = key + '=' + str(conf[cover_map[key]]) + '\n'
                    del cover_map[key]
                file_data += line
            for key in cover_map.keys():
                file_data = file_data + key + '=' + str(conf[cover_map[key]]) + '\n'
        with open(api_config['networkfile'], "w") as f:
            f.write(file_data)

    except Exception as e:
        logging.error(e)
    return


def exchange_maskint(mask_int):
    bin_arr = ['0' for i in range(32)]
    for i in range(mask_int):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)


def exchange_intmask(netmask):
    result = ''
    for num in netmask.split('.'):
        temp = str(bin(int(num)))[2:]
        result = result + temp
    return len("".join(str(result).split('0')[0:1]))


def is_ip(str):
    try:
        IP(str)
        return True
    except Exception as e:
        return False


def access_mode_data():
    access_mode_related_template = {
        "accessMode": "1",
        "certName": "",
        "certKeyName": "",
        "adminDomainName": "",
        "portalDomainName": ""
    }

    admin_domain = str(os.popen(
        "cat /opt/kad/workspace/ruijie-smpplus/conf/all.yml | grep SMPPLUS_SSO_DOMAIN |awk -F ': ' '{print $2}'|tr -d '\"'").readline().replace(
        " ", "").replace("\n", ""))
    portal_domain = str(os.popen(
        "cat /opt/kad/workspace/ruijie-smpplus/conf/all.yml | grep SMPPLUS_PORTAL_DOMAIN |awk -F ': ' '{print $2}'|tr -d '\"'").readline().replace(
        " ", "").replace("\n", ""))
    ingress_mode_comment = str(os.popen(
        "cat /opt/kad/workspace/k8s/conf/all.yml | grep ingress_mode |awk -F ': ' '{print $1}' ").readline().replace(
        " ", "").replace("\n", ""))
    ingress_mode = str(os.popen(
        "cat /opt/kad/workspace/k8s/conf/all.yml | grep ingress_mode |awk -F ': ' '{print $2}'|tr -d '\"'").readline().replace(
        " ", "").replace("\n", ""))
    ingress_ssl_names = str(os.popen(
        "cat /opt/kad/workspace/k8s/conf/all.yml | grep ingress_ssl_names |awk -F ': ' '{print $2}'|tr -d '['| tr -d ']'|tr -d '\"'").readline().replace(
        " ", "").replace("\n", ""))

    if str_is_empty(admin_domain):
        admin_domain = ""
    if str_is_empty(portal_domain):
        portal_domain = ""
    if str_is_empty(ingress_mode_comment):
        ingress_mode_comment = ""
    if str_is_empty(ingress_mode):
        ingress_mode = ""
    if str_is_empty(ingress_ssl_names):
        ingress_ssl_names = ""
    accessMode = "1"
    domain_flag = False
    if admin_domain == "" and portal_domain == "":
        domain_flag = False
    else:
        domain_flag = True

    logging.info("admin_domain or portal_domain is: " + str(domain_flag))
    if ingress_mode_comment == "" or ingress_mode_comment.find("#") > -1:
        #不存在ingress mode 只需要判断 http域名  ip
        #存在ingress mode 但是被注释掉了，只需要判断 http域名  ip
        logging.info("ingress_mode does not exist or is commented out.")
        if not domain_flag:
            accessMode = "1"
        else:
            accessMode = "2"
    else:
        #存在ingress mode，需要判断是 https  还是http  http情况需要考虑ip 或域名
        logging.info("ingress_mode exist.")
        if ingress_mode != "" and ingress_mode.find("https") > -1:
            accessMode = "3"
        else:
            if not domain_flag:
                accessMode = "1"
            else:
                accessMode = "2"

    certName = ""
    certKeyName = ""
    if accessMode == "3":
        if not str_is_empty(ingress_ssl_names):
            certName = ingress_ssl_names + ".pem"
        if not str_is_empty(ingress_ssl_names):
            certKeyName = ingress_ssl_names + "-key.pem"

    access_mode_related_template['accessMode'] = accessMode
    access_mode_related_template['certName'] = certName
    access_mode_related_template['certKeyName'] = certKeyName
    access_mode_related_template['adminDomainName'] = admin_domain
    access_mode_related_template['portalDomainName'] = portal_domain
    logging.info("access_mode_data:access mode is --->" + str(accessMode))
    return access_mode_related_template


def str_is_empty(str1):
    if str1 is None or len(str1) == 0:
        return True
    else:
        return False


def pwd_verify_new(host_ip, username, password):
    try:
        output = os.popen('/usr/bin/which ssh')
        ssh_command_path = str(output.readline().replace(" ", "").replace("\n", ""))
        logging.info("pwd_verify_new: ssh_command_path---> " + ssh_command_path)
        #ssh_command_path = "/usr/local/openssh/bin/ssh"
        host_ip = "127.0.0.1"
        command = 'ls /etc/kad/'
        child = pexpect.spawn(ssh_command_path + ' -l %s %s %s' % (username, host_ip, command), timeout=2)
        ret = child.expect([pexpect.TIMEOUT, 'Are you sure you want to continue connecting', 'assword:'])
        if ret == 0:
            logging.info('[-] Error Connecting')
            return False
        if ret == 1:
            child.sendline('yes')
            ret = child.expect([pexpect.TIMEOUT, 'assword:'])
            if ret == 0:
                logging.info('[-] Error Connecting')
                return False
            if ret == 1:
                child.sendline(password)
        if ret == 2:
            child.sendline(password)
        child.expect(pexpect.EOF)
        logging.info("pwd verify success. " + str(child.before))
        return True
    except Exception as e:
        logging.error("Exception: pwd verify failed.", exc_info=True)
        return False


def access_mode_change(current_info, submit_info):
    try:
        logging.debug("access_mode_change is start.")
        data_dir = str(os.popen("cat /etc/kad/config.yml |awk -F ' ' '{print $2}'|tr -d '\"'").readline()).replace(" ","").replace("\n", "")
        logging.debug("access_mode_change: data_dir:" + data_dir)
        if len(data_dir) < 1:
            logging.error("access_mode_change: data_dir is empty....")
            return

        #current_info 读取现有配置，change_info页面传递来的参数
        current_accessMode = current_info["date"]["accessMode"]
        current_certName = current_info["date"]["certName"]
        current_certKeyName = current_info["date"]["certKeyName"]
        current_adminDomainName = current_info["date"]["adminDomainName"]
        current_portalDomainName = current_info["date"]["portalDomainName"]

        submit_accessMode = submit_info["accessMode"]
        submit_certName = submit_info["certName"]
        submit_certKeyName = submit_info["certKeyName"]
        submit_adminDomainName = submit_info["adminDomainName"]
        submit_portalDomainName = submit_info["portalDomainName"]

        logging.info("access_mode_change: The current access mode is " + current_accessMode + " , The submit access mode is " + submit_accessMode)
        #若模式存在切换则需要更新，
        #若模式未切换，则需要根据对应的模式进行配置：http域名模式，需要判断域名是否变化，变化则需要；https 如果证书不一致或域名不一致则变化
        if submit_accessMode == current_accessMode:
            if submit_accessMode == "1":
                logging.info("access_mode_change: The current accessMode is the same as the commit accessMode, and they are both mode 1 and do not need to do anything")
                return
            if submit_accessMode == "2":
                logging.info("access_mode_change: The current accessMode is the same as the commit accessMode, and they are both mode 2 and do need to do change")
                smpplus_all_change(submit_adminDomainName, submit_portalDomainName)
            if submit_accessMode == "3":
                logging.info("access_mode_change: The current accessMode is the same as the commit accessMode, and they are both mode 3 and do need to do change")
                k8s_all_change(current_accessMode, submit_accessMode, submit_certName, submit_certKeyName)
                smpplus_all_change(submit_adminDomainName, submit_portalDomainName)
                ingress_ssl_certs_change(data_dir, current_certName, current_certKeyName, submit_certName, submit_certKeyName)
        else:
            logging.info("access_mode_change: The current accessMode is different from the commit accessMode in that the submit_accessMode  is " + submit_accessMode)
            k8s_all_change(current_accessMode, submit_accessMode, submit_certName, submit_certKeyName)
            smpplus_all_change(submit_adminDomainName, submit_portalDomainName)
            ingress_ssl_certs_change(data_dir, current_certName, current_certKeyName, submit_certName, submit_certKeyName)

        #进行重启相关操作：ingress reconfig
        logging.info("access_mode_change: start restart ingress.")
        #serverUser = submit_info['serverUser']
        serverPwd = submit_info['serverPwd']
        #current_ipAddress = current_info["date"]["ipAddress"]
        restart_ingress(serverPwd)
        logging.info("access_mode_change: start restart business component.")
        restart_component(serverPwd)
        time.sleep(3)
    except Exception as e:
        logging.error("Exception: access_mode_change failed.", exc_info=True)
    return


def k8s_all_change(current_accessMode, submit_accessMode, submit_certName, submit_certKeyName):
    try:
        #logging.info("0. k8s_all_change: current_accessMode: " + current_accessMode + " ,submit_accessMode: " + submit_accessMode)
        ingress_params_1 = str(os.popen('cat /opt/kad/workspace/k8s/conf/all.yml |grep "ingress_mode" | cat ').readline()).replace(" ", "").replace("\n", "")
        ingress_params_2 = str(os.popen('cat /opt/kad/workspace/k8s/conf/all.yml |grep "ingress_ssl_names" | cat ').readline()).replace(" ", "").replace("\n", "")
        ingress_params_flag = True
        if str_is_empty(ingress_params_1) and str_is_empty(ingress_params_2):
            ingress_params_flag = False
        logging.info("0.k8s_all_change: Whether the ingress parameter exists: " + str(ingress_params_flag))

        ingress_mode_status_code = int(os.system("sed -i '/^.*ingress_mode/d' /opt/kad/workspace/k8s/conf/all.yml"))
        logging.info("1.k8s_all_change: k8s_all_change: delete ingress_mode shell script execution return status code-->" + str(ingress_mode_status_code))
        ingress_ssl_names_status_code = int(os.system("sed -i '/^.*ingress_ssl_names/d' /opt/kad/workspace/k8s/conf/all.yml"))
        logging.info("2.k8s_all_change: k8s_all_change: delete ingress_ssl_names shell script execution return status code-->" + str(ingress_ssl_names_status_code))

        if submit_accessMode == "3":
            ssl_names = submit_certName.replace(".pem", "")
            ingress_mode_status_code_2 = int(os.system("sed -i '$a ingress_mode: \"https\"' /opt/kad/workspace/k8s/conf/all.yml"))
            logging.info("3.k8s_all_change: k8s_all_change: add ingress_mode shell script execution return status code-->" + str(ingress_mode_status_code_2))
            ingress_ssl_names_status_code_2 = int(os.system("sed -i '$a ingress_ssl_names: [\"" + ssl_names + "\"]' /opt/kad/workspace/k8s/conf/all.yml"))
            logging.info("4.k8s_all_change: k8s_all_change: add ingress_ssl_names shell script execution return status code-->" + str(ingress_ssl_names_status_code_2))
    except Exception as e:
        logging.error("Exception: k8s_all_change failed.", exc_info=True)
    return


def smpplus_all_change(submit_adminDomainName, submit_portalDomainName):
    try:
        adminDomain_status_code = int(os.system("sed -i '/^.*SMPPLUS_SSO_DOMAIN/s/.*/SMPPLUS_SSO_DOMAIN: \"" + submit_adminDomainName + "\"/g' /opt/kad/workspace/ruijie-smpplus/conf/all.yml"))
        logging.info("smpplus_all_change: replace adminDomainName shell script execution return status code-->" + str(adminDomain_status_code))
        portalDomain_status_code = int(os.system("sed -i '/^.*SMPPLUS_PORTAL_DOMAIN/s/.*/SMPPLUS_PORTAL_DOMAIN: \"" + submit_portalDomainName + "\"/g' /opt/kad/workspace/ruijie-smpplus/conf/all.yml"))
        logging.info("smpplus_all_change: replace portalDomainName shell script execution return status code-->" + str(portalDomain_status_code))
    except Exception as e:
        logging.error("Exception: smpplus_all_change failed.", exc_info=True)
    return


def ingress_ssl_certs_change(data_dir, current_certName, current_certKeyName, submit_certName, submit_certKeyName):
    try:
        #判断ssl路径是否存在,不存在创建
        logging.info("/etc/kad/ssl/ exists info: " + str(os.path.exists("/etc/kad/ssl/")))
        if os.path.exists("/etc/kad/ssl/"):
            if str_is_empty(current_certName) or str_is_empty(current_certKeyName):
                logging.info("ingress_ssl_certs_change: 1.current_certName or current_certKeyName is empty. No deletion operation is required")
            else:
                #删除证书
                logging.debug("ingress_ssl_certs_change: 2.preparing to delete current_cert. current_certName:" + current_certName + " ,  current_certKeyName" + current_certKeyName)
                os.system("rm -rf /etc/kad/ssl/" + current_certName)
                os.system("rm -rf /etc/kad/ssl/" + current_certKeyName)
                logging.debug("ingress_ssl_certs_change: 3.delete current_cert end")
        else:
            logging.info("ingress_ssl_certs_change: 4.ssl path is not exist, create it")
            os.makedirs("/etc/kad/ssl/")

        if str_is_empty(submit_certName) or str_is_empty(submit_certKeyName):
            logging.info("ingress_ssl_certs_change: 5.submit_certName or submit_certKeyName is empty. No copy operation is required")
        else:
            #拷贝证书
            certs_path = data_dir + "/ruijie/ruijie-smpplus/share/network/" + submit_certName
            certKey_path = data_dir + "/ruijie/ruijie-smpplus/share/network/" + submit_certKeyName
            logging.debug("ingress_ssl_certs_change: 6.prepare to copy cert. certs_path:" + certs_path)
            copy_result_1 = int(os.system("\\cp -f " + certs_path + "  /etc/kad/ssl/" + submit_certName))
            copy_result_2 = int(os.system("\\cp -f " + certKey_path + "  /etc/kad/ssl/" + submit_certKeyName))
            logging.debug("ingress_ssl_certs_change: 7.copy cert result: " + str(copy_result_1) + " ,copy certKey result: " + str(copy_result_2))
    except Exception as e:
        logging.error("Exception: ingress_ssl_certs_change failed.", exc_info=True)
    return


def restart_ingress(serverPwd):
    try:
        #只重启ingress组件
        logging.debug("restart_ingress: restart_ingress is start.")
        password = serverPwd
        output = os.popen("kubectl delete -f /opt/kube/kube-system/nginx-ingress/")
        #删除执行后k8s调度存在时间差，可能会导致后续判断删除的跳过
        time.sleep(5)
        while not pod_running_check():
            logging.debug("restart_ingress:Failed to check all pod running. Wait 5 seconds and check again")
            time.sleep(5)
        logging.debug("restart_ingress: nginx-ingress delete success.")

        # spawn启动reconfig程序
        shell_cmd = 'cd /opt/kad;kad-play playbooks/cluster/ingress.yml'
        process = pexpect.spawn('/bin/bash', ['-c', shell_cmd])
        # expect方法等待scp产生的输出，判断是否匹配指定的字符串Password:
        process.expect('password:')
        # 若匹配，则发送密码响应
        process.sendline(password)
        process.expect(pexpect.EOF, timeout=None)
        logging.info("restart_ingress: reconfig command is executed")
        time.sleep(2)
        logging.debug("restart_ingress: restart_ingress is end.")
    except Exception as e:
        logging.error("Exception: restart_ingress failed.", exc_info=True)
    return


def restart_component(serverPwd):
    try:
        logging.debug("restart_component: restart_component is start.")
        #只重启业务组件
        password = serverPwd
        # spawn启动reconfig程序
        shell_cmd = 'cd /opt/kad;kad-play playbooks/smpplus/update-pod.yml'
        process = pexpect.spawn('/bin/bash', ['-c', shell_cmd])
        # expect方法等待scp产生的输出，判断是否匹配指定的字符串Password:
        process.expect('password:')
        # 若匹配，则发送密码响应
        process.sendline(password)
        process.expect(pexpect.EOF, timeout=None)
        logging.info("restart_component: reconfig command is executed")
        time.sleep(2)
        logging.debug("restart_component: restart_component is start end .")
    except Exception as e:
        logging.error("Exception: restart_component failed.", exc_info=True)
    return


#检测到没在运行的就返回false， 检测到都运行返回true
def pod_running_check():
    flag = False
    try:
        output = os.popen('kubectl get pod -A')
        pod_count = len(output.readlines()) - 1
        num = 0
        logging.debug("1.kubectl get pod -A count: " + str(pod_count))
        output = os.popen('kubectl get pod -A')
        for line in output.readlines():
            if ('NAMESPACE' in line and 'RESTARTS' in line):
                logging.debug("2.This line does not contain pod")
                continue
            if ('Running' not in line):
                logging.debug("pod_running_check: not Running pod name-->: " + line)
                #只要有一行不是则直接结束
                break
            else:
                num += 1
        logging.debug("3.The number of Pods running is: " + str(num))
        if num == pod_count:
            flag = True
            logging.debug("4.1pod is all running")
        else:
            flag = False
            logging.debug("4.2pod is not all running")
    except Exception as e:
        logging.error(e)
        return False
    return flag


def shell_change_ip(serverUser,serverPwd, old_ip, new_ip):
    try:
        logging.debug("shell_change_ip: shell_change_ip is start")
        #只重启业务组件
        password = serverPwd
        # spawn启动reconfig程序
        shell_cmd = 'sh /opt/kad/changeip.sh ' + old_ip + ' ' + new_ip + ' Web_changeIp ' +serverUser
        logging.debug(shell_cmd)
        process = pexpect.spawn('/bin/bash', ['-c', shell_cmd])
        # expect方法等待scp产生的输出，判断是否匹配指定的字符串Password:
        process.expect('password:')
        # 若匹配，则发送密码响应
        process.sendline(password)
        process.expect(pexpect.EOF, timeout=None)
        logging.info("shell_change_ip: shell_change_ip command is executed")
        time.sleep(2)
        logging.debug("shell_change_ip: shell_change_ip is end.")
    except Exception as e:
        logging.error("Exception: shell_change_ip failed.", exc_info=True)
    return


def main():
    CA_FILE = api_config['CA_FILE']
    KEY_FILE = api_config['KEY_FILE']
    CERT_FILE = api_config['CERT_FILE']
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    context.load_verify_locations(CA_FILE)
    context.verify_mode = ssl.CERT_REQUIRED

    server.run(host="0.0.0.0", port=api_config['port'], debug=True, ssl_context=context)


if __name__ == '__main__':
    main()
