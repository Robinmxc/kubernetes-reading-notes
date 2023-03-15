#!/bin/bash
if [ ! -n "$1" ] || [ ! -n "$2" ];
then
  echo "ip不能为空,请输入原ip与新ip!"
else
  sed -i "s/$1/$2/g" /opt/kad/workspace/k8s/conf/all.yml;
  cd /opt/kad;
  ./kad-play.sh -e "old_ip=$1" -e "new_ip=$2" -e "ischangeip=1" playbooks/smpplus/changeip.yml;
fi
