# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
"""
#%%
from PyQt5 import QtCore 

import socket
import sys
import pickle

class tcpip_server(QtCore.QThread):
    
    HEADERSIZE = 10
    
    def __init__(self, address, port, parent=None):
        super(tcpip_server, self).__init__(parent)
        self.address = address
        self.port = port
        self.activated = False
             
    def create_socket(self):
        self.activated = True
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        server_address = (self.address, self.port)
        print(sys.stderr, 'starting up on %s port %s' % server_address)
        self.sock.bind(server_address)
        
    
    def run(self):
        # Listen for incoming connections
        print('socket is listening!')
        self.sock.listen(1)
        while self.activated:
            print(sys.stderr, 'waiting for a connection')
            try:
                self.connection, client_address = self.sock.accept()
            except:
                print(sys.stderr, 'Cannot accept connection due to a closed socket state.')
                break
            try:
                print(sys.stderr, 'connection from', client_address)
        
                full_msg = b''
                new_msg = True
                while True:
                    msg = self.connection.recv(16)
                    if new_msg:
#                        print("new msg len:",msg[:self.HEADERSIZE])
                        msglen = int(msg[:self.HEADERSIZE])
                        new_msg = False
            
#                    print(f"full message length: {msglen}")
            
                    full_msg += msg
            
#                    print(len(full_msg))
            
                    if len(full_msg)-self.HEADERSIZE == msglen:
#                        print("full msg recvd")
#                        print(full_msg[self.HEADERSIZE:])
                        dictionary = pickle.loads(full_msg[self.HEADERSIZE:])
                        print(dictionary.keys())
                        for key in dictionary.keys():
                            print(dictionary[key].shape)
                        new_msg = True
                        full_msg = b""
            except:
                print('Error while listening')
            finally:
                self.close_socket()
        
    def close_socket(self):  
        self.activated = False  
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print('socket is closed!')
        
