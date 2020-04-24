# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter,find_peaks,convolve
from scipy.stats import zscore
import pyhrv.tools as tools
import pyhrv.time_domain as td
import pyhrv.frequency_domain as fd
import pyhrv.nonlinear as nl

def poincare_plot(nni,title=''):    
    nl.poincare(nni,title=title)
    
def frequency_plot(nni,method='welch_psd',title=''):  
    if method == 'lomb_psd':
        fd.lomb_psd(nni,title=title)
    elif method == 'ar_psd':
        fd.ar_psd(nni,title=title)
    else:
        fd.welch_psd(nni,title=title,plot=True)
        
        
def compute_features(nni):
    features = {}
    features['mean_hr'] = tools.heart_rate(nni).mean()
    features['sdnn'] = td.sdnn(nni)[0]
    features['rmssd'] = td.rmssd(nni)[0]
    features['sdsd'] = td.sdsd(nni)[0]
    features['nn20'] = td.nn20(nni)[0]
    features['pnn20'] = td.nn20(nni)[1]
    features['nn50'] = td.nn50(nni)[0]
    features['pnn50'] = td.nn50(nni)[1]
    features['hf_lf_ratio'] = fd.welch_psd(nni,show=False)['fft_ratio']
    features['very_lf'] = fd.welch_psd(nni,show=False)['fft_peak'][0]
    features['lf'] = fd.welch_psd(nni,show=False)['fft_peak'][1]
    features['hf'] = fd.welch_psd(nni,show=False)['fft_peak'][2]
    features['log_very_lf'] = fd.welch_psd(nni,show=False)['fft_log'][0]
    features['log_lf'] = fd.welch_psd(nni,show=False)['fft_log'][1]
    features['log_hf'] = fd.welch_psd(nni,show=False)['fft_log'][2]
    features['sampen'] = nl.sample_entropy(nni)[0]
    
    return features
    
def compute_nni(hrdata,sample_rate=64, sliding_window=.5, prominence=0.1, dist_q1=50, dist_q2=120,  std_window = 6, std_th = 130, method ='remove', plot=False):

    hrdata_inv = hrdata*(-1)
    """Calcuamos a media movil"""
    roll_mean = savgol_filter(hrdata_inv, 81, 2) 
    
#    plt.figure()
#    plt.plot(hrdata_inv)
#    plt.plot(roll_mean)
    
    """Create sliding window to calculate maximum signal over time"""
    windowsize = int(sliding_window*sample_rate)
    add = np.zeros (int(windowsize/2))
    add[:] = np.nan
    hrdata_ext = np.concatenate((add,hrdata_inv,add))
    
    """Calculamos la envolvente superior """
    roll_max =[]
    for i in range (len(hrdata)):
        roll_max.append (np.nanmax(hrdata_ext[i:i+windowsize]))
    
    """Suavizamos la envolvente superior """
    sroll_max = savgol_filter(roll_max, 51, 2) 
    mn = .3*np.std(sroll_max)
    sroll_max = sroll_max + mn
    
#    plt.plot(sroll_max)
    
    
    """Calculamos una representación simplificada del heart rate"""
    simpleHR_1 = (hrdata_inv-roll_mean) * (hrdata_inv > roll_mean)
    envoltorio = minmax(sroll_max-roll_mean)
    simpleHR_2_raw = sigmoid(0,2,5,envoltorio) * simpleHR_1
    simpleHR_2 = savgol_filter(simpleHR_2_raw, 31, 2) * (hrdata_inv > roll_mean)

#    plt.plot(simpleHR_2)
    
    """ Find the centers of the peaks of the signal """
    peaksx = np.where((simpleHR_2 > 0))[0]
    peaksy = simpleHR_2[peaksx]
    peaks, a = find_peaks(peaksy,prominence=prominence)
    
#    plt.plot(peaksx[peaks],simpleHR_2[peaksx[peaks]],'*m')
    

    """ Create an array with the distances between peaks and filter
    the outlayers of missing beats (high or very low distances) """
    nni = tools.nn_intervals((peaksx[peaks]/sample_rate)*1000)  
    hr = tools.heart_rate(nni)
    nni_revised = np.zeros_like(nni)
    nni_revised[:] = np.nan
    index = np.logical_and((hr >= dist_q1), (hr <= dist_q2))
    nni_revised[index] = nni[index]
    nni_revised = nni_revised[~np.isnan(nni_revised)]
    std = std_convoluted(nni_revised,std_window)
    
#    plt.figure()
#    plt.plot(nni_revised)
#    plt.plot(nni)
#    plt.plot(std)
    
    index_std = [i for i in range(len(zscore(std))) if std[i] > std_th]
    groups = np.append(np.diff(index_std),100)
    if groups[0] > 1:
        groups = groups[1:]
        
    index_diff = np.where(groups > 1)[0]
    
    if len(index_diff) > 1:
        start = 0
        end = index_diff[0]
        for i in range(1,len(index_diff)-1):
            index_hole = index_std[start:end]
#            
#            plt.figure()
#            plt.plot(nni_revised[index_hole])
            if method == 'remove':
                aux = np.zeros(nni_revised[index_hole].shape)
                aux[:] = np.nan
                nni_revised[index_hole] = aux#outliers_iqr_method(nni_revised[index_hole])
            elif method == 'iqr':
                nni_revised[index_hole] = outliers_iqr_method(nni_revised[index_hole])
            elif method == 'modified_z':
                nni_revised[index_hole] = outliers_modified_z(nni_revised[index_hole])
                
#            plt.plot(nni_revised[index_hole])
            
            start = index_diff[i-1]
            end = index_diff[i]
        
    nni_revised = nni_revised[~np.isnan(nni_revised)]


    """Representamos las graficas necesarias para visualizar los datos"""
    if plot:
        fig,axes = plt.subplots(2,2)
        axes[0,0].plot(hrdata_inv)
        axes[0,0].plot(roll_mean)
        axes[0,0].plot(roll_max)

        axes[0,1].plot(simpleHR_1)
        axes[0,1].plot(simpleHR_2)
        axes[0,1].plot(peaksx[peaks], peaksy[peaks],'kx')

        if len(nni_revised)%2 == 0:
            size = len(nni_revised)-1
        else:
            size = len(nni_revised)
            
        axes[1,0].plot(nni)
        axes[1,0].plot(nni_revised)
        axes[1,0].plot( savgol_filter(nni_revised, min([101,size]), 2) )
        plt.legend(['original','revised','fit'])
#        
        axes[1,1].plot( tools.heart_rate(nni_revised)) 
        axes[1,1].plot( savgol_filter(tools.heart_rate(nni_revised), min([101,size]), 2) )
        axes[1,1].set_ylim([40,120])
        plt.legend(['Heart Rate'])
        
#        axes[1,1].plot((nni-np.nanmean(nni))/np.nanstd(nni)) 
#        axes[1,1].plot((nni_revised-np.nanmean(nni))/np.nanstd(nni))
#        axes[1,1].plot((std-np.nanmean(std))/np.nanstd(std) )
        
        

    return nni_revised


def minmax(data):
    return (data-data.min())/(data.max()-data.min())

def sigmoid(minv,maxv, a, x):
    return minv + maxv/(1 + np.exp(a*x))

def std_convoluted(nni_revised, N):
    im = np.array(nni_revised, dtype=np.uint32)
    im2 = im**2
    ones = np.ones(im.shape)

    kernel = np.ones((2*N+1,))
    s = convolve(im, kernel, mode="same")
    s2 = convolve(im2, kernel, mode="same")
    ns = convolve(ones, kernel, mode="same")

    return np.sqrt((s2 - s**2 / ns) / ns)

def outliers_iqr_method(hrvalues):
    '''function that removes outliers based on the interquartile range method
    see: https://en.wikipedia.org/wiki/Interquartile_range

    keyword arguments:
    hrvalues -- list of computed hr or hrv values, from which outliers need to be identified

    returns cleaned list, with outliers substituted for the median
    '''
    med = np.median(hrvalues)
    q1, q3 = np.percentile(hrvalues, [60, 95])
    iqr = q3 - q1
    lower = q1 - (1.5 * iqr)
    upper = q3 + (1.5 * iqr)
    output = []
    for i in range(0,len(hrvalues)):
        if hrvalues[i] < lower or hrvalues[i] > upper:
            output.append(med)
        else:
            output.append(hrvalues[i])
    return output

def MAD(data):
    '''function to compute median absolute deviation of data slice
       https://en.wikipedia.org/wiki/Median_absolute_deviation
    
    keyword arguments:
    - data: 1-dimensional numpy array containing data
    '''
    med = np.nanmedian(data)
    return np.nanmedian(np.abs(data - med))

def outliers_modified_z(hrvalues):
    '''function that removes outliers based on the modified Z-score metric

    keyword arguments:
    - hrvalues: list of computed hr or hrv values, from which outliers 
                need to be identified

    returns cleaned list, with outliers substituted for the median
    '''
    hrvalues = np.array(hrvalues)
    threshold = 3.5
    med = np.nanmedian(hrvalues)
    mean_abs_dev = MAD(hrvalues)
    modified_z_result = 0.6745 * (hrvalues - med) / mean_abs_dev
    output = []
    for i in range(0, len(hrvalues)):
        if np.abs(modified_z_result[i]) <= threshold:
            output.append(hrvalues[i])
        else:
            output.append(med)
    return output
    
        
        
        
