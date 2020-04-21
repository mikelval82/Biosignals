# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 13:05:39 2018

@author: UNED
"""

from PyQt5.QtCore import QObject, pyqtSignal 

class empatica_signals(QObject):
    ### QT SIGNALS
    device_list_signal = pyqtSignal(list)
    device_connect_signal = pyqtSignal(bool)
    data_pause_signal = pyqtSignal(bool)
    data_subscribe_signal = pyqtSignal(int)
    
    def connect(self, callbacks):
        ### connect signals ######
        self.device_list_signal.connect(callbacks[0])
        self.device_connect_signal.connect(callbacks[1])
        self.data_pause_signal.connect(callbacks[2])
        self.data_subscribe_signal.connect(callbacks[3])
        
    def device_list_emit(self,device_list):
        self.device_list_signal.emit(device_list)
        
    def device_connect_emit(self,device_connect):
        self.device_connect_signal.emit(device_connect)
        
    def data_pause_emit(self,data_pause):
        self.data_pause_signal.emit(data_pause)
        
    def data_subscribe_emit(self,data_subscribe):
        self.data_subscribe_signal.emit(data_subscribe)