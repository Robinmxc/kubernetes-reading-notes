#!/bin/bash
osname=(`uname -r`)
release_an8_dir="4.19.91-26.an8.x86_64"
release_oe2203_dir="5.10.0-153.12.0.92.oe2203sp2.x86_64"
release_el7_dir="3.10.0-957.el7.x86_64"
release_ky10_dir="4.19.90-52.15.v2207.ky10.x86_64"
dir=${1} 
mkdir -p ${dir}/${release_an8_dir}
mkdir -p ${dir}/${release_oe2203_dir}
mkdir -p ${dir}/${release_el7_dir}
mkdir -p ${dir}/${release_ky10_dir}
result=$(echo $osname | grep ".oe2203" | grep ".x86_64")
if	[[ "$result" != "" ]];then
    if  [[ ${release_oe2203_dir} != "$osname" ]];then
	    ln -s ${dir}/${release_oe2203_dir} ${dir}/${osname}
    fi
    set -e
    rpm -ivh ${dir}/${osname}/*rpm --force --nodeps 
    set +e
fi
result=$(echo $osname | grep ".an8"| grep ".x86_64")
if	[[ "$result" != "" ]];then
    if  [[ ${release_an8_dir} != "$osname" ]];then
	    ln -s ${dir}/${release_an8_dir} ${dir}/${osname}
    fi
    set -e
    rpm -ivh ${dir}/${osname}/*rpm --force --nodeps 
    set +e    
fi
result=$(echo $osname | grep ".el7"| grep ".x86_64")
if	[[ "$result" != "" ]];then
    if  [[ ${release_el7_dir} != "$osname" ]];then
	    ln -s ${dir}/${release_el7_dir} ${dir}/${osname}
    fi
    set -e
    rpm -ivh ${dir}/${osname}/*rpm  --force --nodeps
    set +e
fi
result=$(echo $osname | grep ".ky10"| grep ".x86_64")
if	[[ "$result" != "" ]];then
    if  [[ ${release_ky10_dir} != "$osname" ]];then
	    ln -s ${dir}/${release_ky10_dir} ${dir}/${osname}
    fi
    set -e
    rpm -ivh ${dir}/${osname}/*rpm --force --nodeps 
    set +e    
fi