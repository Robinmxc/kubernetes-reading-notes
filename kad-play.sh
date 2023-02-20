#!/bin/bash
osname=(`uname -r`)
result=$(echo $osname | grep ".el7.x86_64")
if	[[ "$result" != "" ]];then
 	ansible-playbook -i inventory/ -k $* 
else
    ansible-playbook -i inventory/ -k $* -e 'ansible_python_interpreter=/usr/bin/python3'
fi
