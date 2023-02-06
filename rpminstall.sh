#!/bin/bash
yum remove -y python3
mode=${1:-3} 
if [[ ${mode} == 1 || ${mode} == 3 ]];then
	yum -y copr enable copart/restic
	yum -y install yum-utils
fi
echo "参数1：仅下载用于制造离线包 2：仅安装用于现场  3:下载并安装（特定场景） 当前参数${mode}"
rpms=(tar git python39 sshpass  wget unzip tcpdump net-tools ipset ipvsadm tcl bash-completion jq rsyslog oniguruma polkit psmisc rsync socat compat-openssl10 make wntp nfs-utils restic)
for var in ${rpms[@]};
do
     if [[ ${mode} == 1 || ${mode} == 3 ]];then
		yum remove -y $var
		rm -rf  $var
		mkdir $var
		cd $var
		dnf download $var --resolve
		cd ..
	fi
	if [[ ${mode} == 2 || ${mode} == 3 ]]; then
		rpm -ivh ./$var/*.rpm
	fi
done

cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg 
EOF

if [[ ${mode} == 1 || ${mode} == 3 ]];then
	rm -rf ./docker
	rm -rf ./kubernetes
	yum remove -y docker-ce-19.03.15-3.el8 docker-ce-cli-19.03.15-3.el8 containerd.io
	yum kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64
	yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
	yum install --allowerasing -y docker-ce-19.03.15-3.el8 docker-ce-cli-19.03.15-3.el8 containerd.io --downloadonly  --downloaddir=./docker
	yum install -y kubelet-1.23.8-0.x86_64 kubeadm-1.23.8-0.x86_64 kubectl-1.23.8-0.x86_64  --downloadonly  --downloaddir=./kubernetes
fi
if [[ ${mode} == 2 || ${mode} == 3 ]];then
	rpm -ivh ./docker/*.rpm --force --nodeps
	rpm -ivh ./kubernetes/*.rpm
fi

pip3s=(ansible)
for var in ${pip3s[@]};
do
	if [[ ${mode} == 1 || ${mode} == 3 ]];then
		pip3 uninstall -y $var
		rm -rf $var
		pip3 download -d $var  $var -i   https://pypi.douban.com/simple/
	fi
	if [[ ${mode} == 2 || ${mode} == 3 ]];then
		pip3 install  ./$var/*.whl
	fi	
done