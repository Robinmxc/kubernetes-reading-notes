#!/bin/bash

export NAT_IP=$1

if [ -z "$NAT_IP" ]
then
	echo "please set the NAT_IP， example: [./nat.sh 192.168.xxx.xx]"
	exit
fi

#### 添加转发规则
iptables -t nat -A PREROUTING -p tcp  --dport 80 -j DNAT --to $NAT_IP:80
iptables -t nat -A PREROUTING -p tcp  --dport 443 -j DNAT --to $NAT_IP:443
iptables -t nat -A POSTROUTING -j MASQUERADE

#### 查看当前规则
# iptables -t nat -L -n | grep $NAT_IP