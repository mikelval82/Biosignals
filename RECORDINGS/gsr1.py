# Load NeuroKit and other useful packages
import neurokit2 as nk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm
import matplotlib.colors
from scipy.interpolate import interp1d

def interpolate(eda_signal, show=True):
    x = np.linspace(0, len(eda_signal), num=len(eda_signal), endpoint=True)
    f2 = interp1d(x, eda_signal, kind='cubic')
    xnew = np.linspace(0, len(eda_signal), num=len(eda_signal)*2, endpoint=True)
    eda_signal_interp = f2(xnew)
    if show:
        plt.figure()
        plt.scatter(x, eda_signal)
        plt.scatter(xnew, eda_signal_interp)
    
    return eda_signal_interp
#%%

#crear variable eda_signal
eda_signal='TEST_tmp_trial_3.npy'

#open the file
#text_file = open('\Biosignals\RECORDINGS\TEST_tmp_trial_3.npy')
data = np.load('TEST_tmp_trial_3.npy', allow_pickle=True).item()


eda_signal = data['data'][:,1]
eda_signal = interpolate(eda_signal, show=False)


print(eda_signal.shape)
# eda_signal = nk.eda_simulate(duration=10, sampling_rate=250, scr_number=3, drift=0.01)

# Process the raw EDA signal
signals, info = nk.eda_process(eda_signal, sampling_rate=8)
# Extract clean EDA and SCR features
cleaned = signals["EDA_Clean"]
features = [info["SCR_Onsets"], info["SCR_Peaks"], info["SCR_Recovery"]]
# Visualize SCR features in cleaned EDA signal
plot = nk.events_plot(features, cleaned, color=['red', 'blue', 'orange'])
#estandarizamos la señal EDA bruta antes de la descomposición
# Filter phasic and tonic components
data = nk.eda_phasic(nk.standardize(eda_signal), sampling_rate=250)

data["EDA_Raw"] = eda_signal  # Add raw signal
data.plot()
# Plot EDA signal
nk.eda_plot(signals)


