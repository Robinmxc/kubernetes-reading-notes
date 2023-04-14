#!/bin/bash
# 配置项目
to_ip=${1}
to_password=${2} 
local_back_dir="/back_append_store"

# 默认的配置参数非特殊无需修改
enable_fdfs=true
enable_mongo=true
enable_pg=true
to_append_dir="restore_append_store"
mkdir -p ${local_back_dir}
# 关键自动读取的参数，无需配置
to_mongo_user=""
to_mongo_password=""
to_mongo_ip=""
to_fdfs_password=${to_password}
to_fdfs_ip=""

function remote_ssh_command(){
	ip=${1} 
	password=${2}
	command=${3}
	sshpass -p ${password}  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${ip} "${command}"
}
# 全局固定配置
function config_to_process(){
	mkdir -p ${local_back_dir}/to

	sid_config_file=${local_back_dir}/to/souceid-all.yml
	k8s_config_file=${local_back_dir}/to/k8s-all.yml
	sshpass -p ${to_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${to_ip}:/opt/kad/workspace/ruijie-sourceid/conf/all.yml ${sid_config_file}
	sshpass -p ${to_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${to_ip}:/opt/kad/workspace/k8s/conf/all.yml  ${k8s_config_file}
	
	to_mongo_user=`cat ${sid_config_file} | grep MONGODB_ADMIN_USER |awk -F : '{printf $2}' `
	to_mongo_user=${to_mongo_user//\"/}
	to_mongo_password=`cat ${sid_config_file} | grep MONGODB_ADMIN_PWD |awk -F : '{printf $2}' `
	to_mongo_password=${to_mongo_password//\"/}
	
	kube_node_hosts=`cat ${k8s_config_file} | grep KUBE_NODE_HOSTS |awk -F : '{printf $2}' `
	kube_node_hosts=${kube_node_hosts//]/}
	kube_node_hosts=${kube_node_hosts//[/}
	node_hosts=(${kube_node_hosts//\,/ })
	if [[ ${#node_hosts[*]} == 1 ]];then
		to_mongo_ip=${node_hosts[0]};
	elif [[ ${#node_hosts[*]} > 1 ]];then
		to_mongo_ip=${node_hosts[0]};
	fi
	to_mongo_ip=${to_mongo_ip//\"/}
	fdfs_nodes=`cat ${k8s_config_file}  | grep FDFS_STORAGE_HOSTS |awk -F : '{printf $2}' `
	fdfs_nodes=${fdfs_nodes//]/}
	fdfs_nodes=${fdfs_nodes//[/}
	fdfs_nodes=${fdfs_nodes//\"/}
	node_fdfs_hosts=(${fdfs_nodes//\,/ })
}
config_to_process

function fdfs_restore(){

  for to_fdfs_ip in ${node_fdfs_hosts[@]};
  do
    echo "fdfs数据库开始恢复,服务器IP:${to_fdfs_ip}"
    mkdir -p ${local_back_dir}/to
    fdfs_storage_file=${local_back_dir}/to/storage.conf
	
	sshpass -p ${to_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${to_fdfs_ip}:/etc/fdfs/storage.conf ${fdfs_storage_file}
    dirs_result=`cat ${fdfs_storage_file} | grep store_path0 |awk -F = '{printf $2}'`
    dirs=(${dirs_result//\// })
    max_dir=${dirs[0]}
    if [[ ${max_dir} == "ruijie" ]];then
		max_dir=""
    else
		max_dir="/${max_dir}"
    fi
	remote_back_dir="${max_dir}/${to_append_dir}"


    del_command="rm -rf ${remote_back_dir}/fdfs_data_back.tar > /dev/null 2>&1"
    dir_create="mkdir -p ${remote_back_dir}";
    remote_ssh_command ${to_fdfs_ip} ${to_fdfs_password} "${del_command};${dir_create};systemctl stop fdfs_storaged;" 
	sshpass -p ${to_fdfs_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${local_back_dir}/fdfs_data_back.tar root@${to_fdfs_ip}:${remote_back_dir}
	restore_command="rm -rf  ${dirs_result}/data/*;tar  -xvf ${remote_back_dir}/fdfs_data_back.tar -C ${dirs_result}/data> /dev/null 2>&1";
	remote_ssh_command ${to_fdfs_ip} ${to_fdfs_password} "${restore_command};${del_command};systemctl start fdfs_storaged;" 
  done
}

function mongo_restore(){
 if [[ ${to_mongo_ip} != "" ]];then
  	echo "mongo数据库开始恢复,服务器IP:${to_mongo_ip}"
  	mkdir -p ${local_back_dir}/to
  	config_file=${local_back_dir}/to/mongo-config.yml
	sshpass -p ${to_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${to_mongo_ip}:/etc/kad/config.yml ${config_file}
	max_dir_command=(`cat ${config_file} | grep DATA_DIR |awk -F : '{printf $2}' `)
	max_dir=${max_dir//\"/}
  	remote_back_dir="${max_dir}/${to_append_dir}"

 	del_command="rm -rf ${remote_back_dir}/mongodb* > /dev/null 2>&1"
    dir_create="mkdir -p ${remote_back_dir}/mongodb";
	remote_ssh_command ${to_mongo_ip} ${to_password} "${del_command};${dir_create};" 
	sshpass -p ${to_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${local_back_dir}/mongodb.tar root@${to_mongo_ip}:${remote_back_dir}
	
	tar_command="tar  -xvf ${remote_back_dir}/mongodb.tar -C ${remote_back_dir}/mongodb > /dev/null 2>&1";
	restore_command="mongorestore -h ${to_mongo_ip} -u ${to_mongo_user} -p ${to_mongo_password} --authenticationDatabase 'admin' --drop ${remote_back_dir}/mongodb"
	remote_ssh_command ${to_mongo_ip} ${to_password} "${tar_command};${restore_command};${del_command};" 
 fi
}
function pg_restore(){
	  echo "postgres数据库开始恢复,服务器IP:${to_ip}"
  	  config_file=${local_back_dir}/to/pg-config.yml
	  sshpass -p ${to_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${to_ip}:/etc/kad/config.yml ${config_file}
	  max_dir_command=(`cat ${config_file} | grep DATA_DIR |awk -F : '{printf $2}' `)
	  max_dir=${max_dir//\"/}
  	  remote_back_dir="${max_dir}/${to_append_dir}"

	  del_command="rm -rf ${remote_back_dir}/init.sql > /dev/null 2>&1"
	  dir_create="mkdir -p ${remote_back_dir}";
	  remote_ssh_command ${to_ip} ${to_password} "${del_command};${dir_create};" 
	  sshpass -p ${to_password}  scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${local_back_dir}/init.sql root@${to_ip}:${remote_back_dir}
 	  
	  kube_cp="kubectl cp ${remote_back_dir}/init.sql -n ruijie-sourceid  -c  postgresql  postgresql-0:/"
  	  restore_command="kubectl exec -n ruijie-sourceid postgresql-0 -- psql -U postgres -d quartz -f /init.sql > /dev/null 2>&1"
	  remote_ssh_command ${to_ip} ${to_password} "${kube_cp};${restore_command};${del_command};" 
}
if [[ ${enable_mongo} == true ]] ;then
	mongo_restore
fi
if [[ ${enable_pg} == true ]] ;then
	pg_restore
fi
if [[ ${enable_fdfs} == true ]] ;then
	fdfs_restore
fi
if [[ "$back_enable" == true  ]];then
	echo "恢复完毕"
	
fi
