#!/bin/bash
#$1 新ip
#$2 旧ip
ifMark=`ip a|grep $2/ |awk '{print $NF}'`
ifCfg=/etc/sysconfig/network-scripts/ifcfg-${ifMark}
sed -i "s/IPADDR=$2/IPADDR=$1/g" ${ifCfg}
sed -i 's/IPADDR="$2"/IPADDR="$1"/g' ${ifCfg}
