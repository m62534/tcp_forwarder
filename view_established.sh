#!/bin/bash

proxyIp=172.16.171.132
proxySsh=$(jq -r '.server.port' config.json)

while true;do
	echo $(date) :: $(netstat -anp | grep "$proxyIp:$proxySsh" | grep -i ESTABLISHED | wc -l)
        sleep 1
done
