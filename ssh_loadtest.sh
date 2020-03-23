#!/bin/bash

for i in {1..1000};do
	$(ssh test@172.16.171.132 -p 8005 'bash -s' <  ssh_script.sh) &
done
