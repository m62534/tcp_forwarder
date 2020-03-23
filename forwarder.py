#!/usr/bin/python3

import json
import socket
import select
import logging
import subprocess
import os
import re
import threading

class ThreadServer(threading.Thread):
    def init(self, proxyHost, proxyPort, destHost, destPort, connections, clientConn, client_fd, epol, event, fd, 
             final_fd, finalConn, limbo, serverSock, serverSock_fd):
        threading.Thread.__init__(self) 
        self.proxyHost      = proxyHost
        self.proxyPort      = proxyPort
        self.destHost       = destHost
        self.destPort       = destPort
        self.connections    = connections
        self.clientConn     = clientConn 
        self.client_fd      = client_fd 
        self.epol           = epol
        self.event          = event 
        self.fd             = fd
        self.final_fd       = final_fd 
        self.finalConn      = finalConn
        self.limbo          = limbo
        self.serverSock     = serverSock 
        self.serverSock_fd  = serverSock_fd

    def get_open_fds(self):
    
        pid = os.getpid()
        procs = subprocess.check_output( 
            [ "lsof", '-w', '-Ff', "-p", str( pid ) ] )
        
        procs = procs.decode()
        
        p = re.compile(r'f[0-9]+')
        result = p.findall(procs)
    
        return result

    def run(self): 
        while True : 
            print("Server host: ", self.serverHost)
            print("Server port ", self.serverPort)
            print("final host: ", self.finalHost)
            print("final port: ", self.finalPort)
        
            
            # Create server socket
            serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serverSock.bind((self.serverHost, self.serverPort))
            serverSock.listen(5)
            serverSock.setblocking(0) # non-blocking
        
            # Create epoll object
            epol = select.epoll()
            
            # Associate with server socket file descriptor to the epoll object
            epol.register(serverSock.fileno(), select.EPOLLIN)
            print("server associated with epoll object")
            
            # Instantiate
            connections, serverSock_fd = {}, serverSock.fileno()
        
            # Instantiate final dict for final host fd tracking
            limbo = {}
            #trackClient, trackFinal = {}, {}
        
        
            # Continue listening
            try:
                while True:
        
                    events = epol.poll(1)
        
                    for fd, event in events:
                        if fd == serverSock_fd:
                            print("new Connection")
                            # initialize connection with client
                            clientConn, _ = serverSock.accept()
                            clientConn.setblocking(0)
                            client_fd = clientConn.fileno()
        
                            # Register client conn to track
                            epol.register(client_fd, select.EPOLLIN) # Switch to reading
                            connections[client_fd] = clientConn
                            print("Created connection for client")
        
                            ## send connection request to FINAL host (Store state somewhere. possibly another dict)
                            finalConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            finalConn.connect((finalHost, finalPort))
                            finalConn.setblocking(0)
                            final_fd = finalConn.fileno()
                            
                            ## Register final host conn to track
                            epol.register(final_fd, select.EPOLLIN)
                            connections[final_fd] = finalConn
                            print("Created connection to final dest")
        
                            ## Added to limbo dict
                            limbo[client_fd], limbo[final_fd] = finalConn.fileno(), clientConn.fileno()
                            
                            ## testing
                            print(connections[client_fd])
                            print(connections[final_fd])
        
        
                        elif event & select.EPOLLIN:
                            buffer = connections[fd].recv(1024)
                            if buffer == b'':
                                print("This fd needs to close", fd)
                                connections[fd].close()
                                epol.unregister(fd)
                                del connections[fd], limbo[fd]
                            else:
                                connections[limbo[fd]].send(buffer)
        
                        elif event & select.EPOLLHUP:
                            # deregister
                            print("deregistering...")
                            #epol.unregister(limbo[fd])
                            epol.unregister(fd)
        
                            # close
                            print("closing...")
                            #connections[limbo[fd]].close()
                            connections[fd].close()
                            
                            # Release from dicts
                            del connections[fd], limbo[fd]
                            #del connections[limbo[fd]], limbo[limbo[fd]]
                
            finally:
                # Close main socket and epoll
                epol.unregister(serverSock.fileno())
                epol.close()
                serverSock.close()

if __name__ == "__main__":
    
    threads = [] 
    
    connections     = threading.local()
    clientConn      = threading.local()
    client_fd       = threading.local()
    epol            = threading.local()
    event           = threading.local()
    fd              = threading.local()
    final_fd        = threading.local()
    finalConn       = threading.local()
    limbo           = threading.local()
    serverSock      = threading.local()
    serverSock_fd   = threading.local()
    
    # Read static variables from json
    
    with open('config.json', 'r') as f:
        config_settings = json.load(f)
    
    for myConfig in config_settings:
        
        thread = ThreadServer(myConfig['proxyHost'], myConfig['proxyPort'], myConfig['destHost'], myConfig['destPort'],
                             connections, clientConn, client_fd, epol, event, fd, final_fd, finalConn, limbo, 
                             serverSock, serverSock_fd)
        threads += [thread]
        thread.start()
    
    for x in threads: 
        x.join()
