#!/bin/bash
osname=(`uname -r`)
result=$(echo $osname | grep ".el7.x86_64")
input=${1} 
ssh_user=${serverUser}
if	[[ "$ssh_user" == "" ]];then
    ssh_user=$(id -nu $SUDO_UID)
fi
RED='\033[0;31m'
NC='\033[0m' # 恢复默认颜色
who=`whoami`
if [[ ${who} != "root" ]];then
	  set -e
    echo -e "${RED}当前登录用户:${ssh_user},需要sudo -i后执行安装${NC}"
		set +e
    exit 1
fi
ssh_port=$(grep -oP "(?<=Port ).*" /etc/ssh/sshd_config)
sed -i "s/^#*remote_port.*/remote_port = $ssh_port/"  /opt/kad/ansible.cfg
export PATH=$PATH:/usr/local/bin/
if [[ ${ssh_password} == "" ]];then
    echo -n "SSH password: " 
    read  -s ssh_password  
fi 
if	[[ "$result" != "" ]];then
 	 sshpass -p ${ssh_password}  ansible-playbook -i inventory/ -k $*  --become  --become-method  sudo --user ${ssh_user} --extra-vars "ansible_sudo_pass=${ssh_password}" 
else
    result_an8_oe2203_ky10=$(echo $osname | grep -E ".an8|.oe2203|.ky10")
    result_ky10=$(echo $osname | grep -E ".ky10")
    if	[[ "$result_ky10" != "" ]];then
          sed -i '1s/.*/#!\/usr\/bin\/python39/'  /opt/kad/tools/env_process.py 
          sed -i '1s/.*/#!\/usr\/bin\/python39/'  /opt/kad/inventory/kad-workspace.py
    fi
    if	[[ "$result_an8_oe2203_ky10" != "" ]];then
        chmod +777 ./tools/*.py
        set -o errexit
        ./tools/env_process.py "${ssh_user}" "${ssh_password}" "${ssh_port}" "${input}" 
        set +o errexit 
    fi	
    if	[[ "$result_ky10" != "" ]];then
   	  sshpass -p ${ssh_password}  ansible-playbook -i inventory/ -k $* -e 'ansible_python_interpreter=/usr/bin/python39' --become  --become-method  sudo --user ${ssh_user} --extra-vars "ansible_sudo_pass=${ssh_password}" 
    else
       sshpass -p ${ssh_password}  ansible-playbook -i inventory/ -k $* -e 'ansible_python_interpreter=/usr/bin/python3' --become  --become-method  sudo --user ${ssh_user} --extra-vars "ansible_sudo_pass=${ssh_password}" 
    fi

fi