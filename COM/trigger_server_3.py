# -*- coding: utf-8 -*-
"""
A PyQt5-based trigger server for receiving data over a TCP/IP socket.
@author: Mikel Val Calvo
@email: mikel1982mail@gmail.com
@institution: Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED)
@DOI: 10.5281/zenodo.3759262
"""
# Import necessary modules
from PyQt5 import QtCore  # conda install pyqt
import socket
import sys


class TriggerServer(QtCore.QThread):
    """
    A class representing a trigger server using PyQt5 and a TCP/IP socket.

    Attributes:
    - constants (object): An object containing server configuration constants.
    - activated (bool): Flag indicating whether the server is activated or not.
    - server_address (tuple): A tuple containing the server address (IP address, port).

    Signals:
    - socket_emitter (str): Signal emitted when data is received from the socket.
    - log_emitter (str): Signal emitted to log messages.

    Methods:
    - create_socket(): Create and bind a TCP/IP socket.
    - run(): Start listening for incoming connections and data.
    - close_socket(): Close the socket and deactivate the server.
    """

    socket_emitter = QtCore.pyqtSignal(str)
    log_emitter = QtCore.pyqtSignal(str)

    def __init__(self, constants, parent=None):
        super(TriggerServer, self).__init__(parent)
        self.constants = constants
        self.activated = False
        self.server_address = None

    def create_socket(self) -> bool:
        """
        Create and bind a TCP/IP socket to the specified address and port.

        Returns:
        - bool: True if the socket is successfully created and bound, False otherwise.
        """
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        self.server_address = (self.constants.ADDRESS, self.constants.PORT)
        self.log_emitter.emit('Starting up on %s port %s' % self.server_address)
        try:
            self.sock.bind(self.server_address)
            self.activated = True
        except socket.gaierror:
            self.log_emitter.emit('[Errno -2] Unknown name or service')
        finally:
            return self.activated

    def run(self):
        """
        Start listening for incoming connections and data.
        """
        # Listen for incoming connections
        self.log_emitter.emit('Socket is listening!')
        self.sock.listen(1)

        while self.activated:
            self.log_emitter.emit('Waiting for a connection')
            try:
                self.connection, client_address = self.sock.accept()
                self.log_emitter.emit('Connection accepted from %s port %s' % client_address)
            except:
                self.log_emitter.emit('Cannot accept connection due to a closed socket state.')
                break
            try:
                print(sys.stderr, 'Connection from', client_address)

                # Receive the data in small chunks and retransmit it
                while True:
                    data = self.connection.recv(128)
                    if data != b'':
                        self.socket_emitter.emit(data.decode())
                    # INCOMING DATA
                    if data:
                        self.log_emitter.emit('Received "%s"' % data)
                    else:
                        self.log_emitter.emit('No more data from ' + client_address)
                        break
            except:
                self.log_emitter.emit('Error while listening')
            finally:
                self.close_socket()

    def close_socket(self):
        """
        Close the socket and deactivate the server.
        """
        self.activated = False
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.log_emitter.emit('Socket is closed!')
