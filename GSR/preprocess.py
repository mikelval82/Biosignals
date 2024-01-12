import pandas as pd
import scipy.signal as scisig

def interpolateDataTo8Hz(data, sample_rate, startTime):
    """
    Interpolate data to 8Hz sample rate.

    Args:
    - data: Input data as a pandas DataFrame.
    - sample_rate: Original sample rate of the data.
    - startTime: Start time of the data.

    Returns:
    - Interpolated data at 8Hz sample rate as a pandas DataFrame.
    """
    if sample_rate < 8:
        # Upsample by linear interpolation
        if sample_rate == 2:
            data.index = pd.date_range(start=startTime, periods=len(data), freq='500L')
        elif sample_rate == 4:
            data.index = pd.date_range(start=startTime, periods=len(data), freq='250L')
        data = data.resample("125L").mean()
    else:
        if sample_rate > 8:
            # Downsample
            idx_range = list(range(0, len(data)))  # TODO: double check this one
            data = data.iloc[idx_range[0::int(int(sample_rate) / 8)]]
        # Set the index to be 8Hz
        data.index = pd.date_range(start=startTime, periods=len(data), freq='125L')

    # Interpolate all empty values
    data = interpolateEmptyValues(data)
    return data

def interpolateEmptyValues(data):
    """
    Interpolate empty values in a DataFrame.

    Args:
    - data: Input data as a pandas DataFrame.

    Returns:
    - Data with interpolated empty values as a pandas DataFrame.
    """
    cols = data.columns.values
    for c in cols:
        data.loc[:, c] = data[c].interpolate()

    return data

def butter_lowpass(cutoff, fs, order=5):
    """
    Create a low-pass Butterworth filter.

    Args:
    - cutoff: Cutoff frequency of the filter.
    - fs: Sampling frequency of the data.
    - order: Order of the filter.

    Returns:
    - b, a: Coefficients of the Butterworth filter.
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = scisig.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    """
    Apply a low-pass Butterworth filter to the data.

    Args:
    - data: Input data as a pandas DataFrame.
    - cutoff: Cutoff frequency of the filter.
    - fs: Sampling frequency of the data.
    - order: Order of the filter.

    Returns:
    - y: Filtered data.
    """
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = scisig.filtfilt(b, a, data)
    return y

def butter_highpass(cutoff, fs, order=5):
    """
    Create a high-pass Butterworth filter.

    Args:
    - cutoff: Cutoff frequency of the filter.
    - fs: Sampling frequency of the data.
    - order: Order of the filter.

    Returns:
    - b, a: Coefficients of the Butterworth filter.
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = scisig.butter(order, normal_cutoff, btype='hp', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    """
    Apply a high-pass Butterworth filter to the data.

    Args:
    - data: Input data as a pandas DataFrame.
    - cutoff: Cutoff frequency of the filter.
    - fs: Sampling frequency of the data.
    - order: Order of the filter.

    Returns:
    - y: Filtered data.
    """
    b, a = butter_highpass(cutoff, fs, order=order)
    y = scisig.filtfilt(b, a, data)
    return y

def butter_bandpass(lowcut, highcut, fs, order=5):
    """
    Create a band-pass Butterworth filter.

    Args:
    - lowcut: Low cutoff frequency of the filter.
    - highcut: High cutoff frequency of the filter.
    - fs: Sampling frequency of the data.
    - order: Order of the filter.

    Returns:
    - b, a: Coefficients of the Butterworth filter.
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = scisig.butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    """
    Apply a band-pass Butterworth filter to the data.

    Args:
    - data: Input data as a pandas DataFrame.
    - lowcut: Low cutoff frequency of the filter.
    - highcut: High cutoff frequency of the filter.
    - fs: Sampling frequency of the data.
    - order: Order of the filter.

    Returns:
    - y: Filtered data.
    """
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = scisig.filtfilt(b, a, data)
    return y
