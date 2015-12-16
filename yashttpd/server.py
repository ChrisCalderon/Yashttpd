import socket
import sys
from poller import Poller
from client import Client

NEW_CLIENTS = 10

class Server:
    def __init__(self, ip_port):
        listener = socket.socket()
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        listener.bind(ip_port)
        listener.listen(NEW_CLIENTS)
        self.listener = listener
        poller = Poller()
        poller.add(listener)
        self.poller = poller

    def accept_clients():
        for _ in range(NEW_CLIENTS):
            poller.add(Client(self.listener.accept()[0]))
        
    def mainloop(ip_port):
        try:
            while True:
                for sock in self.poller.readables(0.5):
                    if sock == self.listener:
                        self.accept_clients()
                    else:
                        
