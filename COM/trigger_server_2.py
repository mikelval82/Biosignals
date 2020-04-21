# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
"""
#%%
from PyQt5 import QtCore #conda install pyqt

import socket
import sys

class trigger_server(QtCore.QThread):
    new_COM = QtCore.pyqtSignal()
    
    def __init__(self, address=None, port=None, parent=None):
        super(trigger_server, self).__init__(parent)
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
        print('is socket activated? ', self.activated)
        while self.activated:
            print(sys.stderr, 'waiting for a connection')
            try:
                self.connection, client_address = self.sock.accept()
            except:
                print(sys.stderr, 'Cannot accept connection due to a closed socket state.')
                break
            try:
                print(sys.stderr, 'connection from', client_address)
        
                # Receive the data in small chunks and retransmit it
                while True:
                    data = self.connection.recv(128)
                    print('que estamos recibiendo->', (data!=b''))
                    print('data ', data)
                    print('antes de emitir')
                    if data != b'':
                        self.new_COM.emit()
                        print('tras emitir')
                    # INCOMMING DATA
                    if data:
                        print(sys.stderr, 'received "%s"' % data)
                       
                    else:
                        print(sys.stderr, 'no more data from', client_address)
                        break
            except:
                print('Error while listening')
            finally:
                self.close_socket()
        
    def close_socket(self):  
        print('entro a close socket')
        self.activated = False  
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print('socket is closed!')
        