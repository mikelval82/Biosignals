#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
"""
from scipy.signal import savgol_filter
import scipy.signal as scisig
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def extract_gsr_components(gsr_data):
    gsr_data = pd.DataFrame(gsr_data, columns=['datetime','EDA'])
    sampleRate = 4#Hz
    startTime = gsr_data.iloc[0,0]
    # Make sure data has a sample rate of 8Hz
    gsr_data = interpolateDataTo8Hz(gsr_data,sampleRate,startTime)    
    rolling_mean = gsr_data.EDA.rolling(window=20).mean()
    gsr_data['phasic'] = gsr_data.EDA-rolling_mean
    window_length = int(len(gsr_data['EDA'])/100)*2 + 1
    gsr_data['tonic'] = savgol_filter(gsr_data['EDA'], window_length, 2)
    
    return gsr_data

def compute_phasic_features(gsr_data):
    aux1 = np.diff(gsr_data.phasic > .1 )
    aux2 = np.diff(gsr_data.phasic < 0 )
    
    true_list = np.where(aux2)[0]
    
    peaks = {'start':[],'end':[],'peak_locs':[],'amp':[],'rise_time':[],'recovery_time':[]}
    
    for ini,end in zip(true_list,true_list[1:]):
        indx_onsets = np.where(aux1[ini:end])[0]
        if len(indx_onsets) >= 2:
            start = ini + indx_onsets[0]
            finish = end
            peaks['start'].append( start )
            peaks['end'].append( end )
            peaks['amp'].append( np.abs( gsr_data.phasic[start:finish].max() - gsr_data.phasic[start] ) )
            peak_loc = np.where(gsr_data.phasic[start:finish] == gsr_data.phasic[start:finish].max())[0][0]
            peaks['peak_locs'].append( start+peak_loc )
            peaks['rise_time'].append( peak_loc  )
            peaks['recovery_time'].append( (finish-start) - peak_loc )
    
    return pd.DataFrame.from_dict(peaks)

def compute_tonic_features(gsr_data,fs,seconds,overlap=.9):
    
    if overlap != 1:
        step = int((1-overlap)*fs*seconds)
        length = fs*seconds
        windows = int( (len(gsr_data) - length) / step ) + 1
    else:
        step=1
        windows=1
        length = len(gsr_data)
        
    tonic = {'offset':[],'slope':[],'std':[]}
    for i in range(windows):
        ini = i*step
        end = ini + length
        offset, slope = estimate_coefs(np.arange(0,length),gsr_data[ini:end])
        tonic['offset'].append(offset)
        tonic['slope'].append(slope)    
        tonic['std'].append(np.std(gsr_data))
        
    return tonic

def estimate_coefs(x, y): 
    from sklearn.linear_model import LinearRegression
    model = LinearRegression().fit(x.reshape(-1, 1), y)
    model.score(x.reshape(-1, 1), y)

    b_0 = model.intercept_
    b_1 = model.coef_[0]
  
    return b_0, b_1
    
def plot_regression_line(x, y, b): 
    plt.figure()
    # plotting the actual points as scatter plot 
    plt.plot(x, y) 
  
    # predicted response vector 
    y_pred = np.array(b[0]) + np.array(b[1])*x 
  
    # plotting the regression line 
    plt.plot(x, y_pred, color = "m") 
  
    # putting labels 
    plt.xlabel('x') 
    plt.ylabel('y') 
  
    # function to show plot 
    plt.show() 


def interpolateDataTo8Hz(data,sample_rate,startTime):
    if sample_rate<8:
        # Upsample by linear interpolation
        if sample_rate==2:
            data.index = pd.date_range(start=startTime, periods=len(data), freq='500L')
        elif sample_rate==4:
            data.index = pd.date_range(start=startTime, periods=len(data), freq='250L')
        data = data.resample("125L").mean()
    else:
        if sample_rate>8:
            # Downsample
            idx_range = list(range(0,len(data))) # TODO: double check this one
            data = data.iloc[idx_range[0::int(int(sample_rate)/8)]]
        # Set the index to be 8Hz
        data.index = pd.date_range(start=startTime, periods=len(data), freq='125L')

    # Interpolate all empty values
    data = interpolateEmptyValues(data)
    return data

def interpolateEmptyValues(data):
    cols = data.columns.values
    for c in cols:
        data.loc[:, c] = data[c].interpolate()

    return data

def butter_lowpass(cutoff, fs, order=5):
    # Filtering Helper functions
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = scisig.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    # Filtering Helper functions
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = scisig.filtfilt(b, a, data)
    return y

def butter_highpass(cutoff, fs, order=5):
    # Filtering Helper functions
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = scisig.butter(order, normal_cutoff, btype='hp', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    # Filtering Helper functions
    b, a = butter_highpass(cutoff, fs, order=order)
    y = scisig.filtfilt(b, a, data)
    return y

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = scisig.butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = scisig.filtfilt(b, a, data)
    return y