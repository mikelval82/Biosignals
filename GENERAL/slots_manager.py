# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
class SlotsManager:
    
    def __init__(self):
        self.callbacks = []
        
    def trigger(self):
        [callback() for callback in self.callbacks]
        
    def append(self, slot):
        self.callbacks.append(slot)
        print(slot)

        
