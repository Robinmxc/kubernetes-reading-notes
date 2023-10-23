#!/bin/bash
osname=(`uname -r`)
result=$(echo $osname | grep ".el7.x86_64")
input=${1} 
ssh_user=${serverUser}
if	[[ "$result" == "" ]];then
    ssh_user=$(id -nu $SUDO_UID)
fi
ssh_port=$(grep -oP "(?<=Port ).*" /etc/ssh/sshd_config)
sed -i "s/^#*remote_port.*/remote_port = $ssh_port/"  /opt/kad/ansible.cfg
export PATH=$PATH:/usr/local/bin/
echo -n "SSH password: " 
read  -s ssh_password  
if	[[ "$result" != "" ]];then
 	 sshpass -p ${ssh_password}  ansible-playbook -i inventory/ -k $*  --become  --become-method  sudo --user ${ssh_user} --extra-vars "ansible_sudo_pass=${ssh_password}" 
else
    result_an8_oe2203=$(echo $osname | grep -E ".an8|.oe2203")
   
    if	[[ "$result_an8_oe2203" != "" ]];then
        chmod +777 ./tools/*.py
        set -o errexit
        ./tools/env_process.py "${ssh_user}" "${ssh_password}" "${ssh_port}" "${input}" 
        set +o errexit 
    fi	
    sshpass -p ${ssh_password}  ansible-playbook -i inventory/ -k $* -e 'ansible_python_interpreter=/usr/bin/python3' --become  --become-method  sudo --user ${ssh_user} --extra-vars "ansible_sudo_pass=${ssh_password}" 
fi