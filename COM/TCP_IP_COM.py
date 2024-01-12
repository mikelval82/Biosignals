# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from threading import Event, Thread
import socket
import time
from COM.communication_signals import empatica_signals
from GENERAL import preprocessing as pre
from typing import List, Tuple

class mysocket(Thread):
    """
    Custom socket handling thread.
    This class extends the Thread class to handle socket communication.
    """

    def __init__(self, log, dmgs, callbacks):
        """
        Initialize a new socket handling thread.

        :param log: Logger object for logging messages.
        :param dmgs: List of data manager objects.
        :param callbacks: Callback functions for communication signals.
        """
        Thread.__init__(self)
        self.log = log
        self.dmgs = dmgs
        self.exit = Event()
        self.flag = Event()
        self.com_signals = empatica_signals()
        self.com_signals.connect(callbacks)
        self.device_list: List[str] = []
        self.device_connect: bool = False
        self.data_pause: bool = False
        self.data_subscribe: int = 0
        self.stream_subscribe: List[bool] = [False, False, False, False]
        self.count_subscribe: int = 0
        self.error_subscribe: bool = False

    def run(self):
        msg = ''
        while not self.exit.is_set():
            msg += self.sock.recv(8).decode('utf8')
            msg, lines = pre.extractMessages(msg)
            if len(lines):
                for i in range(0, len(lines)):
                    # message
                    if lines[i][0] == 'R':
                        self.log.myprint_in(lines[i])
                        head, message = pre.extractHead(lines[i])
                        if head == "device_list":
                            self.device_list = pre.extractDevice(message)
                            self.com_signals.device_list_emit(self.device_list)
                        elif head == "device_connect":
                            if message[0] == "OK":
                                self.device_connect = True
                            elif message[0] == "ERR":
                                self.log.myprint_error(message[1] + '\r\n')
                            self.com_signals.device_connect_emit(self.device_connect)
                        elif head == "device_disconnect":
                            if message[0] == "OK":
                                self.device_connect = False
                            elif message[0] == "ERR":
                                self.log.myprint_error(message[1] + '\r\n')
                            self.com_signals.device_connect_emit(self.device_connect)
                        elif head == "pause":
                            if message[0] == "ON":
                                self.data_pause = True
                            elif message[0] == "OFF":
                                self.data_pause = False
                            elif message[0] == "ERR":
                                self.log.myprint_error(message[1] + '\r\n')
                            self.com_signals.data_pause_emit(self.data_pause)
                        elif head == "device_subscribe":
                            self.count_subscribe += 1
                            if message[0] == "bvp":
                                ind = 0
                            elif message[0] == "gsr":
                                ind = 1
                            elif message[0] == "tmp":
                                ind = 2
                            elif message[0] == "acc":
                                ind = 3
                            else:
                                ind = -1
                            if message[1] == "ERR":
                                self.error_subscribe = True
                                self.log.myprint_error(message[2] + '\r\n')
                            elif ind == -1:
                                self.error_subscribe = True
                                self.log.myprint_error('The stream is not identified\r\n')
                            else:
                                self.stream_subscribe[ind] = True
                            if self.count_subscribe == 4:
                                self.count_subscribe = 0
                                if self.error_subscribe:
                                    self.data_subscribe = -1
                                else:
                                    if all(self.stream_subscribe):
                                        self.data_subscribe = 1
                                    else:
                                        self.data_subscribe = 0
                                self.com_signals.data_subscribe_emit(self.data_subscribe)
                        else:
                            self.log.myprint_error('The message ' + head + ' is unknown\r\n')
                    # Data stream
                    else:
                        if lines[i][0:6] == 'E4_Bvp':
                            ind = 0
                        elif lines[i][0:6] == 'E4_Gsr':
                            ind = 1
                        elif lines[i][0:6] == 'E4_Tem':
                            ind = 2
                        elif lines[i][0:6] == 'E4_Acc':
                            ind = 3
                        else:
                            ind = -1

                        if ind >= 0:
                            data = pre.extractData(lines[i])
                            self.dmgs[ind].appendSample(data)

                            if self.flag.is_set():
                                self.dmgs[ind].allData.append(data)

        # finally
        self.sock.close()
        self.log.myprint('Killing thread')

    def listDevice(self):
        """
        Send a message to list available devices.

        :return: None
        """
        message = 'device_list\r\n'
        self.send_msg(message)

    def connectDevice(self, device: str):
        """
        Send a message to connect to a specific device.

        :param device: Device identifier.
        :return: None
        """
        message = 'device_connect ' + device + '\r\n'
        self.send_msg(message)

    def disconnectDevice(self):
        """
        Send a message to disconnect from the currently connected device.

        :return: None
        """
        message = 'device_disconnect\r\n'
        self.send_msg(message)

    def pause(self, state: str):
        """
        Send a message to pause or resume data streaming.

        :param state: 'ON' to pause, 'OFF' to resume.
        :return: None
        """
        message = 'pause ' + state + '\r\n'
        self.send_msg(message)

    def subscribe(self, action: str):
        """
        Send subscription messages for each data manager.

        :param action: 'START' or 'STOP' for subscribing or unsubscribing.
        :return: None
        """
        for dmg in self.dmgs:
            message = 'device_subscribe ' + dmg.SIGNAL + ' ' + action + '\r\n'
            self.send_msg(message)
            time.sleep(0.1)

    def openPort(self, IP: str, PORT: int):
        """
        Open a socket connection to the specified IP address and port.

        :param IP: IP address to connect to.
        :param PORT: Port number to connect to.
        :return: None
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (IP, PORT)
        self.sock.connect(server_address)
        self.log.myprint("Connected to Empatica Server")

    def closePort(self):
        """
        Close the socket connection and set the exit flag.

        :return: None
        """
        self.exit.set()
        self.log.myprint("Connection closure with the Empatica Server")

    def send_msg(self, message: str):
        """
        Send a message to the connected socket.

        :param message: Message to be sent.
        :return: None
        """
        self.log.myprint_out(message[0:len(message) - 2])
        self.sock.send(message.encode('utf-8'))

    def __del__(self):
        """
        Destructor for the mysocket thread instance.

        :return: None
        """
        self.log.myprint("Destroying mysocket thread instance -> ")

