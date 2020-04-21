# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
"""
#%%

import socket
import sys
import pickle

class tcpip_client():
    
    HEADERSIZE = 10

    def __init__(self, address, port):
        self.address = address
        self.port = port
        
    def create_socket(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        # Connect the socket to the port where the server is listening
        server_address = (self.address, self.port)
        print (sys.stderr, 'connecting to %s port %s' % server_address)
        self.sock.connect(server_address)
    
    def send_msg(self, message):
        try:          
            # Send data
            msg = pickle.dumps(message)
            msg = bytes(f"{len(msg):<{self.HEADERSIZE}}", 'utf-8')+msg
#            print(sys.stderr, 'sending "%s"' % msg)
            self.sock.sendall(msg)
        except:
            print('Error sending the message tcp/ip')
        
    def close_socket(self):
        print(sys.stderr, 'closing socket')
        self.sock.close()
        