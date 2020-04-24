# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
import numpy as np

#Indicates whether a strip of characters has any digits.
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def extractData(splitted_line): 
    segments = splitted_line.split()
    data = np.ones(len(segments)-1)
    
    for i in range(1,len(segments)):
        if hasNumbers(segments[i]):
            data[i-1] = segments[i].replace(',','.')
        else:
            data[i-1] = np.nan
    
    return data

def extractHead(splitted_line):
    segments = splitted_line.split()
    head = segments[1]
    if len(segments) > 2:
        message = segments[2::]
    else:
        message = []
    return head, message
            
def extractDevice(list_line):
    devices = []
    for i in range(2,len(list_line)):
        if list_line[i] == "Empatica_E4":
            devices.append(list_line[i-1])
    
    return devices

def extractMessages(splitted_line):
    if len(splitted_line):
        if splitted_line.find("\n") == -1:
            msg = splitted_line
            lines = []
        else:
            lines = splitted_line.split("\n")
            msg = lines[-1]
            lines = lines[:-1]
    else:
        msg = ""
        lines = []
        
    return msg,lines
  
