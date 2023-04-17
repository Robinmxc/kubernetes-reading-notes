#!/bin/bash
# 配置项目
from_ip=${1}
from_password=${2} 
local_back_dir="/back_append_store"

# 默认的配置参数非特殊无需修改
enable_fdfs=true
enable_mongo=true
enable_pg=true
from_append_dir="back_append_store"
mkdir -p ${local_back_dir}
# 关键自动读取的参数，无需配置
from_mongo_user=""
from_mongo_password=""
from_mongo_ip=""
from_fdfs_password=${from_password}
from_fdfs_ip=""

function remote_ssh_command(){
	ip=${1} 
	password=${2}
	command=${3}
	sshpass -p ${password}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${ip} "${command}"
	# echo "执行命令：sshpass -p ${password}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${ip} \"${command}\""
}
# 全局固定配置
function config_from_process(){
	mkdir -p ${local_back_dir}/from

	sid_config_file=${local_back_dir}/from/souceid-all.yml
	k8s_config_file=${local_back_dir}/from/k8s-all.yml
	sshpass -p ${from_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${from_ip}:/opt/kad/workspace/ruijie-sourceid/conf/all.yml ${sid_config_file}
	sshpass -p ${from_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${from_ip}:/opt/kad/workspace/k8s/conf/all.yml  ${k8s_config_file}
	
	from_mongo_user=`cat ${sid_config_file} | grep MONGODB_ADMIN_USER |awk -F : '{printf $2}' `
	from_mongo_user=${from_mongo_user//\"/}
	from_mongo_password=`cat ${sid_config_file} | grep MONGODB_ADMIN_PWD |awk -F : '{printf $2}' `
	from_mongo_password=${from_mongo_password//\"/}
	
	kube_node_hosts=`cat ${k8s_config_file} | grep KUBE_NODE_HOSTS |awk -F : '{printf $2}' `
	kube_node_hosts=${kube_node_hosts//]/}
	kube_node_hosts=${kube_node_hosts//[/}
	node_hosts=(${kube_node_hosts//\,/ })
	if [[ ${#node_hosts[*]} == 1 ]];then
		from_mongo_ip=${node_hosts[0]};
	elif [[ ${#node_hosts[*]} > 1 ]];then
		from_mongo_ip=${node_hosts[0]};
	fi
	from_mongo_ip=${from_mongo_ip//\"/}
	fdfs_nodes=`cat ${k8s_config_file}  | grep FDFS_STORAGE_HOSTS |awk -F : '{printf $2}' `
	fdfs_nodes=${fdfs_nodes//]/}
	fdfs_nodes=${fdfs_nodes//[/}
	fdfs_nodes=${fdfs_nodes//\"/}
	node_fdfs_hosts=(${fdfs_nodes//\,/ })
	if [[ ${#node_fdfs_hosts[*]} == 1 ]];then
		from_fdfs_ip=${node_fdfs_hosts[0]};
	elif [[ ${#node_hosts[*]} > 1 ]];then
		from_fdfs_ip=${node_fdfs_hosts[0]};
	fi
}
config_from_process

function fdfs_back(){
 if [[ ${from_fdfs_ip} != "" ]];then
    echo "fastDfs数据库开始备份,服务器IP:${from_fdfs_ip}"
    mkdir -p ${local_back_dir}/from
    fdfs_storage_file=${local_back_dir}/from/storage.conf
	sshpass -p ${from_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${from_fdfs_ip}:/etc/fdfs/storage.conf ${fdfs_storage_file}
	if [  -f "$fdfs_storage_file" ]; then
		dirs_result=`cat ${fdfs_storage_file} | grep store_path0 |awk -F = '{printf $2}'`
		dirs=(${dirs_result//\// })
		max_dir=${dirs[0]}
		if [[ ${max_dir} == "ruijie" ]];then
			max_dir=""
		else
			max_dir="/${max_dir}"
		fi

		remote_back_dir="${max_dir}/${from_append_dir}"
		del_command="rm -rf ${remote_back_dir}}/fdfs_data_back.tar > /dev/null 2>&1"
		dir_create="mkdir -p ${remote_back_dir}";
		back_command="cd ${dirs_result}/data; tar  -zcvf ${remote_back_dir}/fdfs_data_back.tar *> /dev/null 2>&1";
		remote_ssh_command ${from_fdfs_ip} ${from_fdfs_password} "${del_command};${dir_create};${back_command};" 
		## 远程拷贝到本地目录，然后清空远程备份
		rm -r ${local_back_dir}/fdfs_data_back.tar  > /dev/null 2>&1
		mkdir -p ${local_back_dir} 
		sshpass -p ${from_fdfs_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${from_fdfs_ip}:${remote_back_dir}/fdfs_data_back.tar ${local_back_dir}
		remote_ssh_command ${from_fdfs_ip} ${from_fdfs_password} "${del_command};" 
	else
	     echo "fdfs未配置，不进行备份,服务器IP:${to_fdfs_ip},配置文件:${fdfs_storage_file}"
	fi

 fi
}

function mongo_back(){
 if [[ ${from_mongo_ip} != "" ]];then
  	echo "mongo数据库开始备份,服务器IP:${from_mongo_ip}"
  	mkdir -p ${local_back_dir}/from
  	config_file=${local_back_dir}/from/mongo-config.yml
	sshpass -p ${from_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${from_ip}:/etc/kad/config.yml ${config_file}
	max_dir_command=(`cat ${config_file} | grep DATA_DIR |awk -F : '{printf $2}' `)
	max_dir=${max_dir//\"/}
  	remote_back_dir="${max_dir}/${from_append_dir}"

 	del_command="rm -rf ${remote_back_dir}/mongodb* > /dev/null 2>&1"
    dir_create="mkdir -p ${remote_back_dir}/mongodb";
	back_command="mongodump -h ${from_mongo_ip} -u ${from_mongo_user} -p ${from_mongo_password} --authenticationDatabase 'admin'  -o ${remote_back_dir}/mongodb"
	tar_command="cd ${remote_back_dir}/mongodb;tar  -zcvf ${remote_back_dir}/mongodb.tar * > /dev/null 2>&1";
	remote_ssh_command ${from_mongo_ip} ${from_password} "${del_command};${dir_create};${back_command};${tar_command};" 
	
	rm -rf  ${local_back_dir}/mongodb.tar > /dev/null 2>&1
	mkdir -p ${local_back_dir}
	sshpass -p ${from_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${from_mongo_ip}:${remote_back_dir}/mongodb.tar ${local_back_dir}
	remote_ssh_command ${from_mongo_ip} ${from_password} "${del_command};" 
 fi
}
function pg_back(){
	  echo "postgres数据库开始备份,服务器IP:${from_ip}"
  	  config_file=${local_back_dir}/from/pg-config.yml
	  sshpass -p ${from_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${from_ip}:/etc/kad/config.yml ${config_file}
	  max_dir_command=(`cat ${config_file} | grep DATA_DIR |awk -F : '{printf $2}' `)
	  max_dir=${max_dir//\"/}
  	  remote_back_dir="${max_dir}/${from_append_dir}"
  	  
	  del_command="rm -rf ${remote_back_dir}/init.sql > /dev/null 2>&1"
	  dir_create="mkdir -p ${remote_back_dir}";
	  back_command="kubectl exec -n ruijie-sourceid postgresql-0 -- pg_dump -U postgres  quartz > ${remote_back_dir}/init.sql";
	  remote_ssh_command ${from_ip} ${from_password} "${del_command};${dir_create};${back_command};" 
	  rm -rf ${local_back_dir}/init.sql  > /dev/null 2>&1
	  mkdir -p ${local_back_dir}
	  sshpass -p ${from_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  root@${from_ip}:${remote_back_dir}/init.sql ${local_back_dir}
	  remote_ssh_command ${from_ip} ${from_password} "${del_command};" 
}
if [[ ${enable_mongo} == true ]] ;then
	mongo_back
fi
if [[ ${enable_pg} == true ]] ;then
	pg_back
fi
if [[ ${enable_fdfs} == true ]] ;then
	fdfs_back
fi
if [[ "$back_enable" == true  ]];then
	echo "备份完毕"
	
fi
