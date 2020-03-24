#!/bin/bash
## Shows all active ESTABLISHED and TIME_WAIT connections on listening proxy port
## USAGE: ./view_established.sh 8022 ##

if [[ -z $1 ]];then
	echo "Requires port argument"
fi

#proxyIp=$(hostname -I)
proxyPort=$1

while true;do
	echo $(date) :: $(netstat -anp | grep ":$proxyPort" | grep -i ESTABLISHED | wc -l) "-" "ESTABLISHED"
	echo $(date) :: $(netstat -anp | grep ":$proxyPort" | grep -i TIME_WAIT | wc -l) "-" "TIME_WAIT"
        sleep 1
done
