#!/bin/bash
osname=(`uname -r`)
rm -rf /opt/kad/down/fdfs/rpms
rm -rf /opt/kad/down/fdfs/rpms/fastdfs/${osname}
mkdir -p /opt/kad/down/fdfs/rpms/fastdfs/${osname}
tar -xvf /opt/kad/down/fdfs/fastdfs.tar.gz -C /opt/kad/down/fdfs/rpms/
chmod +777  /opt/kad/tools/fdfsinstall.sh
\cp -rpf  /opt/kad/tools/fdfsinstall.sh /opt/kad/down/fdfs/rpms/fastdfs
cd /opt/kad/down/fdfs/rpms/fastdfs/${osname}
result=$(echo $osname | grep ".el7.x86_64")
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
               net-snmp-libs    openssl-devel   pcre-devel  perl-Data-Dumper   perl-Test-Harness  perl-Thread-Queue  zlib-devel "    
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

cd /opt/kad/down/fdfs/rpms/
rm -rf /opt/kad/down/fdfs/rpms/fastdfs.tar.gz
tar  -zcvf   fastdfs.tar.gz *
\cp -rpf  fastdfs.tar.gz /opt/kad/down/fdfs/