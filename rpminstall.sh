#!/bin/bash
if [  -f "./rpminstall.sh" ];then
	cp -r ./rpminstall.sh /opt/kad/down/rpms
fi
yum remove -y python3  > /dev/null 2>&1
mode=${1:-3} 
needExec=${2:-"True"} 
osname=(`uname -r`)
mkdir -p /opt/kad/down/rpms/${osname}
cd /opt/kad/down/rpms/${osname}
function rpmOperator(){
	var=${1} 
	echo "rpmOperator call ${var}"
	if [[ ${mode} == 1 || ${mode} == 3 ]];then
		yum remove -y $var > /dev/null 2>&1
		rm -rf  $var 
		mkdir $var
		cd $var
		dnf download $var --resolve
		cd ..
	fi
	if [[ ${mode} == 2 || ${mode} == 3 ]]; then
			rpm -ivh ./$var/*.rpm --force --nodeps
	fi	
}
function pipOperator(){
	var=${1} 
	echo "pipOperator call ${var}"
	if [[ ${mode} == 1 || ${mode} == 3 ]];then
		pip3 uninstall -y $var > /dev/null 2>&1
		rm -rf $var
		pip3 download -d $var  $var -i   https://pypi.douban.com/simple/
	fi
	if [[ ${mode} == 2 || ${mode} == 3 ]];then
		pip3 install  ./$var/*.whl
	fi	

}
function mongo_tool(){
	echo "mongo_tool call"
	if [[ ${mode} == 1 || ${mode} == 3 ]];then
		yum remove -y mongodb-database-tools > /dev/null 2>&1
		rm -rf   mongodb-database-tools
		mkdir  mongodb-database-tools
		cd mongodb-database-tools
		wget https://fastdl.mongodb.org/tools/db/mongodb-database-tools-rhel80-x86_64-100.6.1.rpm
		cd ..
		yum install --allowerasing -y ./mongodb-database-tools/mongodb-database-tools-rhel80-x86_64-100.6.1.rpm --downloadonly  --downloaddir=./mongodb-database-tools
	fi
	if [[ ${mode} == 2 || ${mode} == 3 ]]; then
			rpm -ivh ./mongodb-database-tools/*.rpm
	fi	
}
function commonInstall(){
	echo "commonInstall call"
	if [[ ${mode} == 1 || ${mode} == 3 ]];then
		yum -y install yum-utils 
		yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
		#yum -y copr enable copart/restic 
	fi
	echo "参数1：仅下载用于制造离线包 2：仅安装用于现场  3:下载并安装（特定场景） 当前参数${mode}"
	rpms=(tar git python39 sshpass  wget unzip tcpdump net-tools ipset ipvsadm tcl bash-completion jq rsyslog oniguruma polkit psmisc rsync socat  make  nfs-utils cyrus-sasl epel-release)
	for var in ${rpms[@]};
	do
		rpmOperator $var
	done
	cp -r /usr/bin/pip3 /usr/local/bin/pip3
	pip3s=(ansible)
	for var in ${pip3s[@]};
	do
		pipOperator $var
	done

cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF
}	
function kubernetes_process(){
	echo "kubernetes_process call"
	if [[ ${mode} == 1 || ${mode} == 3 ]];then
		rm -rf ./docker
		rm -rf ./kubernetes
		yum remove -y docker-ce-19.03.15-3.el8 docker-ce-cli-19.03.15-3.el8 containerd.io > /dev/null 2>&1
		yum remove -y kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64 > /dev/null 2>&1
		yum-config-manager --add-repo https://repo.huaweicloud.com/docker-ce/linux/centos/docker-ce.repo
		sed -i 's/$releasever/8/g' /etc/yum.repos.d/docker-ce.repo
		yum install --allowerasing -y docker-ce-19.03.15-3.el8 docker-ce-cli-19.03.15-3.el8 containerd.io --downloadonly  --downloaddir=./docker
		yum install -y kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64  --downloadonly  --downloaddir=./kubernetes
	fi

	if [[ ${mode} == 2 || ${mode} == 3 ]];then
		rpm -ivh ./docker/*.rpm --force --nodeps
		rpm -ivh ./kubernetes/*.rpm --force --nodeps
	fi	
}
function AnolisOS_python3_module(){
	echo "AnolisOS_python3_module call"
	rpm -qa|grep python38|xargs rpm -ev --allmatches --nodeps  > /dev/null 2>&1
    yum remove -y python2 > /dev/null 2>&1
}
function AnolisOS(){
	echo "AnolisOS call"
	AnolisOS_python3_module
	commonInstall
	rm -rf /usr/local/bin/pip3
	cp -r /usr/bin/pip3 /usr/local/bin/pip3
	pip3s=(pyyaml)
	for var in ${pip3s[@]};
	do
		pipOperator $var
	done
	mongo_tool
	if [[ ${mode} == 1 || ${mode} == 3 ]];then
	 	rpm -ivh http://mirrors.wlnmp.com/centos/wlnmp-release-centos.noarch.rpm
		yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
	fi
	rpms=(wntp)
	for var in ${rpms[@]};
	do
		rpmOperator $var
	done

	kubernetes_process
}
function openEulerOs(){
	echo "openEulerOs call"
	commonInstall
	mongo_tool
	if [[ ${mode} == 1 || ${mode} == 3 ]];then
		dnf config-manager --add-repo=https://mirrors.aliyun.com/openeuler/openEuler-20.03-LTS/OS/x86_64/
		dnf config-manager --add-repo=https://mirrors.aliyun.com/openeuler/openEuler-20.03-LTS/everything/x86_64/
	fi
	rpms=(ntp)
	for var in ${rpms[@]};
	do
		rpmOperator $var
	done
	kubernetes_process
}


result=$(echo $osname | grep ".oe2203.x86_64")
if	[[ "$result" != "" ]] && [[ "True" == "$needExec" ]];then
	openEulerOs
fi
result=$(echo $osname | grep ".an8.x86_64")
if	[[ "$result" != "" ]]&& [[ "True" == "$needExec" ]];then
	AnolisOS
fi