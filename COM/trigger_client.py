# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
import socket
import sys

class trigger_client():
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
            print(sys.stderr, 'sending "%s"' % message)
            self.sock.sendall(message)
        except:
            print('Error sending the message tcp/ip')
        
    def close_socket(self):
        print(sys.stderr, 'closing socket')
        self.sock.close()
        



