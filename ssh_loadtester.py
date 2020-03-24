#!/usr/local/bin/python3

import sys, os, string, threading
import paramiko

lock = threading.Lock()

def main():
    threads = []
    host, port = '172.16.171.132', 8022
    run = "echo hi; sleep 10"
    for _ in range(20):
        thread = threading.Thread(target=sshRun, args=(host, port, run))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    

def sshRun(host,port,run):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username='test', password='test')
    stdin, stdout, stderr = ssh.exec_command(run)
    stdin.write('xy\n')
    stdin.flush()
    with lock:
        _ = stdout.readlines()

if __name__ == "__main__":
    main()