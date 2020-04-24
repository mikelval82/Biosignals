# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from EDF.writeEDFFile import edf_writter
from GENERAL.ring_buffer_02 import RingBuffer as buffer
from threading import Lock

class data_manager():
   
    def __init__(self, signal=None, signal_numbers=None, seconds=None, sample_rate=None):
        ############### CONSTANTS ######################  
        self.PATH = None
        self.SIGNAL = signal
        self.SIGNAL_NUMBERS = signal_numbers
        self.SECONDS = seconds
        self.SAMPLE_RATE = sample_rate         
        self.WINDOW = self.SAMPLE_RATE*self.SECONDS 
        self.freqTask = self.SAMPLE_RATE
        ############### data save trigger
        self.io = edf_writter(self.SIGNAL_NUMBERS+1, self.SAMPLE_RATE)
        self.allData = []
        self.current_trial = 0
        ############### buffer ########################
        self.buffer = buffer(channels=self.SIGNAL_NUMBERS+1, num_samples=self.WINDOW, sample_rate=self.SAMPLE_RATE)
#        self.trigger_control = None
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
        self.buffer.reset()
        self.mutexBuffer.release()
    
    def appendSample(self,sample):
        self.mutexBuffer.acquire()            
        self.buffer.append(sample)
        self.mutexBuffer.release()
        
    def getSamples(self):
        self.mutexBuffer.acquire()
        plot_data = self.buffer.get()
        self.mutexBuffer.release()       
        return plot_data
    
