#!/usr/bin/python
#-*-coding:utf-8-*-

"""
A socket proxy used to forward request-data from src address(host,port)
to dest address(host,port), and forward response-data from dest address
to src address.
request:  src --> proxy --> dest
response: dest --> proxy --> src

author:     iyarkee@gmail.com
version:    1.0 , 2013-01-02
"""

import socket
import select
import logging


def main():
    print("hello")

    # Read static variables from json
    myConfig = configObject('config.json')
    global serverHost, serverPort, finalHost, finalPort
    serverHost = myConfig.serverHost
    serverPort = myConfig.serverPort
    finalHost = myConfig.finalHost
    finalPort = myConfig.finalPort

    ProxyServer()

class configObject:
    def __init__(self, configFile):
        with open(configFile) as config_file:
            data = json.load((config_file))
            self.serverHost = data['server']['host']
            self.serverPort = data['server']['port']
            self.finalHost = data['final']['host']
            self.finalPort = data['final']['port']


def ProxyServer():
        conns, forward_to = {}, {}
    try:
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSock.bind((host, port))
        serverSock.listen(1000)
        serverSock.setblocking(0)

        epol = select.epoll()
        epol.register(serverSock.fileno(), select.EPOLLIN)
    except Exception as e:
        logging.exception('')
        serverSock = None

    try:
        while True:
            events = epol.poll(1)
            for fileno, event in events:
                if fileno == serverSock.fileno():
                    conn, addr = serverSock.accept()
                    logging.info(conn.getpeername())
                    conn.setblocking(0)
                    epol.register(conn.fileno(), select.EPOLLIN)

                    forward_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    forward_sock.connect((finalHost, finalPort))
                    forward_sock.setblocking(0)

                    epol.register(forward_sock.fileno(), select.EPOLLIN)

                    conns[conn.fileno()] = conn
                    conns[forward_sock.fileno()] = forward_sock
                    forward_to[conn.fileno()] = forward_sock.fileno()
                    forward_to[forward_sock.fileno()] = conn.fileno()
                elif event & select.EPOLLIN:
                    data = conns[fileno].recv(1024)
                    to_fileno = forward_to[fileno]
                    to_sock = conns[to_fileno]
                    to_sock.send(data)
                elif event & select.EPOLLHUP:
                    if fileno in forward_to:
                        to_fileno = forward_to[fileno]
                    else:
                        return
                    epol.unregister(fileno)
                    epol.unregister(to_fileno)
                    conns[fileno].close()
                    conns[to_fileno].close()
                    del conns[fileno], conns[to_fileno], forward_to[fileno], forward_to[to_fileno]
    finally:
        epol.unregister(serverSock.fileno())
        epol.close()
        serverSock.close()

if __name__ == '__main__':
    main()
