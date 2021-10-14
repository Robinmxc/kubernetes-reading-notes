#!/bin/bash
set -o errexit
set -o pipefail

oldIp=$1
newIp=$2

kubectl delete -f /opt/kube/kube-system/coredns/coredns.yaml
kubectl delete -f /opt/kad/workspace/ruijie-smpplus/yaml/mongo/mongo1.yml
kubectl delete -f /opt/kad/workspace/ruijie-smpplus/yaml/rocketmq/rocketmq.yml
kubectl delete -f /opt/kube/kube-system/flannel/kube-flannel.yaml

podname=$(kubectl get pod -A -o custom-columns=NAME:.metadata.name)

while [[ ${podname} =~ "mongo1" || ${podname} =~ "rocketmq" || ${podname} =~ "flannel" ]]
do
  sleep 1;
  podname=$(kubectl get pod -A -o custom-columns=NAME:.metadata.name) 
done


cd /etc/etcd/ssl
echo "/opt/kube/bin/cfssl gencert -ca=/etc/kubernetes/ssl/ca.pem -ca-key=/etc/kubernetes/ssl/ca-key.pem -config=/etc/kubernetes/ssl/ca-config.json -profile=kubernetes etcd-csr.json | /opt/kube/bin/cfssljson -bare etcd"
/opt/kube/bin/cfssl gencert -ca=/etc/kubernetes/ssl/ca.pem -ca-key=/etc/kubernetes/ssl/ca-key.pem -config=/etc/kubernetes/ssl/ca-config.json -profile=kubernetes etcd-csr.json | /opt/kube/bin/cfssljson -bare etcd

cd /etc/kubernetes/ssl/
/opt/kube/bin/cfssl gencert -ca=/etc/kubernetes/ssl/ca.pem -ca-key=/etc/kubernetes/ssl/ca-key.pem -config=/etc/kubernetes/ssl/ca-config.json -profile=kubernetes kubernetes-csr.json | /opt/kube/bin/cfssljson -bare kubernetes

cd /etc/kubernetes/ssl/
/opt/kube/bin/cfssl gencert -ca=/etc/kubernetes/ssl/ca.pem -ca-key=/etc/kubernetes/ssl/ca-key.pem -config=/etc/kubernetes/ssl/ca-config.json -profile=kubernetes kubelet-csr.json | /opt/kube/bin/cfssljson -bare kubelet

/opt/kube/bin/cfssl gencert -ca=/etc/kubernetes/ssl/ca.pem -ca-key=/etc/kubernetes/ssl/ca-key.pem -config=/etc/kubernetes/ssl/ca-config.json -profile=kubernetes kube-proxy-csr.json | /opt/kube/bin/cfssljson -bare kube-proxy


/opt/kube/bin/kubectl config set-cluster kubernetes --certificate-authority=/etc/kubernetes/ssl/ca.pem --embed-certs=true --server=https://${newIp}:6443

cd /
/opt/kube/bin/kubectl config set-cluster kubernetes --certificate-authority=/etc/kubernetes/ssl/ca.pem --embed-certs=true --server=https://${newIp}:6443 --kubeconfig=kube-proxy.kubeconfig

/opt/kube/bin/kubectl config set-credentials kube-proxy --client-certificate=/etc/kubernetes/ssl/kube-proxy.pem --client-key=/etc/kubernetes/ssl/kube-proxy-key.pem --embed-certs=true --kubeconfig=kube-proxy.kubeconfig

/opt/kube/bin/kubectl config set-context default --cluster=kubernetes --user=kube-proxy --kubeconfig=kube-proxy.kubeconfig

/opt/kube/bin/kubectl config use-context default --kubeconfig=kube-proxy.kubeconfig

/opt/kube/bin/kubectl config set-cluster kubernetes --certificate-authority=/etc/kubernetes/ssl/ca.pem --embed-certs=true --server=https://${newIp}:6443 --kubeconfig=kubelet.kubeconfig

/opt/kube/bin/kubectl config set-credentials system:node:${newIp} --client-certificate=/etc/kubernetes/ssl/kubelet.pem --embed-certs=true --client-key=/etc/kubernetes/ssl/kubelet-key.pem --kubeconfig=kubelet.kubeconfig

/opt/kube/bin/kubectl config set-context default --cluster=kubernetes --user=system:node:${newIp} --kubeconfig=kubelet.kubeconfig

/opt/kube/bin/kubectl config use-context default --kubeconfig=kubelet.kubeconfig

cp -rpf kube-proxy.kubeconfig /etc/kubernetes/
cp -rpf kubelet.kubeconfig /etc/kubernetes/

systemctl daemon-reload

systemctl restart network

systemctl restart etcd.service kube-scheduler.service kube-proxy.service kubelet.service kube-controller-manager.service kube-apiserver.service

ifconfig cni0 down
ip link delete cni0

kubectl delete nodes ${oldIp}

kubectl apply -f /opt/kube/kube-system/flannel/kube-flannel.yaml
kubectl apply -f /opt/kube/kube-system/coredns/coredns.yaml
kubectl apply -f /opt/kad/workspace/ruijie-smpplus/yaml/mongo/mongo1.yml
kubectl apply -f /opt/kad/workspace/ruijie-smpplus/yaml/rocketmq/rocketmq.yml
