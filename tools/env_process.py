#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import json
import os
import subprocess
import sys
Py_version = sys.version_info
Py_v_info = str(Py_version.major) + '.' + str(Py_version.minor) + '.' + str(Py_version.micro)
if Py_version >= (3, 0):
    import importlib
output=subprocess.check_output("/opt/kad/inventory/kad-workspace.py --list", shell=True)
json_object = json.loads(output)
ssh_password=""
def python3_rpm(ip):
  output_uname= subprocess.check_output("uname -r", shell=True).decode("utf-8")
  output_uname=output_uname.replace("\n","")
  output_uname=output_uname.replace(" ","")
  try:
    if ".an8.x86_64" in output_uname  :
      try:
        version_command="sshpass -p "+ ssh_password+  " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"+ip+" \" python3 --version;\" "
        version_command_output = subprocess.check_output(version_command, shell=True).decode("utf-8")
      except Exception :
        print("远程安装python3:服务器IP="+ip+"")
        copy_command="sshpass -p "+ ssh_password+ " scp  -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /opt/kad/down/rpms/"+output_uname+"/python39 root@"+ip+":/tmp/python39 > /dev/null 2>&1"
        install_command="sshpass -p "+ ssh_password+  " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"+ip+" \"rpm -ivh  /tmp/python39/*.rpm --force --nodeps > /dev/null 2>&1;\" "
        copy_command_output = subprocess.check_output(copy_command, shell=True)
        install_command_output = subprocess.check_output(install_command, shell=True)
  except Exception :
        raise NameError("远程安装python3失败,请保证"+ip+"远程可用")

def rsyslog_rpm(ip):
  output_uname= subprocess.check_output("uname -r", shell=True).decode("utf-8")
  output_uname=output_uname.replace("\n","")
  output_uname=output_uname.replace(" ","")
  try:
    if ".an8.x86_64" in output_uname  :
      try:
        version_command="sshpass -p "+ ssh_password+  " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"+ip+" \"  ls /usr/sbin/rsyslogd \" "
        version_command_output = subprocess.check_output(version_command, shell=True).decode("utf-8")
      except Exception :
        print("远程安装rsyslog:服务器IP="+ip+"")
        copy_command="sshpass -p "+ ssh_password+ " scp  -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /opt/kad/down/rpms/"+output_uname+"/rsyslog root@"+ip+":/tmp/rsyslog > /dev/null 2>&1"
        install_command="sshpass -p "+ ssh_password+  " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"+ip+" \"rpm -ivh  /tmp/rsyslog/*.rpm --force --nodeps > /dev/null 2>&1;\" "
        copy_command_output = subprocess.check_output(copy_command, shell=True)
        install_command_output = subprocess.check_output(install_command, shell=True)
  except Exception :
        raise NameError("远程安装python3失败,请保证"+ip+"远程可用")  

def k8sProcess():
  if json_object["all"]["vars"]["KUBE_NODE_HOSTS"]:
    kube_nodes=json_object["all"]["vars"]["KUBE_NODE_HOSTS"]
    for item in kube_nodes:
      python3_rpm(item)
      rsyslog_rpm(item)
            
def ldapProcess():
  if json_object["all"]["vars"]["LDAP"]:
    ldap_mode=json_object["all"]["vars"]["LDAP"]["LDAP_MODE"]
    ldap_nodes=json_object["all"]["vars"]["LDAP"]["LDAP_HOST"]
    ldap_enable=json_object["all"]["vars"]["LDAP"]["enable"]
    if ldap_mode == "standalone" and ldap_enable:
      for item in ldap_nodes:
        python3_rpm(item)
        rsyslog_rpm(item)

def fdfsProcess():
  if json_object["all"]["vars"]["FDFS_MODE"]:
    fdfs_mode=json_object["all"]["vars"]["FDFS_MODE"]
    if fdfs_mode and fdfs_mode!="none":
      fdfs_nodes=json_object["all"]["vars"]["FDFS_STORAGE_HOSTS"]
      for item in fdfs_nodes:
        python3_rpm(item)
        rsyslog_rpm(item)

def eomsProcess():
  if json_object["all"]["vars"]["EOMS"]:
    eoms_enable=json_object["all"]["vars"]["EOMS"]["enable"]
    if eoms_enable:
      eoms_nodes=json_object["all"]["vars"]["EOMS"]["EOMS_STORAGE_HOST"]
      for item in eoms_nodes:
        python3_rpm(item)
        rsyslog_rpm(item)        
def main():
    if Py_version < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf8')
    else:
        importlib.reload(sys)
    global ssh_password
    ssh_password=sys.argv[1];  
    input=sys.argv[2];  
    if "ldap" in input:
      ldapProcess()
    elif "eoms" in input:
      eomsProcess()   
    elif "fdfs" in input:
      fdfsProcess()    
    else:
       k8sProcess()	
if __name__ == '__main__':
    main()
