# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 15:26:41 2018

@author: UNED
"""
from EDF.writeEDFFile import edf_writter
from DATA_MANAGERS import fileIO as io
from threading import Lock
import numpy as np
import math

class data_manager():
   
    def __init__(self, signal=None, signal_numbers=None, seconds_max=None, seconds=None, sample_rate=None, block_size=None, delay_max=None):
        ##################### user path  ##############################
        self.path = ''
        ############### CONSTANTS ######################  
        self.SIGNAL = signal
        self.SIGNAL_NUMBERS = signal_numbers
        self.SECONDS_MAX = seconds_max
        self.SECONDS = seconds
        self.SAMPLE_RATE = sample_rate         
        self.BLOCK_SIZE = block_size
        self.WINDOW = self.SAMPLE_RATE*self.SECONDS 
        self.DELAY_MAX = self.BLOCK_SIZE + 1 + self.SAMPLE_RATE*delay_max
        ############### data save trigger
        self.allData = []
        self.current_trial = 0
        self.running_window = 0
        ############### buffer ########################
        self.max = self.SAMPLE_RATE*self.SECONDS_MAX + self.DELAY_MAX
        self.data = np.ones((self.max,self.SIGNAL_NUMBERS+1))*np.nan
        self.cur_append = self.max-1
        self.cur_get = self.max-1
        self.pending = 0
        self.overflow = False  
        self.isstored = True
        ##############Frequency of plotting tasks (max 25Hz) and samples to be returned by the get.
        self.nGet = math.ceil(self.SAMPLE_RATE/24)
        if self.nGet == 1:
            self.freqTask = self.SAMPLE_RATE
        else:
            self.freqTask = self.SAMPLE_RATE/self.nGet
        ###### mutex lock
        self.mutexBuffer = Lock()
        
    def create_file(self):
        io.create_csvFile(self.path)
        
    def save_streamData(self):           
        if self.SIGNAL == 'bvp':
            columns = ['trial','time','bvp']
        elif self.SIGNAL == 'gsr':
            columns = ['trial','time','gsr']
        elif self.SIGNAL == 'tmp':
            columns = ['trial','time','tmp']
        elif self.SIGNAL == 'acc':
            columns = ['trial','time','x','y','z']
            
        io.append_to_csvFile(self.current_trial, self.allData, self.path, columns, self.isstored)
        if self.isstored:
            self.isstored = False
        
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
        if self.cur_append >= self.max:
            self.overflow = True
            self.cur_append = 0
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
        

#%%
#    def create_file(self):
#        self.io.new_file(self.app.constants.PATH + '_trial_' + str(self.app.constants.running_trial) + '.edf')
#        self.app.log.update_text('* -- USER ' + self.app.constants.PATH + ' CREATED -- *')
#        
#    def close_file(self):
#        self.io.close_file()
#        self.app.log.update_text('* -- USER ' + self.app.constants.PATH + ' CLOSED -- *')
#        
#    def reset_data_store(self):
#        self.all_data_store = np.empty(shape=(self.app.constants.CHANNELS, 0))
#        
#    def online_annotation(self, notation):
#        instant = self.app.constants.running_window*self.app.constants.SECONDS + (self.app.buffer.cur % self.app.buffer.size_short)/self.app.constants.SAMPLE_RATE
#        duration = -1
#        event = notation
#        self.io.annotation(instant, duration, event)
#        
#    def append_to_store(self):
#        sample_data = self.get_short_sample(self.app.constants.METHOD)
#        self.all_data_store = np.hstack((self.all_data_store, sample_data))  
#        instant = self.app.constants.running_window*self.app.constants.SECONDS
#        duration = -1
#        self.app.log.update_text('* -- last action in eeg_dmg: ' + str(self.app.constants.last_action) + ' -- *')
#        event = self.app.constants.last_action
##        self.io.annotation(instant, duration, event)
#
#        self.app.constants.running_window += 1
#        
#    def append_to_file(self):# tarda mucho en guardar, probar hilos o guardar en variable allData hasta terminar registro y luego guardar en archivo
#        if self.app.constants.ispath:
#            # save EDF trial file
#            self.io.append(self.all_data_store)
#            self.io.writeToEDF()
#            # re-initialize
#            self.all_data_store = np.empty(shape=(self.app.constants.CHANNELS, 0))
#            # update metadata
#            self.app.constants.running_trial += 1
#            if self.app.constants.isstored:
#                self.app.constants.isstored = False
#        else:
#            self.app.log.update_text('* -- EDF file path is needed -- *')