#!/bin/bash
serverUser=${4}
export KAD_APP_NAMESPACE=ruijie-smpplus
if [ ! -n "$1" ] || [ ! -n "$2" ];
then
  echo "ip不能为空,请输入原ip与新ip!"
else
  sed -i "s/$1/$2/g" /opt/kad/workspace/k8s/conf/all.yml;
  cd /opt/kad;
  if [ -n "$3" ] && [ "$3" = "Web_changeIp" ] ;
  then
    echo "web changeIp task execute..."
    source ./kad-play.sh -e "old_ip=$1" -e "new_ip=$2" -e "ischangeip=1" -e "iswebchangeip=1" playbooks/smpplus/changeip.yml;
  else
    echo "shell changeIp task execute..."
    source ./kad-play.sh -e "old_ip=$1" -e "new_ip=$2" -e "ischangeip=1" playbooks/smpplus/changeip.yml;
  fi
fi
