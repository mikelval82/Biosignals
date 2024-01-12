# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from scipy.signal import savgol_filter
import scipy.signal as scisig
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def extract_gsr_components(gsr_data):
    """
    Extract GSR components from GSR data.

    Args:
    - gsr_data: DataFrame containing GSR data with 'datetime' and 'EDA' columns.

    Returns:
    - gsr_data: DataFrame with 'EDA', 'phasic', and 'tonic' columns added.
    """
    gsr_data = pd.DataFrame(gsr_data, columns=['datetime', 'EDA'])
    sampleRate = 4  # Hz
    startTime = gsr_data.iloc[0, 0]
    gsr_data = interpolateDataTo8Hz(gsr_data, sampleRate, startTime)
    rolling_mean = gsr_data.EDA.rolling(window=20).mean()
    gsr_data['phasic'] = gsr_data.EDA - rolling_mean
    window_length = int(len(gsr_data['EDA']) / 100) * 2 + 1
    gsr_data['tonic'] = savgol_filter(gsr_data['EDA'], window_length, 2)
    return gsr_data


def compute_phasic_features(gsr_data):
    """
    Compute phasic features from GSR data.

    Args:
    - gsr_data: DataFrame containing GSR data with 'datetime' and 'phasic' columns.

    Returns:
    - DataFrame with phasic features.
    """
    aux1 = np.diff(gsr_data.phasic > .1)
    aux2 = np.diff(gsr_data.phasic < 0)
    true_list = np.where(aux2)[0]
    peaks = {'start': [], 'end': [], 'peak_locs': [], 'amp': [], 'rise_time': [], 'recovery_time': []}

    for ini, end in zip(true_list, true_list[1:]):
        indx_onsets = np.where(aux1[ini:end])[0]
        if len(indx_onsets) >= 2:
            start = ini + indx_onsets[0]
            finish = end
            peaks['start'].append(start)
            peaks['end'].append(end)
            peaks['amp'].append(np.abs(gsr_data.phasic[start:finish].max() - gsr_data.phasic[start]))
            peak_loc = np.where(gsr_data.phasic[start:finish] == gsr_data.phasic[start:finish].max())[0][0]
            peaks['peak_locs'].append(start + peak_loc)
            peaks['rise_time'].append(peak_loc)
            peaks['recovery_time'].append((finish - start) - peak_loc)
    return pd.DataFrame.from_dict(peaks)


def compute_tonic_features(gsr_data, fs, seconds, overlap=0.9):
    """
    Compute tonic features from GSR data.

    Args:
    - gsr_data: GSR data.
    - fs: Sampling frequency.
    - seconds: Duration of the data.
    - overlap: Overlap factor.

    Returns:
    - Dictionary with tonic features.
    """
    if overlap != 1:
        step = int((1 - overlap) * fs * seconds)
        length = fs * seconds
        windows = int((len(gsr_data) - length) / step) + 1
    else:
        step = 1
        windows = 1
        length = len(gsr_data)
    tonic = {'offset': [], 'slope': [], 'std': []}

    for i in range(windows):
        ini = i * step
        end = ini + length
        offset, slope = estimate_coefs(np.arange(0, length), gsr_data[ini:end])
        tonic['offset'].append(offset)
        tonic['slope'].append(slope)
        tonic['std'].append(np.std(gsr_data))
    return tonic


def estimate_coefs(x, y):
    """
    Estimate coefficients for linear regression.

    Args:
    - x: Input data.
    - y: Output data.

    Returns:
    - Coefficients (offset and slope).
    """
    from sklearn.linear_model import LinearRegression
    model = LinearRegression().fit(x.reshape(-1, 1), y)
    model.score(x.reshape(-1, 1), y)
    b_0 = model.intercept_
    b_1 = model.coef_[0]
    return b_0, b_1


def plot_regression_line(x, y, b):
    """
    Plot a regression line.

    Args:
    - x: Input data.
    - y: Output data.
    - b: Coefficients (offset and slope).

    Returns:
    - None (displays the plot).
    """
    plt.figure()
    plt.plot(x, y)
    y_pred = np.array(b[0]) + np.array(b[1]) * x
    plt.plot(x, y_pred, color="m")
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()


def interpolateDataTo8Hz(data, sample_rate, startTime):
    """
    Interpolate data to a 8Hz sample rate.

    Args:
    - data: Input data as a DataFrame.
    - sample_rate: The original sample rate of the data.
    - startTime: Start time of the data.

    Returns:
    - Interpolated data at 8Hz.
    """
    if sample_rate < 8:
        if sample_rate == 2:
            data.index = pd.date_range(start=startTime, periods=len(data), freq='500L')
        elif sample_rate == 4:
            data.index = pd.date_range(start=startTime, periods=len(data), freq='250L')
        data = data.resample("125L").mean()
    else:
        if sample_rate > 8:
            idx_range = list(range(0, len(data)))
            data = data.iloc[idx_range[0::int(int(sample_rate)/8)]]
        data.index = pd.date_range(start=startTime, periods=len(data), freq='125L')

    # Interpolate empty values
    data = interpolateEmptyValues(data)
    return data

def interpolateEmptyValues(data):
    """
    Interpolate empty values in a DataFrame.

    Args:
    - data: Input data as a DataFrame.

    Returns:
    - Data with interpolated empty values.
    """
    cols = data.columns.values
    for c in cols:
        data.loc[:, c] = data[c].interpolate()

    return data

import numpy as np
import scipy.signal as scisig
import pandas as pd

def butter_lowpass(cutoff: float, fs: float, order: int = 5) -> tuple:
    """
    Design a low-pass Butterworth filter.

    Args:
    - cutoff (float): The cutoff frequency in Hertz.
    - fs (float): The sampling frequency in Hertz.
    - order (int, optional): The filter order. Defaults to 5.

    Returns:
    - tuple: A tuple containing (b, a), where b and a are arrays representing
      the filter coefficients.
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = scisig.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data: pd.DataFrame, cutoff: float, fs: float, order: int = 5) -> pd.DataFrame:
    """
    Apply a low-pass Butterworth filter to data.

    Args:
    - data (pd.DataFrame): Input data.
    - cutoff (float): The cutoff frequency in Hertz.
    - fs (float): The sampling frequency in Hertz.
    - order (int, optional): The filter order. Defaults to 5.

    Returns:
    - pd.DataFrame: Filtered data.
    """
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = scisig.filtfilt(b, a, data)
    return pd.DataFrame(y, columns=data.columns)



def butter_highpass(cutoff: float, fs: float, order: int = 5) -> tuple:
    """
    Design a high-pass Butterworth filter.

    Args:
        cutoff (float): The cutoff frequency for the high-pass filter.
        fs (float): The sampling frequency.
        order (int, optional): The filter order (default is 5).

    Returns:
        tuple: Numerator (b) and denominator (a) coefficients of the filter.
    """
    # Calculate Nyquist frequency
    nyq = 0.5 * fs
    # Normalize cutoff frequency
    normal_cutoff = cutoff / nyq
    # Design the high-pass Butterworth filter
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data: np.ndarray, cutoff: float, fs: float, order: int = 5) -> np.ndarray:
    """
    Apply a high-pass Butterworth filter to the input data.

    Args:
        data (np.ndarray): The input data to be filtered.
        cutoff (float): The cutoff frequency for the high-pass filter.
        fs (float): The sampling frequency.
        order (int, optional): The filter order (default is 5).

    Returns:
        np.ndarray: The filtered data.
    """
    # Get filter coefficients
    b, a = butter_highpass(cutoff, fs, order=order)
    # Apply the filter to the data
    y = filtfilt(b, a, data)
    return y

def butter_bandpass(lowcut: float, highcut: float, fs: float, order: int = 5) -> tuple:
    """
    Design a band-pass Butterworth filter.

    Args:
        lowcut (float): The lower cutoff frequency for the band-pass filter.
        highcut (float): The upper cutoff frequency for the band-pass filter.
        fs (float): The sampling frequency.
        order (int, optional): The filter order (default is 5).

    Returns:
        tuple: Numerator (b) and denominator (a) coefficients of the filter.
    """
    # Calculate Nyquist frequency
    nyq = 0.5 * fs
    # Normalize cutoff frequencies
    low = lowcut / nyq
    high = highcut / nyq
    # Design the band-pass Butterworth filter
    b, a = butter(order, [low, high], btype='band', analog=False)
    return b, a

def butter_bandpass_filter(data: np.ndarray, lowcut: float, highcut: float, fs: float, order: int = 5) -> np.ndarray:
    """
    Apply a band-pass Butterworth filter to the input data.

    Args:
        data (np.ndarray): The input data to be filtered.
        lowcut (float): The lower cutoff frequency for the band-pass filter.
        highcut (float): The upper cutoff frequency for the band-pass filter.
        fs (float): The sampling frequency.
        order (int, optional): The filter order (default is 5).

    Returns:
        np.ndarray: The filtered data.
    """
    # Get filter coefficients
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    # Apply the filter to the data
    y = filtfilt(b, a, data)
    return y

