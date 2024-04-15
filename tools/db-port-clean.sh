#!/bin/bash
kubectl delete service -n ruijie-sourceid mongo-node 
kubectl delete service -n ruijie-sourceid rg-pg-node
kubectl delete service -n ruijie-sourceid sidpy-node