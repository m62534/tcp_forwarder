#!/bin/bash

proxyIp=172.16.171.132
proxyPort=8005

for i in {1..10000};do
    curl http://$proxyIp:$proxyPort >> /dev/null
done