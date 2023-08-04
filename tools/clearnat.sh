#!/bin/bash

#### 清除转发规则
iptables -F -t nat

#### 查看当前规则
# iptables -t nat -L -n