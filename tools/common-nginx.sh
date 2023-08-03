#!/bin/bash
osname=(`uname -r`)
rm -rf /opt/kad/down/rpms/common
rm -rf /opt/kad/down/rpms/common/nginx/${osname}
mkdir -p /opt/kad/down/rpms/common/nginx/${osname}
tar -xvf /opt/kad/down/common/nginx.tar.gz -C /opt/kad/down/rpms/common/
chmod +777  /opt/kad/tools/common-nginx-install.sh
\cp -rpf  /opt/kad/tools/common-nginx-install.sh /opt/kad/down/rpms/common/nginx
cd /opt/kad/down/rpms/common/nginx/${osname}
function centos7(){
	echo "centos7 call"
    rpms="make autoconf automake cpp gcc gcc-c++  glibc-devel  glibc-headers  keepalived  kernel-headers  keyutils-libs-devel  krb5-devel \
          libcom_err-devel libkadm5 libmpc libselinux-devel libsepol-devel libstdc++-devel \
             libtool  libverto-devel  lm_sensors-libs m4  mpfr  net-snmp-agent-libs \
               net-snmp-libs    openssl-devel   pcre-devel  perl-Data-Dumper   perl-Test-Harness  perl-Thread-Queue  zlib-devel "
	yum install -y $rpms --downloadonly  --downloaddir=./
}
function AnolisOS(){
	echo "AnolisOS call"
    rpms="make autoconf automake cpp gcc gcc-c++  glibc-devel  glibc-headers  keepalived  kernel-headers  keyutils-libs-devel  krb5-devel \
          libcom_err-devel libkadm5 libmpc libselinux-devel libsepol-devel libstdc++-devel \
             libtool  libverto-devel  lm_sensors-libs m4  mpfr  net-snmp-agent-libs \
               net-snmp-libs    openssl-devel   pcre-devel  perl-Data-Dumper   perl-Test-Harness  perl-Thread-Queue  zlib-devel "
	yum install -y $rpms --downloadonly  --downloaddir=./
}
function openEulerOs(){
	echo "openEulerOs call"
    rpms="make  autoconf automake cpp gcc gcc-c++  glibc-devel  glibc-headers  keepalived  kernel-headers  keyutils-libs-devel  krb5-devel \
          libcom_err-devel libkadm5 libmpc libselinux-devel libsepol-devel libstdc++-devel \
             libtool  libverto-devel  lm_sensors-libs m4  mpfr  net-snmp-agent-libs \
               net-snmp-libs    openssl-devel   pcre-devel  perl-Data-Dumper   perl-Test-Harness  perl-Thread-Queue  zlib-devel guile"
	yum install -y $rpms --downloadonly  --downloaddir=./
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

cd /opt/kad/down/rpms/common/
rm -rf /opt/kad/down/rpms/common/nginx.tar.gz
tar  -zcvf   nginx.tar.gz *
\cp -rpf  nginx.tar.gz /opt/kad/down/common/