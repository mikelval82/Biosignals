# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from __future__ import division, print_function, absolute_import

import os
import numpy as np
import pyedflib

class edf_writter:
    
    def __init__(self, CHANNELS, SAMPLE_RATE):
        self.CHANNELS = CHANNELS
        self.SAMPLE_RATE = SAMPLE_RATE
        
    def new_file(self,path):
        data_file = os.path.join('.', path)
        self.file = pyedflib.EdfWriter(data_file, self.CHANNELS, file_type=pyedflib.FILETYPE_EDFPLUS)
        
        self.channel_info = []
        self.data_list = []
        
    def append(self, all_data_store, channel_IDs):
        for channel in range(len(channel_IDs)):
            if channel_IDs[channel] == 'time':
                dimension = 'seconds'
            elif channel_IDs[channel] == 'bvp':
                dimension = 'mili_volts'
            elif channel_IDs[channel] == 'gsr':
                dimension = 'micro_siemens'
            elif channel_IDs[channel] == 'tmp':
                dimension = 'grades'
            elif channel_IDs[channel] == 'x' or channel_IDs[channel] == 'y' or channel_IDs[channel] == 'z':
                dimension = 'meters'
                
            ch_dict = {'label': channel_IDs[channel], 'dimension': dimension, 'sample_rate': self.SAMPLE_RATE, 'physical_max': np.asarray(all_data_store)[:,channel].max(), 'physical_min': np.asarray(all_data_store)[:,channel].min(), 'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
            self.channel_info.append(ch_dict)
            self.data_list.append(np.asarray(all_data_store)[:,channel])

    def writeToEDF(self):
        self.file.setSignalHeaders(self.channel_info)
        self.file.writeSamples(self.data_list)
        
    def annotation(self, instant, duration, event):
        print('edf writer event: ', event, ' instant: ', str(instant))
        self.file.writeAnnotation(instant, duration, event)
        
    def close_file(self):
        self.file.close()
        del self.file
        
    def __del__(self):
        print("deleted")
