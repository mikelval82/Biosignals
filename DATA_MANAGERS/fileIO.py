# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
import pandas as pd
import csv

def create_csvFile(path):
    print('path: ', path)
    with open(path, 'wb') as csvfile:
        csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
def append_to_csvFile(trial, allData, path, columns, control):
    
    data = []
    for i in range(len(allData)):
        aux = [trial]
        for j in range(allData[i].shape[0]): aux.append(allData[i][j])
        data.append(aux)
        
    dataframe = pd.DataFrame(data, columns = columns)
    
    with open(path, 'a') as f:
        dataframe.to_csv(f, index=False, header=control)
  
