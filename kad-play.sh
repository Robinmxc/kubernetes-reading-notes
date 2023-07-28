#!/bin/bash
osname=(`uname -r`)
result=$(echo $osname | grep ".el7.x86_64")
input=${1} 
if	[[ "$result" != "" ]];then
 	ansible-playbook -i inventory/ -k $* 
else
    result_an8_oe2203=$(echo $osname | grep -E ".an8|.oe2203")
    echo -n "SSH password: " 
    read  -s ssh_password  
    if	[[ "$result_an8_oe2203" != "" ]];then
        chmod +777 ./tools/*.py
        set -o errexit
        ./tools/env_process.py "${ssh_password}" "${input}"
        set +o errexit 
    fi	
    sshpass -p ${ssh_password}  ansible-playbook -i inventory/ -k $* -e 'ansible_python_interpreter=/usr/bin/python3'
fi
