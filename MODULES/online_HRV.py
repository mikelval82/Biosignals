# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from threading import Thread
#from multiprocessing import Process
from COM.tcpip_dict_client import tcpip_client as client
from HRV import pybvp 
from GSR import pygsr

class pipeline(Thread):
    
    def __init__(self, app):
        Thread.__init__(self)
        self.app = app
        self.dmgs = self.app.gui.getDmgs()
        # -- tcpip dict client settings --
        self.client = client(self.app.toADDRESS, self.app.PORT)
        self.client.create_socket()
        self.client.connect()

    def run(self):
        print('modulo cargado')
        self.app.slots.append(self.send_data)
        
    def send_data(self):
        print('sending data')
        # get data
        bvp = self.dmgs[0].getSamples()
        gsr = self.dmgs[1].getSamples()
        # compute BVP features
        nni = pybvp.compute_nni(bvp[:,1])
        bvp_features = pybvp.compute_features(nni)
        # compute GSR features
        gsr_data = pygsr.extract_gsr_components(gsr)
        fs = 8
        seconds = len(gsr_data)/fs
        gsr_tonic_features = pygsr.compute_tonic_features(gsr_data['tonic'],fs,seconds,overlap=1)
        gsr_tonic_features
        # send dictionary data
        msg={'bvp':bvp_features, 'gsr':gsr_tonic_features}
        self.client.send_msg(msg)
        print('data sended')
        
        
    
