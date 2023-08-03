#!/bin/bash
osname=(`uname -r`)
release_an8_dir="4.19.91-26.an8.x86_64"
release_oe2203_dir="5.10.0-153.12.0.92.oe2203sp2.x86_64"
release_el7_dir="3.10.0-957.el7.x86_64"
mkdir -p /opt/kad/down/rpms/common/nginx/${release_an8_dir}
mkdir -p /opt/kad/down/rpms/common/nginx/${release_oe2203_dir}
mkdir -p /opt/kad/down/rpms/common/nginx/${release_el7_dir}
result=$(echo $osname | grep ".oe2203" | grep ".x86_64")
if	[[ "$result" != "" ]];then
    if  [[ ${release_oe2203_dir} != "$osname" ]];then
	    ln -s /opt/kad/down/rpms/common/nginx/${release_oe2203_dir} /opt/kad/down/rpms/common/nginx/${osname}
    fi
    set -e
    rpm -ivh /opt/kad/down/rpms/common/nginx/${osname}/*rpm --force --nodeps
    set +e
fi
result=$(echo $osname | grep ".an8"| grep ".x86_64")
if	[[ "$result" != "" ]];then
    if  [[ ${release_oe2203_dir} != "$osname" ]];then
	    ln -s /opt/kad/down/rpms/common/nginx/${release_an8_dir} /opt/kad/down/rpms/common/nginx/${osname}
    fi
    set -e
    rpm -ivh /opt/kad/down/rpms/common/nginx/${osname}/*rpm --force --nodeps
    set +e
fi
result=$(echo $osname | grep ".el7"| grep ".x86_64")
if	[[ "$result" != "" ]];then
    if  [[ ${release_oe2203_dir} != "$osname" ]];then
	    ln -s /opt/kad/down/rpms/common/nginx/${release_el7_dir} /opt/kad/down/rpms/common/nginx/${osname}
    fi
    set -e
    rpm -ivh /opt/kad/down/rpms/common/nginx/${osname}/*rpm
    set +e
fi
