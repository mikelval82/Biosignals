# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from PyQt5 import QtCore #conda install pyqt

import socket
import sys

class trigger_server(QtCore.QThread):
    socket_emitter = QtCore.pyqtSignal(str)
    log_emitter = QtCore.pyqtSignal(str)
    
    def __init__(self, constants, parent=None):
        super(trigger_server, self).__init__(parent)
        self.constants = constants
        self.activated = False
        self.server_address = None
             
    def create_socket(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        self.server_address = (self.constants.ADDRESS, self.constants.PORT)
        self.log_emitter.emit(' starting up on %s port %s' % self.server_address)
        try:
            self.sock.bind(self.server_address)
            self.activated = True
        except socket.gaierror:
            self.log_emitter.emit('[Errno -2] Unknown name or service')
        finally:
            return self.activated
    
    def run(self):
        # Listen for incoming connections
        self.log_emitter.emit('Socket is listening!')
        self.sock.listen(1)

        while self.activated:
            self.log_emitter.emit('Waiting for a connection')
            try:
                self.connection, client_address = self.sock.accept()
                self.log_emitter.emit('connection accepted from %s port %s ' % client_address)
            except:
                self.log_emitter.emit('Cannot accept connection due to a closed socket state.')
                break
            try:
                print(sys.stderr, 'connection from', client_address)
        
                # Receive the data in small chunks and retransmit it
                while True:
                    data = self.connection.recv(128)
                    if data != b'':
                        self.socket_emitter.emit(data.decode())
                    # INCOMMING DATA
                    if data:
                        self.log_emitter.emit('received "%s"' % data)
                    else:
                        self.log_emitter.emit('no more data from ' + client_address)
                        break
            except:
                self.log_emitter.emit('Error while listening')
            finally:
                self.close_socket()
        
    def close_socket(self):  
        self.activated = False  
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.log_emitter.emit('Socket is closed!')
        
