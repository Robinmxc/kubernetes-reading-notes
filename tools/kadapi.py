#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
import re
import ssl
import flask, json
import time
import yaml
from IPy import IP
from flask import Flask, jsonify, request
from threading import Thread
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    filename='/var/log/messages'
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
    data_dir = str(os.popen("cat /etc/kad/config.yml |awk -F ' ' '{print $2}'|tr -d '\"'").readline()).replace(" ", "").replace("\n", "")
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
    data_dir = str(os.popen("cat /etc/kad/config.yml |awk -F ' ' '{print $2}'|tr -d '\"'").readline().replace(" ", "").replace("\n", ""))
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
    copy_result_1 = int(os.system("\\cp -f " + certs_path + "  /opt/kad/workspace/ruijie-smpplus/conf/freeradius/certs/" + cert_name))
    copy_result_2 = int(os.system("\\cp -f " + certs_path + "  " + data_dir + "/ruijie/ruijie-smpplus/freeradius/certs/" + cert_name))
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

    effect_result_pwd = int(os.system("sed -i '/^.*private_key_password = /s/" + old_cert_private_key_pwd + "/" + cert_private_key_pwd + "/' " + effect_certs_config_file))
    effect_result_file_1 = int(os.system("sed -i '/^.*private_key_file = /s/" + old_cert_name + "/" + cert_name + "/' " + effect_certs_config_file))
    effect_result_file_2 = int(os.system("sed -i '/^.*certificate_file = /s/" + old_cert_name + "/" + cert_name + "/' " + effect_certs_config_file))

    kad_result_pwd = int(os.system("sed -i '/^.*private_key_password = /s/" + old_cert_private_key_pwd + "/" + cert_private_key_pwd + "/' " + kad_certs_config_file))
    kad_result_file_1 = int(os.system("sed -i '/^.*private_key_file = /s/" + old_cert_name + "/" + cert_name + "/' " + kad_certs_config_file))
    kad_result_file_2 = int(os.system("sed -i '/^.*certificate_file = /s/" + old_cert_name + "/" + cert_name + "/' " + kad_certs_config_file))

    freeradius_yml_result_1 = int(os.system("sed -i '/^.*mountPath: \/usr\/local\/etc\/raddb\/certs/s/" + old_cert_name + "/" + cert_name + "/' " + freeradius_yml_file))
    freeradius_yml_result_2 = int(os.system("sed -i '/^.*subPath:/s/" + old_cert_name + "/" + cert_name + "/' " + freeradius_yml_file))

    freeradius_yml_role_result_1 = int(os.system("sed -i '/^.*mountPath: \/usr\/local\/etc\/raddb\/certs/s/" + old_cert_name + "/" + cert_name + "/' " + freeradius_yml_role_file))
    freeradius_yml_role_result_2 = int(os.system("sed -i '/^.*subPath:/s/" + old_cert_name + "/" + cert_name + "/' " + freeradius_yml_role_file))

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
    restart_pod = int(os.system("cd /opt/kad/workspace/ruijie-smpplus/yaml/freeradius;kubectl delete -f freeradius.yml && "
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
    old_ip = prase_netfile()["date"]["ipAddress"]
    new_ip = data["ipAddress"]

    edit_netfile(data)
    if (old_ip == new_ip):
        logging.info("changeip: old_ip equals new_ip, only restart network")
        os.system('systemctl restart network')
        return

    logging.info("changeip: old_ip is not equal to new_ip. old_ip: " + old_ip + " new_ip: " + new_ip)
    file_list = api_config['filelist']
    for filepath in file_list:
        time.sleep(0.2)
        logging.info("changeip:start change file-->" + filepath)
        status_code = int(os.system('sed -i "s/' + old_ip + '/' + new_ip + '/g" ' + filepath))
        logging.info("changeip:end change file-->" + filepath + "execution return status code-->" + str(status_code))

    logging.info("changeip: start replacing mongofile")
    filepath = api_config['mongofile']

    os.system('cp ' + filepath + ' ' + filepath + 'temp')
    os.system('sed -i "s/oldIp/' + old_ip + '/g" ' + filepath)
    os.system('sed -i "s/newIp/' + new_ip + '/g" ' + filepath)

    maintenance_shell_script = "smpplus-oper.sh"
    maintenance_shell_script_path = "/opt/kube/maintenance/script/smpplus-oper.sh"
    if os.path.isfile(maintenance_shell_script_path):
        logging.info("changeip:start stop maintenance-related shell script")
        stop_script_status_code = int(os.system("sed -i '/" + maintenance_shell_script + "/d' /var/spool/cron/root"))
        logging.info("changeip:end stop maintenance-related shell script" + "execution return status code-->" + str(stop_script_status_code))

    logging.info("changeip: start changeip.sh")
    os.system('sh /etc/kad/api/changeip.sh ' + old_ip + ' ' + new_ip)
    logging.info("changeip: end changeip.sh")
    change_mongoip = True
    while change_mongoip:
        try:
            output = os.popen('kubectl get pod -A')
            for line in output.readlines():
                if ('mongo1-0' in line and 'Running' in line):
                    change_mongoip = False
                    break
        except Exception as e:
            time.sleep(5)
            logging.error(e)

    change_mongoip = True
    while change_mongoip:
        try:
            change_mongoip = False
            output = os.popen('kubectl exec -n ruijie-smpplus mongo1-0 -- mongo -u admin -p ' + smp_config[
                'MONGODB_ADMIN_PWD'] + '  --authenticationDatabase admin  /ruijie/init/smpplus/rg-init-db/update-replset.js')
            for line in output.readlines():
                if ('fail' in line):
                    change_mongoip = True
                    logging.error("update mongo fail: " + line)
                    time.sleep(0.5)
                    break
        except Exception as e:
            change_mongoip = True
            time.sleep(0.5)
            logging.error(e)

    os.system('mv -f ' + filepath + 'temp ' + filepath)
    logging.info("changeip: success update mongo")

    if os.path.isfile(maintenance_shell_script_path):
        logging.info("changeip: start maintenance-related shell script")
        stop_script_status_code = int(os.system("echo '*/1 * * * * sh " + maintenance_shell_script_path + " >/dev/null 2>&1'  >> /var/spool/cron/root"))
        logging.info("changeip: end maintenance-related shell script" + "execution return status code-->" + str(stop_script_status_code))

    logging.info("changeip: task executed successfully")


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
            "ipParagraphPrompt": ""
        }
    }
    try:
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
