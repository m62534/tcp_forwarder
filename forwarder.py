#!/usr/bin/python3

import json
import socket
import select
import logging
import subprocess
import os
import re
import threading
import sys

class ThreadServer(threading.Thread):
    lock = threading.Lock()
    
    def __init__(self, proxyHost, proxyPort, destHost, destPort, connections, clientConn, client_fd, epol, event, fd, final_fd, finalConn, limbo, serverSock, serverSock_fd):
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
            logging.debug('ThreadSever started...')
            
            logging.debug("  Proxy Host: {}".format(self.proxyHost))
            logging.debug("  Proxy Port {}".format(self.proxyPort))
            logging.debug("  Dest Host: {}".format(self.destHost))
            logging.debug("  Dest Port: {}".format(self.destPort))
            
            # Create server socket
            serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logging.debug("Attempting to bind self.proxyHost: {0} and self.proxyPort: {1}".format(self.proxyHost, self.proxyPort))
            try:
                serverSock.bind((self.proxyHost, self.proxyPort))
                serverSock.listen(5)
                serverSock.setblocking(0) # non-blocking
            except Exception as e1:
                # Create epoll object
                logging.debug("FAILED registering bind listen block...")
                sys.exit()
            
            epol = select.epoll()
            
            try:
                # Associate with server socket file descriptor to the epoll object
                epol.register(serverSock.fileno(), select.EPOLLIN)
                logging.debug("server associated with epoll object")
            except Exception as e1:
                # Create epoll object
                logging.debug("FAILED registering epol fd register...")
                sys.exit()
            
            
            # Instantiate
            connections, serverSock_fd = {}, serverSock.fileno()
        
            # Instantiate final dict for final host fd tracking
            limbo = {}
        
        
            # Continue listening
            try:
                while True:
                    logging.debug("polling...")
                    events = epol.poll(1)
        
                    for fd, event in events:
                        logging.debug('event registered in thread')
                        if fd == serverSock_fd:
                            logging.debug("new Connection")
                            # initialize connection with client
                            clientConn, _ = serverSock.accept()
                            clientConn.setblocking(0)
                            client_fd = clientConn.fileno()
        
                            # Register client conn to track
                            epol.register(client_fd, select.EPOLLIN) # Switch to reading
                            connections[client_fd] = clientConn
                            logging.debug("Created connection for client")
        
                            ## send connection request to FINAL host (Store state somewhere. possibly another dict)
                            finalConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            finalConn.connect((self.destHost, self.destPort))
                            finalConn.setblocking(0)
                            final_fd = finalConn.fileno()
                            
                            ## Register final host conn to track
                            epol.register(final_fd, select.EPOLLIN)
                            connections[final_fd] = finalConn
                            logging.debug("Created connection to final dest")
        
                            ## Added to limbo dict
                            limbo[client_fd], limbo[final_fd] = finalConn.fileno(), clientConn.fileno()
                            
                            ## Show new connection objects
                            print(connections[client_fd])
                            print(connections[final_fd])
        
        
                        elif event & select.EPOLLIN:
                            buffer = connections[fd].recv(1024)
                            if buffer == b'':
                                logging.debug("Closing this fd: {}".format(fd))
                                connections[fd].close()
                                connections[limbo[fd]].close()
                                epol.unregister(fd)
                                epol.unregister(limbo[fd])
                                del connections[fd], connections[limbo[fd]], limbo[fd], limbo[limbo[fd]]
                            else:
                                if fd in limbo:
                                    connections[limbo[fd]].send(buffer)
        
                        elif event & select.EPOLLHUP:
                            # deregister
                            logging.debug("deregistering...")
                            epol.unregister(fd)
        
                            # close
                            logging.debug("closing...")
                            #connections[limbo[fd]].close()
                            connections[fd].close()

                            # Release from dicts
                            del connections[fd], limbo[fd]

            except Exception as e:
                print(e)
            finally:
                # Close main socket and epoll
                epol.unregister(serverSock.fileno())
                epol.close()
                serverSock.close()

if __name__ == "__main__":
    
    threads = [] 
    logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
    
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
    try:
        with open('config.json', 'r') as f:
            config_settings = json.load(f)
        
        for myConfig in config_settings:            
            thread = ThreadServer(myConfig['proxyHost'], myConfig['proxyPort'], myConfig['destHost'], myConfig['destPort'], connections, clientConn, client_fd, epol, event, fd, final_fd, finalConn, limbo, serverSock, serverSock_fd)
            thread.daemon = True
            threads += [thread]
            thread.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        for x in threads:
            x.join()
        sys.exit()
