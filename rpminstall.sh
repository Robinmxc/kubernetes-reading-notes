#!/bin/bash
if [  -f "./rpminstall.sh" ];then
	cp -r ./rpminstall.sh /opt/kad/down/rpms
fi

mode=${1:-3} 
needExec=${2:-"True"} 
skipKubernetes=${3:-"False"} 
osname=(`uname -r`)
mkdir -p /opt/kad/down/rpms/${osname}
cd /opt/kad/down/rpms/${osname}

echo "###检查unzip安装成功####"
if [ -d  /opt/kad/down/rpms/${osname}/unzip ];then
    rpm -ivh  /opt/kad/down/rpms/${osname}/unzip/*.rpm --force --nodeps 
    if [ $? -eq 0 ];then
                echo -e "\033[36m Unzip RPM installed sucessfully.\033[0m "
    else
                echo -e "\033[31m Unzip RPM installed failed. Please check rpm env\033[0m "
                exit 0
    fi

else 
    rpm -ivh  /opt/kad/down/rpms/unzip/*.rpm --force --nodeps 
    if [ $? -eq 0 ];then
                echo -e "\033[36m Unzip RPM installed sucessfully.\033[0m "
    else
                echo -e "\033[31m Unzip RPM installed failed. Please check rpm env\033[0m "
                exit 0
    fi

fi


result=$(echo $osname | grep ".el7.x86_64")
allowerasing="--allowerasing"
if	[[ "$result" != "" ]]&& [[ "True" == "$needExec" ]];then
 	allowerasing=""
	rpm -e --nodeps python3  > /dev/null 2>&1
fi
function rpmOperator(){
	var=${1} 
	echo "rpmOperator call ${var}"
	if [[ ${mode} == 4 ]];then
		yum remove -y $var > /dev/null 2>&1
	fi
	if [[ ${mode} == 3 ]];then
		yum remove -y $var > /dev/null 2>&1
		rm -rf  $var 
		mkdir $var
		cd $var
		result=$(echo $osname | grep ".el7.x86_64")
		if	[[ "$result" != "" ]]&& [[ "True" == "$needExec" ]];then
			yum install $var --downloadonly  --downloaddir=.
		else
			dnf download $var --resolve
		fi
		cd ..
	fi
	fileSize=`ls ./$var/ | wc -l`
	if [[ ${mode} == 2 || ${mode} == 3 ]]  && [[ ${fileSize} > 0 ]]; then
			set -e
			rpm -ivh ./$var/*.rpm --force --nodeps
			set +e
	fi	
}
function pipOperator(){
	var=${1} 
	echo "pipOperator call ${var}"
	if [[ ${mode} == 4 ]];then
		pip3 uninstall -y $var > /dev/null 2>&1
	fi
	if [[ ${mode} == 3 ]];then
		pip3 uninstall -y $var > /dev/null 2>&1
		rm -rf $var
		pip3 download -d $var  $var -i   https://pypi.douban.com/simple/
	fi
	if [[ ${mode} == 2 || ${mode} == 3 ]];then
	    set -e
		pip3 install  ./$var/*.whl
		set +e
	fi	

}
function mongo_tool(){
	echo "mongo_tool call"
	if [[ ${mode} == 4 ]];then
		yum remove -y mongodb-database-tools > /dev/null 2>&1
	fi
	if [[  ${mode} == 3 ]];then
		yum remove -y mongodb-database-tools > /dev/null 2>&1
		rm -rf   mongodb-database-tools
		mkdir  mongodb-database-tools
		cd mongodb-database-tools
		wget https://fastdl.mongodb.org/tools/db/mongodb-database-tools-rhel80-x86_64-100.6.1.rpm
		cd ..
		result=$(echo $osname | grep ".el7.x86_64")
		yum install ${allowerasing} -y ./mongodb-database-tools/mongodb-database-tools-rhel80-x86_64-100.6.1.rpm --downloadonly  --downloaddir=./mongodb-database-tools
	fi
	if [[ ${mode} == 2 || ${mode} == 3 ]]; then
			set -e
			rpm -ivh ./mongodb-database-tools/*.rpm --force --nodeps
			set +e
	fi	
}
function commonInstall(){
	echo "commonInstall call"
	echo "参数 2：仅安装用于现场  3:下载并安装（特定场景） 4:清理 当前参数${mode}"
	rpms=(git  sshpass  wget unzip libpcap tcpdump net-tools iptables-services ipset-libs ipset ipvsadm tcl bash-completion  rsyslog  \
		oniguruma polkit psmisc rsync socat  make  nfs-utils cyrus-sasl)
	for var in ${rpms[@]};
	do
		rpmOperator $var
	done
	
	source /usr/share/bash-completion/bash_completion

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
function ansibleInstall(){
	cp -r /usr/bin/pip3 /usr/local/bin/pip3
	pip3s=(ansible)
	for var in ${pip3s[@]};
	do
		pipOperator $var
	done
}		
function kubernetes_process(){
	echo "kubernetes_process call"
	if [[ ${mode} == 4 ]];then
		yum remove -y docker-ce-19.03.15-3.el8 docker-ce-cli-19.03.15-3.el8 containerd.io > /dev/null 2>&1
		yum remove -y  libbpf conntrack-tools containernetworking-plugins  cri-tools libnetfilter_cthelper libnetfilter_cttimeout  libnetfilter_queue kubernetes-cni-1.2.0-0  kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64 > /dev/null 2>&1
	fi	
	if [[ ${mode} == 3 ]];then
		rm -rf ./docker
		rm -rf ./kubernetes
		yum remove -y docker-ce-19.03.15-3.el8 docker-ce-cli-19.03.15-3.el8 containerd.io > /dev/null 2>&1
		yum remove -y  libbpf conntrack-tools containernetworking-plugins  cri-tools libnetfilter_cthelper libnetfilter_cttimeout  libnetfilter_queue kubernetes-cni-1.2.0-0  kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64 > /dev/null 2>&1
		yum install ${allowerasing} -y docker-ce-19.03.15-3.el8 docker-ce-cli-19.03.15-3.el8 containerd.io --downloadonly  --downloaddir=./docker
		yum install -y  libbpf kubernetes-cni-1.2.0-0 kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64  --downloadonly  --downloaddir=./kubernetes
	fi

	if [[ ${mode} == 2 || ${mode} == 3 ]];then
	    set -e
		rpm -ivh ./docker/*.rpm --force --nodeps
		rpm -ivh ./kubernetes/*.rpm --force --nodeps
		set +e
	fi	
}
function kubernetes_process_centos7(){
	if [[ "${skipKubernetes}" != "True" ]];then
		echo "kubernetes_process call"
		if [[ ${mode} == 4 ]];then
			yum remove -y docker-ce-19.03.15-3.el7 docker-ce-cli-19.03.15-3.el7 containerd.io > /dev/null 2>&1
			yum remove -y   conntrack-tools containernetworking-plugins  cri-tools libnetfilter_cthelper libnetfilter_cttimeout  libnetfilter_queue kubernetes-cni-1.2.0-0  kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64 > /dev/null 2>&1
		fi	
		if [[ ${mode} == 3 ]];then
			rm -rf ./docker
			rm -rf ./kubernetes
			yum remove -y docker-ce-19.03.15-3.el7 docker-ce-cli-19.03.15-3.el7 containerd.io > /dev/null 2>&1
			yum remove -y   conntrack-tools containernetworking-plugins  cri-tools libnetfilter_cthelper libnetfilter_cttimeout  libnetfilter_queue kubernetes-cni-1.2.0-0  kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64 > /dev/null 2>&1
			set -e
			yum install  -y docker-ce-19.03.15-3.el7 docker-ce-cli-19.03.15-3.el7 containerd.io --downloadonly  --downloaddir=./docker
			yum install -y   kubernetes-cni-1.2.0-0 kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64  --downloadonly  --downloaddir=./kubernetes
			set +e
		fi

		if [[ ${mode} == 2 || ${mode} == 3 ]];then
			#解决重装时docker删除不干净问题
			yum remove -y docker-ce-19.03.15-3.el7 docker-ce-cli-19.03.15-3.el7 containerd.io > /dev/null 2>&1
			yum remove -y   conntrack-tools containernetworking-plugins  cri-tools libnetfilter_cthelper libnetfilter_cttimeout  libnetfilter_queue kubernetes-cni-1.2.0-0  kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64 > /dev/null 2>&1
			set -e
			rpm -ivh ./docker/*.rpm --force --nodeps
			rpm -ivh ./kubernetes/*.rpm --force --nodeps
			set +e
		fi

	fi	
	
}
function AnolisOS_python3_module(){
	echo "AnolisOS_python3_module call"
	rpm -qa|grep python38|xargs rpm -ev --allmatches --nodeps  > /dev/null 2>&1
	rpm -qa|grep python36|xargs rpm -ev --allmatches --nodeps  > /dev/null 2>&1
    yum remove -y python2 > /dev/null 2>&1
}
function AnolisOS(){
	echo "AnolisOS call"
	AnolisOS_python3_module
	if [[ ${mode} == 3 ]];then
		yum -y install yum-utils 
		yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
		#yum -y copr enable copart/restic 
	fi
	commonInstall
	rpms=(tar jq python39 wntp epel-release unzip)
	for var in ${rpms[@]};
	do
		rpmOperator $var
	done
	rm -rf /usr/local/bin/pip3
	cp -r /usr/bin/pip3 /usr/local/bin/pip3
	pip3s=(pyyaml simplejson)
	for var in ${pip3s[@]};
	do
		pipOperator $var
	done
	mongo_tool
	if [[ ${mode} == 3 ]];then
	 	rpm -ivh http://mirrors.wlnmp.com/centos/wlnmp-release-centos.noarch.rpm
		yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
	fi
	ansibleInstall
	kubernetes_process
}
function openEulerOs(){
	echo "openEulerOs call"
	if [[ ${mode} == 3 ]];then
		dnf config-manager --add-repo=https://mirrors.aliyun.com/openeuler/openEuler-20.03-LTS/OS/x86_64/
		dnf config-manager --add-repo=https://mirrors.aliyun.com/openeuler/openEuler-20.03-LTS/everything/x86_64/
		rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-openEuler
		yum-config-manager --add-repo https://repo.huaweicloud.com/docker-ce/linux/centos/docker-ce.repo
		sed -i 's/$releasever/8/g' /etc/yum.repos.d/docker-ce.repo
	fi
	commonInstall
	rpms=(tar jq python39 ntp  chrony.x86_64)
	for var in ${rpms[@]};
	do
		rpmOperator $var
	done
	mongo_tool
	ansibleInstall
	kubernetes_process
}

function centos7(){
	echo "centos7 call"
	if [[ ${mode} == 3 ]];then
		yum -y install yum-utils 
		yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
		yum install -y http://mirror.centos.org/centos/7/extras/x86_64/Packages/container-selinux-2.119.1-1.c57a6f9.el7.noarch.rpm
		yum install -y http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
	fi
	commonInstall
	rpms=(python3 ntp  chrony.x86_64 ansible)
	for var in ${rpms[@]};
	do
		rpmOperator $var
	done

	pip3s=(pyyaml)
	for var in ${pip3s[@]};
	do
		pipOperator $var
	done
	
	mongo_tool
	kubernetes_process_centos7
}

result=$(echo $osname | grep ".oe2203.x86_64")
if	[[ "$result" != "" ]] && [[ "True" == "$needExec" ]];then
	openEulerOs
fi
result=$(echo $osname | grep ".an8.x86_64")
if	[[ "$result" != "" ]]&& [[ "True" == "$needExec" ]];then
	AnolisOS
fi
result=$(echo $osname | grep ".el7.x86_64")
if	[[ "$result" != "" ]];then
	if  [[ "True" == "$needExec" ]];then
		centos7
	else	
		## 凡是安装必须重新走一下此保证清理和安装，主要升级场景kubelet服务不能删除
		kubernetes_process_centos7
	fi	
fi