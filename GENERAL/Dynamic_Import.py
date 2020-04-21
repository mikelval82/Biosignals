#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 14:56:41 2018

@author: mikel
"""

import sys 
import os
import importlib
    
def load_module(fileName, app):
    ########### separo path y nombre del modulo ##############
    aux = fileName.split("/")
    path = '/'
    for i in range(1, len(aux)-1):
        path += aux[i] + '/'
    module_name = aux[-1][:-3]
    #---------------------------------------------------------
    sys.path.append(os.path.realpath('./MODULES/'))
    module = importlib.import_module(module_name)
    custom_object = module.pipeline(app)
    try:
        custom_object.start()
    except:
        print('Loaded module must have a callable -> execute() <- function')    
    #################################################################
    

