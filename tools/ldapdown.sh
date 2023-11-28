#!/bin/bash
osname=(`uname -r`)
rm -rf /opt/kad/down/ldap/rpms
mkdir -p /opt/kad/down/ldap/rpms/ldap/${osname}
cd /opt/kad/down/ldap/rpms/ldap/${osname}
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
  rpms="cyrus-sasl-devel    openldap-clients openldap-devel openldap-servers cyrus-sasl-lib openldap libtool-ltdl guile" 
	yum install -y $rpms --downloadonly  --downloaddir=./ 
} 
function ky10(){
	echo "openEulerOs call"
 	 rpms="cyrus-sasl-devel    openldap-clients openldap-devel openldap-servers cyrus-sasl-lib openldap libtool-ltdl" 
	 yum install -y cyrus-sasl-devel    openldap-clients openldap-devel openldap-servers cyrus-sasl-lib openldap libtool-ltdl --downloadonly  --downloaddir=./ 
}	   
result=$(echo $osname | grep ".oe2203")
yum remove -y make
if	[[ "$result" != "" ]] ;then
	openEulerOs
fi
result=$(echo $osname | grep ".an8")
if	[[ "$result" != "" ]];then
	AnolisOS
fi
result=$(echo $osname | grep ".el7.x86_64")
if	[[ "$result" != "" ]];then
	centos7
fi
result=$(echo $osname | grep ".ky10")
if	[[ "$result" != "" ]];then
	ky10
fi
cd /opt/kad/down/ldap/rpms/
rm -rf /opt/kad/down/ldap/rpms/ldap.tar.gz
tar  -zcvf   ldap.tar.gz *
cp ldap.tar.gz /opt/kad/down/ldap/