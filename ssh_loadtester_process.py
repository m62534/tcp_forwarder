#!/usr/local/bin/python3

import sys, os, string
import paramiko
import json
import multiprocessing
from time import sleep

def main():
    global host, port, run, username, password
    with open('loadtest.json', 'r') as f:
        loadtest_config = json.load(f)
    host = loadtest_config['host']
    port = loadtest_config['port']
    load = loadtest_config['load']
    username = loadtest_config['username']
    password = loadtest_config['password']
    sleeptime = loadtest_config['sleeptime']

    run = "echo hi; sleep " + str(sleeptime)
    run = "for i in {1.." + str(sleeptime) + "};do echo hi;sleep 1;done"
    jobs = []
    for i in range(load):
        p = multiprocessing.Process(target=sshRun)
        jobs.append(p)
        p.start()
        sleep(0.1)
    

def sshRun():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username=username, password=password, timeout = 60, allow_agent=False,look_for_keys=False)
    stdin, stdout, _ = ssh.exec_command(run)
    stdin.write('xy\n')
    stdin.flush()
    _ = stdout.readlines()
    ssh.close()

if __name__ == "__main__":
    main()