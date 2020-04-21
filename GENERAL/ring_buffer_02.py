#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
"""
from PyQt5 import QtCore 
import numpy as np
import copy

class RingBuffer(QtCore.QThread):
    """ class that implements a not-yet-full buffer """
    emitter = QtCore.pyqtSignal()
    
    def __init__(self, channels=None, num_samples=None, sample_rate = None, parent=None):
        super(RingBuffer, self).__init__(parent)
        self.channels = channels
        self.max = num_samples
        self.data = np.zeros((self.max, self.channels))
        self.cur = copy.copy(self.max)
        self.cur_show = copy.copy(self.max)
        self.sample_rate = sample_rate   
        self.seconds = 6
        self.control = self.sample_rate*self.seconds
         
    def reset(self):
        self.data = np.zeros((self.max, self.channels))
        self.cur = copy.copy(self.max)
        self.cur_show = copy.copy(self.max)
        
    def append(self,x):
        """append an element at the end of the buffer"""  
        self.cur = self.cur % self.max
        self.data[self.cur,:] = np.array(x)
        self.cur = self.cur+1
        if self.cur_show > 0:
            self.cur_show -= 1
        if (self.cur_show == 0) and ((self.cur % self.control) == 0):
            self.emitter.emit()  

    def get(self):
        """ Return a list of elements from the oldest to the newest. """ 
        data = np.vstack((self.data[self.cur:,:], self.data[:self.cur,:]))
        data = data[self.cur_show:,:]
        return data
    
    
