#!/bin/bash

echo "开始执行回滚"
./kad-play.sh playbooks/sourceid/rollback.yml
echo "回滚成功"