#!/bin/bash

ansible-playbook -i inventory/ playbooks/sourceid/download.yml

ansible-playbook -i inventory/ playbooks/sourceid/0-all.yml -k

