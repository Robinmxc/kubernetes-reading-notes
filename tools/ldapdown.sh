#!/bin/bash
osname=(`uname -r`)
rm -rf /opt/kad/down/ldap/rpms
mkdir -p /opt/kad/down/ldap/rpms/ldap/${osname}
cd /opt/kad/down/ldap/rpms/ldap/${osname}
result=$(echo $osname | grep ".el7.x86_64")
function centos7(){
	echo "centos7 call"
  rpms="compat-openldap cyrus-sasl-devel migrationtools   openldap-clients openldap-devel openldap-servers cyrus-sasl-lib openldap libtool-ltdl"           
	yum install -y $rpms --downloadonly  --downloaddir=./
}  
function AnolisOS(){
	echo "AnolisOS call"
  rpms="cyrus-sasl-devel    openldap-clients openldap-devel openldap-servers cyrus-sasl-lib openldap libtool-ltdl"     
	yum install -y $rpms --downloadonly  --downloaddir=./
}  
function openEulerOs(){
	echo "openEulerOs call"
  rpms="cyrus-sasl-devel    openldap-clients openldap-devel openldap-servers cyrus-sasl-lib openldap libtool-ltdl" 
	yum install -y $rpms --downloadonly  --downloaddir=./ 
}    
result=$(echo $osname | grep ".oe2203.x86_64")
yum remove -y make
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
cd /opt/kad/down/ldap/rpms/
rm -rf /opt/kad/down/ldap/rpms/ldap.tar.gz
tar  -zcvf   ldap.tar.gz *
cp ldap.tar.gz /opt/kad/down/ldap/