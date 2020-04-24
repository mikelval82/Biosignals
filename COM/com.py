# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from tcpip_dict_client import tcpip_client as client
import numpy as np

port = 10000

client = client('10.1.28.117', port)
client.create_socket()
client.connect()

eeg = np.random.rand(8,20)
bvp = np.random.rand(12,1)
gsr = np.random.rand(2,1)
faces = np.random.rand(48,48,24)

msg = {'eeg':eeg, 'BVP':bvp, 'gsr':gsr, 'faces':faces}
client.send_msg(msg)
#%%
from tcpip_server import tcpip_server as server
from tcpip_client import tcpip_client as client
import numpy as np

port = 9999
#%%
server = server('10.1.28.117', port)
server.create_socket()
server.start()

#%%
client = client('10.1.28.117', port)
client.create_socket()
client.connect()

#%%
eeg = np.random.rand(8,20)
bvp = np.random.rand(12,1)
gsr = np.random.rand(2,1)
faces = np.random.rand(48,48,24)

msg = {'eeg':eeg, 'BVP':bvp, 'gsr':gsr, 'faces':faces}
client.send_msg(msg)

#%%
client.close_socket()
server.close_socket()

