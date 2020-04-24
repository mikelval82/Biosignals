# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from COM.trigger_client import trigger_client

tc_fer = trigger_client('10.1.28.117',10000)
tc_fer.create_socket()
tc_fer.connect()

tc_eeg = trigger_client('10.1.28.117',10001)
tc_eeg.create_socket()
tc_eeg.connect()
#%%
tc_fer.send_msg(b'start')
tc_eeg.send_msg(b'start')
#%%
tc_fer.send_msg(b'stop')
tc_eeg.send_msg(b'stop')
#%%
tc_fer.close_socket()
tc_eeg.close_socket()
