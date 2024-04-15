#!/bin/bash
# 配置项目
username=${1:-root} 
password=${2} 
local_back_dir="/tmp/mongo/"
mkdir -p ${local_back_dir}
function remote_ssh_command(){
	ip=${1} 
	password=${2}
	command=${3}
	#echo "sshpass -p ${password}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${username}@${ip} \"${command}\""
	sshpass -p ${password}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${username}@${ip} "${command}"
}
function process(){
	rm -rf ${local_back_dir}/from
	mkdir -p ${local_back_dir}/from
	k8s_config_file=/opt/kad/workspace/k8s/conf/all.yml
	kube_node_hosts=`cat ${k8s_config_file} | grep KUBE_NODE_HOSTS |awk -F : '{printf $2}' `
	kube_node_hosts=${kube_node_hosts//]/}
	kube_node_hosts=${kube_node_hosts//[/}
	node_hosts=(${kube_node_hosts//\,/ })
	if [[ ${#node_hosts[*]} > 1 ]];then
		config_file=/etc/kad/config.yml
		max_dir=(`cat ${config_file} | grep DATA_DIR |awk -F : '{printf $2}' `)
		max_dir=${max_dir//\"/}
		del_command="rm -rf ruijie/ruijie-sourceid/mongodb/data/*> /dev/null 2>&1";
		remote_ssh_command ${node_hosts[2]//\"/} ${password} "${del_command};" 
		kubectl delete -f /opt/kad/workspace/ruijie-sourceid/yaml/mongo/mongo1.yml
		kubectl delete -f /opt/kad/workspace/ruijie-sourceid/yaml/mongo/mongo3.yml
		#echo "sshpass -p ${password} scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r ${username}@${node_hosts[0]//\"/}:${max_dir}/ruijie/ruijie-sourceid/mongodb/data/* ${username}@${node_hosts[2]//\"/}@${max_dir}/ruijie/ruijie-sourceid/mongodb/data/"
		sshpass -p ${password} scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r ${username}@${node_hosts[0]//\"/}:${max_dir}/ruijie/ruijie-sourceid/mongodb/data/* ${username}@${node_hosts[2]//\"/}:${max_dir}/ruijie/ruijie-sourceid/mongodb/data/
		rm -rf /tmp/mongo/status
		mkdir -p /tmp/mongo/
		touch /tmp/mongo/status
		echo "scp" > /tmp/mongo/status
		kubectl create -f /opt/kad/workspace/ruijie-sourceid/yaml/mongo/mongo1.yml
		kubectl create -f /opt/kad/workspace/ruijie-sourceid/yaml/mongo/mongo3.yml
		echo "修眠33s等待mongo启动完毕"
		echo "修眠结束，请手工执行 kubectl get pods -A 观察mongo状态 "
	else
		echo "非集群模式不支持PSS"
	fi
	
}
if	[[ "$username" == "" || "$password" == "" ]];then
	echo "请输入ssh账号和密码"
else
	process
fi

