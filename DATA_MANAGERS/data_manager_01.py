# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from EDF.writeEDFFile import edf_writter
#from DATA_MANAGERS import fileIO as io
from threading import Lock
import numpy as np
import math

class data_manager():
   
    def __init__(self, signal=None, signal_numbers=None, seconds_max=None, seconds=None, sample_rate=None, block_size=None, delay_max=None):
        ############### CONSTANTS ######################  
        self.PATH = None
        self.SIGNAL = signal
        self.SIGNAL_NUMBERS = signal_numbers
        self.SECONDS_MAX = seconds_max
        self.SECONDS = seconds
        self.SAMPLE_RATE = sample_rate         
        self.BLOCK_SIZE = block_size
        self.WINDOW = self.SAMPLE_RATE*self.SECONDS 
        self.DELAY_MAX = self.BLOCK_SIZE + 1 + self.SAMPLE_RATE*delay_max
        ############### data save trigger
        self.io = edf_writter(self.SIGNAL_NUMBERS+1, self.SAMPLE_RATE)
        self.allData = []
        self.current_trial = 0
        ############### buffer ########################
        self.max = self.SAMPLE_RATE*self.SECONDS_MAX + self.DELAY_MAX
        self.data = np.ones((self.max,self.SIGNAL_NUMBERS+1))*np.nan
        self.cur_append = self.max-1
        self.cur_get = self.max-1
        self.cur_index = 0
        self.pending = 0
        self.overflow = False  
        self.isstored = True
        self.trigger_control = None
        ##############Frequency of plotting tasks (max 25Hz) and samples to be returned by the get.
        self.nGet = math.ceil(self.SAMPLE_RATE/24)
        if self.nGet == 1:
            self.freqTask = self.SAMPLE_RATE
        else:
            self.freqTask = self.SAMPLE_RATE/self.nGet
        ###### mutex lock
        self.mutexBuffer = Lock()
        
    def create_file(self):
        self.io.new_file(self.PATH + '_' + self.SIGNAL + '_trial_' + str(self.current_trial) + '.edf')        
               
    def close_file(self):
        self.io.close_file()
        
    def reset_data_store(self):
        self.allData = []
        
    def online_annotation(self, notation):       
        instant = self.cur_index/self.SAMPLE_RATE# alo mejor NO es cur_append
        duration = -1
        event = notation
        self.io.annotation(instant, duration, event)
        
    def save_streamData(self):           
        if self.SIGNAL == 'bvp':
            columns = ['time','bvp']
        elif self.SIGNAL == 'gsr':
            columns = ['time','gsr']
        elif self.SIGNAL == 'tmp':
            columns = ['time','tmp']
        elif self.SIGNAL == 'acc':
            columns = ['time','x','y','z']
            
        self.io.append(self.allData,columns)
        self.io.writeToEDF()
        
    def setWindow(self,seconds):
        self.mutexBuffer.acquire()
        self.SECONDS = seconds
        self.WINDOW = self.SAMPLE_RATE * self.SECONDS
        self.mutexBuffer.release()
        
    def getWindow(self):
        return self.WINDOW
    
    def clearBuffer(self):
        self.mutexBuffer.acquire()
        self.data *= np.nan;
        self.cur_append = self.max-1
        self.cur_get = self.max-1
        self.pending = 0
        self.overflow = False
        self.mutexBuffer.release()
    
    def appendSample(self,sample):
        self.mutexBuffer.acquire()
        self.cur_append += 1
        self.cur_index +=1
        if self.cur_append >= self.max:
            self.overflow = True
            self.cur_append = 0
            
#        if ((self.cur_index/self.SAMPLE_RATE) % 12 == 0) and (not self.trigger_control):
#            self.online_annotation('window')
            
        self.data[self.cur_append] = sample
        self.pending += 1
        #Resets when it exceeds the maximum delay
        if self.pending > self.DELAY_MAX:
            self.data *= np.nan;
            self.cur_append = self.max-1
            self.cur_get = self.max-1
            self.pending = 0
            self.overflow = False
        self.mutexBuffer.release()
        
    def getSamples(self):
        self.mutexBuffer.acquire()
        self.cur_get += self.nGet
        self.pending -= self.nGet
        #if more than the block size is left pending, two samples are taken to recover
        if self.pending >= self.BLOCK_SIZE:
            self.cur_get += 1
            self.pending -= 1
        #It prevents the get cursor from overcoming the append cursor
        if not self.overflow and self.cur_get > self.cur_append:
            self.cur_get = self.cur_append
            self.pending = 0
        #it checks if there is overflow
        if self.cur_get >= self.max:
            self.overflow = False
            self.cur_get = self.cur_get % self.max                  
        #the size data of the window is taken to plot.
        init = self.cur_get - self.WINDOW + 1
        if init >= 0:
            plot_data = np.copy(self.data[init:self.cur_get+1])
        else:
            plot_data = np.copy( np.concatenate((self.data[self.max+init:],self.data[:self.cur_get+1]),axis=0))
        self.mutexBuffer.release()       
        return plot_data
    
