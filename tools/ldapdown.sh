#!/bin/bash
osname=(`uname -r`)
result=$(echo $osname | grep ".el7.x86_64")
allowerasing="--allowerasing"
if	[[ "$result" != "" ]]&& [[ "True" == "$needExec" ]];then
 	allowerasing=""
fi
function ldap_process(){
	echo "ldap_process call"
	yum remove -y perl openldap openldap-clients  openldap-devel openldap-servers migrationtools     compat-openldap cyrus-sasl cyrus-sasl-devel cyrus-sasl-lib > /dev/null 2>&1
	mkdir /opt/kad/down/ldap/ldap
	rm -rf cd /opt/kad/down/ldap/ldap/${osname}
	mkdir /opt/kad/down/ldap/ldap/${osname}
	yum install -y  perl openldap openldap-clients  openldap-devel openldap-servers migrationtools     compat-openldap cyrus-sasl cyrus-sasl-devel cyrus-sasl-lib  --downloadonly  --downloaddir=/opt/kad/down/ldap/ldap/${osname}
	cd /opt/kad/down/ldap/ldap/
	rm -rf /opt/kad/down/ldap/ldap/*.tar
	tar  -cvf   ldap.tar *
	cd /opt/kad/down/ldap/
	mv ldap/ldap.tar .
}
function nginx_process(){
	echo "nginx_process call"
	rpms="perl  perl-Thread-Queue perl-Test-Harness perl-Data-Dumper wget centos-indexhtml gperftools-libs  nginx-filesystem  \
	openssl11-libs gcc gcc-c++   pcre-devel openssl openssl-devel zlib  zlib-devel libtool openssl-libs autoconf automake make keepalived \
	ipset libverto-devel mpfr"
	yum remove -y rpms > /dev/null 2>&1
	mkdir /opt/kad/down/ldap/nginxbuild
	rm -rf cd /opt/kad/down/ldap/nginxbuild/${osname}
	mkdir /opt/kad/down/ldap/nginxbuild/${osname}
	echo "/opt/kad/down/ldap/nginxbuild/${osname}"
	yum install -y  $rpms  --downloadonly  --downloaddir=/opt/kad/down/ldap/nginxbuild/${osname}

	cd /opt/kad/down/ldap/nginxbuild/
	rm -rf /opt/kad/down/ldap/nginxbuild/*.tar
	tar  -cvf   nginxbuild.tar *
	cd /opt/kad/down/ldap/
	mv nginxbuild/nginxbuild.tar .
}
function openEulerOs(){
	echo "openEulerOs call"
    
}    
function AnolisOS(){
	echo "AnolisOS call"
}  
function centos7(){
	echo "centos7 call"
	nginx_process
}  
result=$(echo $osname | grep ".oe2203.x86_64")
if	[[ "$result" != "" ]] ;then
	openEulerOs
fi
result=$(echo $osname | grep ".an8.x86_64")
if	[[ "$result" != "" ]];then
	AnolisOS
fi
result=$(echo $osname | grep ".el7.x86_64")
if	[[ "$result" != "" ]];then
	centos7
fi