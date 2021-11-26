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
           

api_config=read_yml('/etc/kad/api/kadapi.yaml')
kad_config=read_yml('/opt/kad/workspace/k8s/conf/all.yml')
smp_config=read_yml('/opt/kad/workspace/ruijie-smpplus/conf/all.yml')
# 获取token
@server.route('/kadapi/systemConfig/networkConfig/ipAddrCheck', methods=['get', 'post'])
def idaddr_check():
    result = {
        "code": 200,
        "message": "ok",
        "result": True,
        "date" : {
            "ipParagraphPrompt": "196.200.192.0/20"
        }
      }

    data = json.loads(request.get_data(as_text=True))
    if "ipAddress" not in data.keys():
        result["result"]=False
        result["code"]=204
        result["message"]='ipAddress NotFound'
        return result

    ip_address = str(data["ipAddress"])   
    result["ipAddress"]=ip_address
    if not is_ip(ip_address):
        result["result"]=False
        result["code"]=204
        result["message"]='ipAddress format was invalid'
        return result

    if ip_address in IP('196.200.192.0/20'):
        result["result"]=False
        result["code"]=204
        result["message"]='ipAddress in 196.200.192.0/20'
        return result
    return result

@server.route('/kadapi/systemConfig/networkConfig/save', methods=['get', 'post'])  
def save_ip():
    result = {
        "code" : 200,
        "message" : "ok",
        "result": True,
        "date" : {}
        }
    data = json.loads(request.get_data(as_text=True))
    keys=['ipAddress','subnetMask','defaultGateway','firstDnsServer','spareDnsServer','ipParagraphPrompt',]
    if all(t not in data.keys() for t in keys):
        result["result"]=False
        result["code"]=204
        result["message"]='Parameter illegal'
        return result
    if not is_ip(data['ipAddress']) or not is_ip(data['firstDnsServer']) or not is_ip(data['subnetMask']):
        result["result"]=False
        result["code"]=204
        result["message"]='Parameter illegal'
        return result
    
    old_ip=prase_netfile()["date"]["ipAddress"]
    if not is_ip(old_ip):
        result["result"]=False
        result["code"]=204
        result["message"]='未获取到原IP'
        logging.error("can not get old IP from " + api_config['networkfile'])
        return result
    
    t=Thread(target=changeip_thread,args=(data,))
    t.start()
    return result


def changeip_thread(data):
    old_ip=prase_netfile()["date"]["ipAddress"]
    new_ip=data["ipAddress"]

    edit_netfile(data)
    if(old_ip == new_ip):
        os.system('systemctl restart network')
        return
    
    file_list=api_config['filelist']
    for filepath in file_list:
        logging.info("change file"+filepath)
        os.system('sed -i "s/'+old_ip+'/' + new_ip + '/g" '+ filepath)
    
    filepath=api_config['mongofile']
    os.system('sed -i "s/'+old_ip+'/' + new_ip + '/g" '+ filepath)
    os.system('sed -i "s/oldIp/' + old_ip + '/g" '+ filepath)
    os.system('sed -i "s/newIp/' + new_ip + '/g" '+ filepath)
    
    logging.info("start changeip.sh")
    os.system('sh /etc/kad/api/changeip.sh '+old_ip+' ' +new_ip )
    logging.info("end changeip.sh")
    change_mongoip=True
    while change_mongoip:
        try:
            output = os.popen('kubectl get pod -A')
            for line in output.readlines():
                if ('mongo1-0' in line and 'Running' in line):
                    change_mongoip=False
                    break
        except Exception as e:
            time.sleep(5)
            logging.error(e)
            
    change_mongoip=True
    while change_mongoip:
        try:
            change_mongoip=False
            output = os.popen('kubectl exec -n ruijie-smpplus mongo1-0 -- mongo -u admin -p ' + smp_config['MONGODB_ADMIN_PWD'] + '  --authenticationDatabase admin  /ruijie/init/smpplus/rg-init-db/update-replset.js')
            for line in output.readlines():
                if ('fail' in line):
                    change_mongoip=True
                    logging.error("update mongo fail: "+ line)
                    time.sleep(0.5)
                    break
        except Exception as e:
            change_mongoip=True
            time.sleep(0.5)
            logging.error(e)
    logging.info("success update mongo")

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
        file=open(api_config['networkfile'])
        for line in file:
            key=str(line.split('=')[0]).strip()
            value=str(line.split('=')[1]).strip()
            value=value.replace('\"','')
            eth0_data[key]= value
        if 'NETMASK' in eth0_data.keys() and 'PREFIX' not in eth0_data.keys():
            eth0_data['PREFIX']=exchange_intmask(eth0_data.get('NETMASK', ""))
        #不配置子网，默认24位
        if 'PREFIX' not in eth0_data.keys():
            eth0_data['PREFIX']=24
        result["date"]["ipAddress"] = eth0_data.get('IPADDR', "")
        result["date"]["subnetMask"] = exchange_maskint(int(eth0_data.get('PREFIX', "")))
        result["date"]["defaultGateway"] = eth0_data.get('GATEWAY', "")
        result["date"]["firstDnsServer"] = eth0_data.get('DNS1', "")
        result["date"]["spareDnsServer"] = eth0_data.get('DNS2', "")
        result["date"]["ipParagraphPrompt"] = kad_config.get('CLUSTER_CIDR', "")
        return  result
    except Exception as e:
        result["code"]=204
        result["message"]='get network message error: ' + str(e)
        logging.error('get network message error: ' + str(e))
        return  result

def edit_netfile(conf):
    try:
        file_data = ""
        cover_map = {'IPADDR':'ipAddress','GATEWAY':'defaultGateway','DNS1':'firstDnsServer','DNS2':'spareDnsServer','PREFIX':'subnetMask'}
        eth0_data = {}
        conf['subnetMask']=exchange_intmask(conf['subnetMask'])
        with open(api_config['networkfile'],"r") as file:
            for line in file:
                if('=' not in line):
                    continue
                key=str(line.split('=')[0])
                if( key in cover_map.keys()):
                    line = key +'=' +str(conf[cover_map[key]])+'\n'
                    del cover_map[key]
                file_data+=line
            for key in cover_map.keys():
                file_data = file_data + key +'='+str(conf[cover_map[key]])+'\n'
        with open(api_config['networkfile'],"w") as f:
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

    CA_FILE=api_config['CA_FILE']
    KEY_FILE=api_config['KEY_FILE']
    CERT_FILE=api_config['CERT_FILE']
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERT_FILE,keyfile=KEY_FILE)
    context.load_verify_locations(CA_FILE)
    context.verify_mode=ssl.CERT_REQUIRED

    server.run(host="0.0.0.0", port=api_config['port'], debug=True,ssl_context=context)

if __name__ == '__main__':
    main()
