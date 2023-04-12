#!/bin/bash
# 配置项目
remote_ip=${1}
remote_passowrd=${2} 
back_enable=${3:-true} 
restore_enable=${4:-false} 
echo "备份开启标志:${back_enable},恢复开启标志:${restore_enable}"
# 关键自动读取的参数
remoute_mongo_user=""
remoute_mongo_password=""
remoute_mongo_ip=""

local_mongo_user=""
local_mongo_password=""
local_mongo_ip=""

remoute_fdfs_ip=""
local_fdfs_ip=""
remoute_fdfs_dir=""
local_fdfs_dir=""
local_fdfs_all=()
# 配置文件读取的配置项目
remote_max_dir=""
local_max_dir=""
remote_back_dir=""
local_back_dir=""
# 默认配置项目
enable_fdfs=true
enable_mongo=true
enable_pg=true
append_dir="back_append_store"
fdfs_password=${remote_passowrd}
echo "远程服务器${remote_ip},密码${remote_passowrd}机器相关的数据组件"
function config_local_process(){
	echo "自动获取本地配置"
	config_file=/etc/kad/config.yml
	sid_config_file=/opt/kad/workspace/ruijie-sourceid/conf/all.yml
	k8s_config_file=/opt/kad/workspace/k8s/conf/all.yml
	local_max_dir=(`cat ${config_file} | grep DATA_DIR |awk -F : '{printf $2}' `)
	local_max_dir=${local_max_dir//\"/}
	local_back_dir="${local_max_dir}/${append_dir}"
	local_mongo_user=(`cat ${sid_config_file} | grep MONGODB_ADMIN_USER |awk -F : '{printf $2}' `)
	local_mongo_user=${local_mongo_user//\"/}
	local_mongo_password=(`cat  ${sid_config_file} | grep MONGODB_ADMIN_PWD |awk -F : '{printf $2}' `)
	local_mongo_password=${local_mongo_password//\"/}

	kube_node_hosts=(`cat  ${k8s_config_file} | grep KUBE_NODE_HOSTS |awk -F : '{printf $2}' `)
	kube_node_hosts=${kube_node_hosts//]/}
	kube_node_hosts=${kube_node_hosts//[/}
	node_hosts=(${kube_node_hosts//\,/ })
	if [[ ${#node_hosts[*]} == 1 ]];then
		local_mongo_ip=${node_hosts[0]};
	elif [[ ${#node_hosts[*]} > 1 ]];then
		local_mongo_ip=${node_hosts[1]};
	fi
	local_mongo_ip=${local_mongo_ip//\"/}
	local_fdfs_dir="${local_max_dir}/ruijie/fdfs/storage/data"
	
	fdfs_nodes=(`cat ${k8s_config_file} | grep FDFS_STORAGE_HOSTS |awk -F : '{printf $2}' `)

	fdfs_nodes=${fdfs_nodes//]/}
	fdfs_nodes=${fdfs_nodes//[/}
	fdfs_nodes=${fdfs_nodes//\"/}
	node_fdfs_hosts=(${fdfs_nodes//\,/ })
	if [[ ${#node_fdfs_hosts[*]} == 1 ]];then
		local_fdfs_ip=${node_fdfs_hosts[0]};
	elif [[ ${#node_hosts[*]} > 1 ]];then
		local_fdfs_ip=${node_fdfs_hosts[1]};
	fi
	local_fdfs_all=(${node_fdfs_hosts[@]}) 
}
function config_remote_process(){
	echo "自动获取远程配置"
	config_file=${local_back_dir}/config.yml
	sid_config_file=${local_back_dir}/souceid-all.yml
	k8s_config_file=${local_back_dir}/k8s-all.yml
	sshpass -p ${remote_passowrd}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${remote_ip}:/etc/kad/config.yml ${config_file}
	sshpass -p ${remote_passowrd}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${remote_ip}:/opt/kad/workspace/ruijie-sourceid/conf/all.yml ${sid_config_file}
	sshpass -p ${remote_passowrd}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${remote_ip}:/opt/kad/workspace/k8s/conf/all.yml  ${k8s_config_file}
	remote_max_dir=(`cat ${config_file} | grep DATA_DIR |awk -F : '{printf $2}' `)
	remote_max_dir=${remote_max_dir//\"/}
	remote_back_dir="${remote_max_dir}/${append_dir}"
	
	remoute_mongo_user=(`cat ${sid_config_file} | grep MONGODB_ADMIN_USER |awk -F : '{printf $2}' `)
	remoute_mongo_user=${remoute_mongo_user//\"/}
	remoute_mongo_password=(`cat ${sid_config_file} | grep MONGODB_ADMIN_PWD |awk -F : '{printf $2}' `)
	remoute_mongo_password=${remoute_mongo_password//\"/}
	
	kube_node_hosts=(`cat  ${k8s_config_file} | grep KUBE_NODE_HOSTS |awk -F : '{printf $2}' `)
	kube_node_hosts=${kube_node_hosts//]/}
	kube_node_hosts=${kube_node_hosts//[/}
	node_hosts=(${kube_node_hosts//\,/ })
	if [[ ${#node_hosts[*]} == 1 ]];then
		remoute_mongo_ip=${node_hosts[0]};
	elif [[ ${#node_hosts[*]} > 1 ]];then
		remoute_mongo_ip=${node_hosts[1]};
	fi
	remoute_mongo_ip=${remoute_mongo_ip//\"/}
	remoute_fdfs_dir="${remote_max_dir}/ruijie/fdfs/storage/data"
	fdfs_nodes=(`cat ${k8s_config_file} | grep FDFS_STORAGE_HOSTS |awk -F : '{printf $2}' `)
	fdfs_nodes=${fdfs_nodes//]/}
	fdfs_nodes=${fdfs_nodes//[/}
	fdfs_nodes=${fdfs_nodes//\"/}
	node_fdfs_hosts=(${fdfs_nodes//\,/ })
	if [[ ${#node_fdfs_hosts[*]} == 1 ]];then
		remoute_fdfs_ip=${node_fdfs_hosts[0]};
	elif [[ ${#node_hosts[*]} > 1 ]];then
		remoute_fdfs_ip=${node_fdfs_hosts[1]};
	fi
	
}
config_local_process
config_remote_process


function fdfs_back(){
 if [[ ${remoute_fdfs_ip} != "" ]];then
  	echo "fastDfs数据库开始备份"
     del_command="rm -rf ${remote_back_dir}/fdfs_data_back.tar > /dev/null 2>&1"
     dir_create="mkdir -p ${remote_back_dir}";
     back_command="tar  -zcvf ${remote_back_dir}/fdfs_data_back.tar ${remoute_fdfs_dir}> /dev/null 2>&1";
	sshpass -p ${fdfs_password}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${remoute_fdfs_ip} "${del_command};${dir_create};${back_command};"  
	
	rm -r ${local_back_dir}/fdfs_data_back.tar  > /dev/null 2>&1
	mkdir -p ${local_back_dir} 
	sshpass -p ${fdfs_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${remoute_fdfs_ip}:${remote_back_dir}/fdfs_data_back.tar ${local_back_dir}
	sshpass -p ${fdfs_password}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${remoute_fdfs_ip} "${del_command};"  
 fi
}


function mongo_back(){
 if [[ ${remoute_mongo_ip} != "" ]];then
  	echo "mongo数据库开始备份"
  	iptables_command="iptables -F";
  	
	sshpass -p ${remote_passowrd}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${remoute_mongo_ip} "${iptables_command};"  
 	rm -rf ${local_back_dir}/mongodb
 	mkdir -p ${local_back_dir}/mongodb
 	echo "执行mongo数据库备份命令:mongodump -h ${remoute_mongo_ip} -u ${remoute_mongo_user} -p ${remoute_mongo_password} --authenticationDatabase 'admin' -o ${local_back_dir}/mongodb > /dev/null 2>&1 "
 	mongodump -h ${remoute_mongo_ip} -u ${remoute_mongo_user} -p ${remoute_mongo_password} --authenticationDatabase 'admin' -o ${local_back_dir}/mongodb > /dev/null 2>&1
 fi
}
function pg_back(){
  echo "postgres数据库开始备份"
  del_command="rm -rf ${remote_back_dir}/init.sql > /dev/null 2>&1"
  dir_create="mkdir -p ${remote_back_dir}";
  back_command="kubectl exec -n ruijie-sourceid postgresql-0 -- pg_dump -U postgres  quartz > ${remote_back_dir}/init.sql";
  echo "执行postgres数据库备份命令:sshpass -p ${remote_passowrd}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${remote_ip} \"${del_command};${dir_create};${back_command};\" "
  sshpass -p ${remote_passowrd}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${remote_ip} "${del_command};${dir_create};${back_command};" 
  rm -rf ${local_back_dir}/init.sql  > /dev/null 2>&1
  mkdir -p ${local_back_dir}
  sshpass -p ${remote_passowrd}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  root@${remote_ip}:${remote_back_dir}/init.sql ${local_back_dir}
  
}
if [[ ${enable_mongo} == true ]] && [[ "$back_enable" == true  ]];then
	mongo_back
fi
if [[ ${enable_pg} == true ]] && [[ "$back_enable" == true  ]];then
	pg_back
fi
if [[ ${enable_fdfs} == true ]] && [[ "$back_enable" == true  ]];then
	fdfs_back
fi
if [[ "$back_enable" == true  ]];then
	echo "备份完毕"
	
fi
function mongo_restore(){
  echo "mongo数据库开始恢复,恢复命令: mongorestore -h ${remoute_mongo_ip} -u ${remoute_mongo_user} -p ${remoute_mongo_password} --authenticationDatabase 'admin' --drop ${local_back_dir}/mongodb > /dev/null 2>&1"
  mongorestore -h ${remoute_mongo_ip} -u ${remoute_mongo_user} -p ${remoute_mongo_password} --authenticationDatabase 'admin' --drop ${local_back_dir}/mongodb > /dev/null 2>&1
}
function pg_restore(){
  echo "pg数据库开始恢复，执行命令:kubectl exec -n ruijie-sourceid postgresql-0 -- psql -U postgres -d quartz -f ${local_back_dir}/init.sql"
  kubectl cp ${local_back_dir}/init.sql -n ruijie-sourceid  -c  postgresql  postgresql-0:/
  kubectl exec -n ruijie-sourceid postgresql-0 -- psql -U postgres -d quartz -f /init.sql > /dev/null 2>&1
}
function fdfs_restore(){
	echo "fdfs数据库开始恢复"
	for var in ${local_fdfs_all[@]};
	do
		
		del_command="rm -rf ${local_back_dir}/fdfs_data_back.tar > /dev/null 2>&1"
	     dir_create="mkdir -p ${local_back_dir}";
		sshpass -p ${fdfs_password}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${var} "${del_command};${dir_create};"  
		sshpass -p ${fdfs_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${local_back_dir}/fdfs_data_back.tar root@${var}:${local_back_dir} 
		restore_command="systemctl stop fdfs_storaged;rm -rf ${local_fdfs_dir}; tar -xvf ${local_back_dir}/fdfs_data_back.tar -C ${local_back_dir};systemctl start fdfs_storaged;";
		echo "fdfs数据库${var}开始恢复，恢复命令:sshpass -p ${fdfs_password}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${var} "${restore_command}"   > /dev/null 2>&1"	
		sshpass -p ${fdfs_password}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${var} "${restore_command}"   > /dev/null 2>&1
	done
}
if [[ ${enable_mongo} == true ]] && [[ "$restore_enable" == true  ]];then
	mongo_restore
fi
if [[ ${enable_pg} == true ]] && [[ "$restore_enable" == true  ]];then
	pg_restore
fi
if [[ ${enable_fdfs} == true ]] && [[ "$restore_enable" == true  ]];then
	fdfs_restore
fi
if [[ "$restore_enable" == true  ]];then
	echo "还原完毕"
fi