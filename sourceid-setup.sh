#!/bin/bash

#rpmDirs=$(ls /opt/kad/down/rpms/)
#for loop in ${rpmDirs[*]}
#do
# rpm -ivh /opt/kad/down/rpms/$loop/*.rpm  >/dev/null 2>&1
#done
chmod +777 ./rpminstall.sh
cp -r ./rpminstall.sh /opt/kad/down/rpms
cd /opt/kad/down/rpms
./rpminstall.sh
cd /opt/kad/down/ 
tar -xvf /opt/kad/down/rarlinux-x64-5.3.0.tar.gz >/dev/null 2>&1
cd /opt/kad/down/rar
make >/dev/null 
chmod 777 /opt/kad/*.sh 
chmod 777 /opt/kad/inventory/kad-workspace.py
if [ ! -d "/opt/kad/workspace" ]; then
  cp -rpf /opt/kad/example/workspace /opt/kad/workspace 
  chmod -R o-w /opt/kad/workspace
  chmod -R o-r /opt/kad/workspace
fi
if [ ! -f "/usr/bin/kad-play" ]; then
  link /opt/kad/kad-play.sh /usr/bin/kad-play
fi

grep DATA_DIR /etc/kad/config.yml >/dev/null 2>&1
if [ $? -ne 0 ]; then
    if [ ! -d "/etc/kad" ]; then
    mkdir /etc/kad>/dev/null
    fi
    touch /etc/kad/config.yml
fi

export KAD_APP_NAMESPACE=ruijie-sourceid
cd /opt/kad
./kad-play.sh playbooks/sourceid/0-all.yml

