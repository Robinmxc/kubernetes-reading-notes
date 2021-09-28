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
import pymongo
from threading import Thread

server = flask.Flask(__name__)  # 把app.python文件当做一个server

def read_yml(file_path):
    file = open(file_path)
    config = yaml.load(file, Loader=yaml.SafeLoader)
    file.close()
    return config

api_config=read_yml('/etc/kad/api/kadapi.yaml')
kad_config=read_yml('/opt/kad/workspace/ruijie-smpplus/conf/all.yml')
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
    if not is_ip(data['ipAddress']) and not is_ip(data['firstDnsServer']):
        result["result"]=False
        result["code"]=204
        result["message"]='Parameter illegal'
        return result

    t=Thread(target=changeip_thread,args=(data,))
    t.start()
    return result


def changeip_thread(data):
    old_ip=prase_netfile()["date"]["ipAddress"]
    new_ip=data["ipAddress"]

    
    file_list=api_config['filelist']
    for filepath in file_list:
        os.system('sed -i "s/'+old_ip+'/' + new_ip + '/g" '+ filepath)
    os.system('sh /etc/kad/api/changeip.sh '+old_ip+' ' +new_ip )
    change_mongoip=False
    while change_mongoip:
        try:
            myclient = pymongo.MongoClient('mongodb://{}:{}@{}:{}/?authSource={}'.format("admin",kad_config["MONGODB_ADMIN_PWD"],new_ip,27017,"admin"))
            myclient.get_database('').command('rs.conf()')
            change_mongoip=True
        except Exception as e:
            change_mongoip=False
            time.sleep(5)
            print(e)


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
            eth0_data[str(line.split('=')[0])]= str(line.split('=')[1]).strip()
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
        return  result

def exchange_maskint(mask_int):
  bin_arr = ['0' for i in range(32)]
  for i in range(mask_int):
    bin_arr[i] = '1'
  tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
  tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
  return '.'.join(tmpmask)

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
