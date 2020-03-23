#!/bin/bash

# must be ran inline
proxyIp=172.16.171.132
proxyPort=8005

for i in {1..10000};do
    telnet 172.16.171.132 8005 &
    sleep 0.5
done