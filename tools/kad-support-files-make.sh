#!/bin/bash
set -o errexit
set -o pipefail
rm -rf kad-support-files-2.9.0
mkdir  kad-support-files-2.9.0
mkdir  kad-support-files-2.9.0/bin
mkdir  kad-support-files-2.9.0/down 
mkdir  kad-support-files-2.9.0/down/rpms   
downFiles=( addon-resizer-1.8.3.tar  calico_v3.4.3.tar  dashboard_v1.10.1.tar  heapster_v1.5.4.tar  metrics-server_v0.3.1.tar  mongo-4.0.24.tar       rocketmq-4.3.0.tar  \
	busybox-1.30.1.tar         mgob-1.0.tar               postgres-13.6.tar                        \
	coredns-v1.8.6.tar  etcd-3.5.1-0.tar  flannel-cni-plugin-v1.1.2.tar  flannel-v0.20.2.tar  kube-apiserver-v1.23.8.tar     \
	kube-controller-manager-v1.23.8.tar  kube-proxy-v1.23.8.tar  kube-scheduler-v1.23.8.tar  nginx-ingress-1.5.1.tar  pause-3.6.tar   \
	sourceid-kad-dlmu.r1.3.zip)
for var in ${downFiles[@]};
do
	cp -r /opt/kad/down/${var} ./kad-support-files-2.9.0/down
done
rpmsFile=(5.10.0-60.18.0.50.oe2203.x86_64 4.19.91-26.an8.x86_64 3.10.0-957.el7.x86_64)
for var in ${rpmsFile[@]};
do
	mkdir ./kad-support-files-2.9.0/down/rpms/${var}
	cp -r  /opt/kad/down/rpms/${var} ./kad-support-files-2.9.0/down/rpms/
done
cd    kad-support-files-2.9.0
tar  -zcvf   kad-support-files-2.9.0.tar.gz bin down
cd ..
mv kad-support-files-2.9.0/kad-support-files-2.9.0.tar.gz .
