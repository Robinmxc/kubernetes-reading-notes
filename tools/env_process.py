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
ssh_user="root"
ssh_port=22
def python3_rpm(ip):
  sudo="echo "+ssh_password+" | sudo -S "
  output_uname= subprocess.check_output("uname -r", shell=True).decode("utf-8")
  output_uname=output_uname.replace("\n","")
  output_uname=output_uname.replace(" ","")
  try:
    if ".an8" in output_uname or  ".oe2203" in output_uname:
      try:
        version_command="sshpass -p "+ ssh_password+  " ssh -p "+ssh_port+" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "+ssh_user+"@"+ip+" \" "+sudo+"python3 --version;\" "
        version_command_output = subprocess.check_output(version_command, shell=True).decode("utf-8")
      except Exception :
        print("远程安装python3:服务器IP="+ip+"")
        copy_command="sshpass -p "+ ssh_password+ " scp  -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /opt/kad/down/rpms/"+output_uname+"/python39 "+ssh_user+"@"+ip+":/tmp/python39 > /dev/null 2>&1"
        install_command="sshpass -p "+ ssh_password+  " ssh -p "+ssh_port+" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "+ssh_user+"@"+ip+" \""+sudo+"rpm -ivh  /tmp/python39/*.rpm --force --nodeps > /dev/null 2>&1;\" "
        copy_command_output = subprocess.check_output(copy_command, shell=True)
        install_command_output = subprocess.check_output(install_command, shell=True)
    if  ".ky10" in output_uname:
      try:
        version_command="sshpass -p "+ ssh_password+  " ssh -p "+ssh_port+" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "+ssh_user+"@"+ip+" \" "+sudo+"/usr/bin/python39 --version;\" "
        version_command_output = subprocess.check_output(version_command, shell=True).decode("utf-8")
      except Exception :
        print("远程安装python3:服务器IP="+ip+"")
        del_command="sshpass -p "+ ssh_password+  " ssh -p "+ssh_port+" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "+ssh_user+"@"+ip+" \""+sudo+" rm -rf /usr/bin/python39;"+sudo+"rm -rf /usr/bin/pip3;"+sudo+"rm -rf /usr/local/python3;"+sudo+"mkdir -p /usr/local/python3 > /dev/null 2>&1;\" "
        del_command_output= subprocess.check_output(del_command, shell=True)   
        copy_command="sshpass -p "+ ssh_password+ " scp  -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /opt/kad/down/rpms/"+output_uname+"/python39/* "+ssh_user+"@"+ip+":/tmp/ > /dev/null 2>&1"
        copy_command_output = subprocess.check_output(copy_command, shell=True)   
        install_command="sshpass -p "+ ssh_password+  " ssh -p "+ssh_port+" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "+ssh_user+"@"+ip+" \""+sudo+"tar -xvf /tmp/python3.tar -C /usr/local/python3;"+sudo+"cp /usr/local/python3/bin/python3.9 /usr/bin/python39;	"+sudo+"cp /usr/local/python3/bin/pip3 /usr/bin/pip3;\" "
        install_command_output = subprocess.check_output(install_command, shell=True)   
  except Exception :
        raise NameError("远程安装python3失败,请保证"+ip+"远程可用")

def tar_rpm(ip):
  sudo="echo "+ssh_password+" | sudo -S "
  output_uname= subprocess.check_output("uname -r", shell=True).decode("utf-8")
  output_uname=output_uname.replace("\n","")
  output_uname=output_uname.replace(" ","")
  try:
    if ".an8" in output_uname or  ".oe2203" in output_uname :
      try:
        version_command="sshpass -p "+ ssh_password+  " ssh -p "+ssh_port+" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "+ssh_user+"@"+ip+" \" "+sudo+"tar --version;\" "
        version_command_output = subprocess.check_output(version_command, shell=True).decode("utf-8")
      except Exception :
        print("tar:服务器IP="+ip+"")
        copy_command="sshpass -p "+ ssh_password+ " scp  -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /opt/kad/down/rpms/"+output_uname+"/tar "+ssh_user+"@"+ip+":/tmp/tar > /dev/null 2>&1"
        install_command="sshpass -p "+ ssh_password+  " ssh -p "+ssh_port+" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "+ssh_user+"@"+ip+" \""+sudo+"rpm -ivh  /tmp/tar/*.rpm --force --nodeps > /dev/null 2>&1;\" "
        copy_command_output = subprocess.check_output(copy_command, shell=True)
        install_command_output = subprocess.check_output(install_command, shell=True)
  except Exception :
        raise NameError("远程安装python3失败,请保证"+ip+"远程可用")

def rsyslog_rpm(ip):
  sudo="echo "+ssh_password+" | sudo -S "
  output_uname= subprocess.check_output("uname -r", shell=True).decode("utf-8")
  output_uname=output_uname.replace("\n","")
  output_uname=output_uname.replace(" ","")
  try:
    if ".an8" in output_uname or  ".oe2203" in output_uname:
      try:
        version_command="sshpass -p "+ ssh_password+  " ssh -p "+ssh_port+" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "+ssh_user+"@"+ip+" \"  "+sudo+"ls /usr/sbin/rsyslogd \" "
        version_command_output = subprocess.check_output(version_command, shell=True).decode("utf-8")
      except Exception :
        print("远程安装rsyslog:服务器IP="+ip+"")
        copy_command="sshpass -p "+ ssh_password+ " scp  -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /opt/kad/down/rpms/"+output_uname+"/rsyslog "+ssh_user+"@"+ip+":/tmp/rsyslog > /dev/null 2>&1"
        install_command="sshpass -p "+ ssh_password+  " ssh -p "+ssh_port+" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "+ssh_user+"@"+ip+" \""+sudo+"rpm -ivh  /tmp/rsyslog/*.rpm --force --nodeps > /dev/null 2>&1;\" "
        copy_command_output = subprocess.check_output(copy_command, shell=True)
        install_command_output = subprocess.check_output(install_command, shell=True)
  except Exception :
        raise NameError("远程安装python3失败,请保证"+ip+"远程可用")  

def k8sProcess():
  if json_object["all"]["vars"]["KUBE_NODE_HOSTS"]:
    kube_nodes=json_object["all"]["vars"]["KUBE_NODE_HOSTS"]
    for item in kube_nodes:
      tar_rpm(item)      
      python3_rpm(item)
      rsyslog_rpm(item)
            
def ldapProcess():
  if json_object["all"]["vars"]["LDAP"]:
    ldap_mode=json_object["all"]["vars"]["LDAP"]["LDAP_MODE"]
    ldap_nodes=json_object["all"]["vars"]["LDAP"]["LDAP_HOST"]
    ldap_enable=json_object["all"]["vars"]["LDAP"]["enable"]
    if ldap_mode == "standalone" and ldap_enable:
      for item in ldap_nodes:
        tar_rpm(item)       
        python3_rpm(item)
        rsyslog_rpm(item)

def fdfsProcess():
  if json_object["all"]["vars"]["FDFS_MODE"]:
    fdfs_mode=json_object["all"]["vars"]["FDFS_MODE"]
    if fdfs_mode and fdfs_mode!="none":
      fdfs_nodes=json_object["all"]["vars"]["FDFS_STORAGE_HOSTS"]
      for item in fdfs_nodes:
        tar_rpm(item)
        python3_rpm(item)
        rsyslog_rpm(item)

def eomsProcess():
  if json_object["all"]["vars"]["EOMS"]:
    eoms_enable=json_object["all"]["vars"]["EOMS"]["enable"]
    if eoms_enable:
      eoms_nodes=json_object["all"]["vars"]["EOMS"]["EOMS_STORAGE_HOST"]
      for item in eoms_nodes:
        tar_rpm(item)        
        python3_rpm(item)
        rsyslog_rpm(item)        
def main():
    if Py_version < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf8')
    else:
        importlib.reload(sys)
    global ssh_password
    global ssh_user
    global ssh_port
    ssh_user=sys.argv[1];  
    ssh_password=sys.argv[2];  
    ssh_port=sys.argv[3];  
    input=sys.argv[4];  
    if "ldap" in input:
      ldapProcess()
    elif "eoms" in input:
      eomsProcess()   
    elif "fdfs" in input:
      fdfsProcess()    
    else:
      ldapProcess()
      eomsProcess()
      fdfsProcess()
      k8sProcess()	
if __name__ == '__main__':
    main()
