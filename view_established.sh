#!/bin/bash

#if [[ -n $(dnf list installed | grep jq.x86_64) ]];then
#	echo "No need to install jq"
#else
#	echo "Need to install jq. Installing"
#	dnf -y install jq
#fi


proxyIp=172.16.171.132
proxyPort=$1
#proxySsh=$(jq -r '.server.port' config.json)

while true;do
	echo $(date) :: $(netstat -anp | grep "$proxyIp:$proxyPort" | grep -i ESTABLISHED | wc -l)
        sleep 1
done
