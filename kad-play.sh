#!/bin/bash

ansible-playbook -i inventory/ -k $* -e 'ansible_python_interpreter=/usr/bin/python3'
