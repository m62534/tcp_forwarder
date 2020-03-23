#!/bin/bash
## Shows all active ESTABLISHED and TIME_WAIT connections on listening proxy port
## USAGE: ./view_established.sh 8022 ##

proxyIp=$(hostname -I)
proxyPort=$2

while true;do
	echo $(date) :: $(netstat -anp | grep "$proxyIp:$proxyPort" | grep -i ESTABLISHED | wc -l) "-" "ESTABLISHED"
	echo $(date) :: $(netstat -anp | grep "$proxyIp:$proxyPort" | grep -i TIME_WAIT | wc -l) "-" "TIME_WAIT"
        sleep 1
done
