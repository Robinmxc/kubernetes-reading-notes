#!/bin/bash

## 从2.0.3版本开始替换
versions=(R2.0.3)

## 需要更新的脚本
database=(linkid cas ess)

CURRENT_VERSION=R2.0.3
cd {{ KAD_PACKAGE_DIR }}/db/sourceid/rg-upgrade-db

for (( i = 0 ; i < ${#database[@]} ; i++ ))
do
start=0
end=0
FILE_NAME=${database[$i]}
UPGRADE_VERSION={{DB_VERSION[${FILE_NAME}]["version"]}}
for (( j = 0 ; j < ${#versions[@]} ; j++ ))
do
if [ ${versions[$j]} == ${CURRENT_VERSION} ]
then
	start=$j
fi
if [ ${versions[$j]} == ${UPGRADE_VERSION} ]
then
	end=$j
fi
done

for (( j = $start+1 ; j < $end+1 ; j++ ))
do
directory=${FILE_NAME}_upgrade_db/sourceid/${versions[$j]}

find ./${directory} -name "*.sql" -type f -exec sed 's/(SOURCEID_SSO_DOMAIN)/{{SOURCEID_SSO_DOMAIN}}/g' {} \
find ./${directory} -name "*.js" -type f -exec sed 's/(SOURCEID_SSO_DOMAIN)/{{SOURCEID_SSO_DOMAIN}}/g' {} \

find ./${directory} -name "*.sql" -type f -exec sed 's/(SOURCEID_GATE_DOMAIN)/{{SOURCEID_GATE_DOMAIN}}/g' {} \;
find ./${directory} -name "*.js" -type f -exec sed 's/(SOURCEID_GATE_DOMAIN)/{{SOURCEID_GATE_DOMAIN}}/g' {} \;
done

done