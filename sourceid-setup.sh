#!/bin/bash

result=$(python inventory/kad-workspace.py --check)
if [ "$result"x != "ok"x ]
then
  echo ""
  echo -en "\033[31m"
  echo Error: $result
  echo -en "\033[0m"
  echo ""
  exit 1
fi

./kad-play.sh playbooks/sourceid/0-all.yml
