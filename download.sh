#!/bin/bash

ansible-playbook -i inventory/ playbooks/prepare-download.yml

down/download.sh
