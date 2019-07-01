#!/bin/bash

# create ca cert
cfssl gencert -initca ca-csr.json | cfssljson -bare ca

# create app cert
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config ca-config.json -profile=app example.com-csr.json | cfssljson -bare example.com
