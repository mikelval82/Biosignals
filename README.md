# BIOSIGNALS: General BVP, GSR, TMP and ACC experimentation in real-time, an open source software for physiological real-time experimental designs

1. Real-time acquisition and visualisation of physiological signals: blood volume pressure(BVP), galvanic skin response(GSR), temperature(TMP) and accelerometers(ACC).
2. Trigger synchronisation by a tcp/ip interface which allows start/stop recordings
remotely.
3. Data recording on EDF file format for electrophysiological signals.
4. Online behaviour labelling interface which labels are synchronised and stored on
EDF files.

# INSTRUCTIONS:
Install dependencies:
```
PyQt5
pyhrv
PythonQwt
scipy
pandas
matplotlib
numpy
pyEDFlib
```

# USE EXAMPLE:
1) Run in one terminal:
```
python BCI_STANDARD_EXPERIMENT_03.py
```
2) Set the user filename

3) Set IP and PORT in the app and click the trigger button

4) Run in another terminal:
```
python
```
5) Create a client
```
from COM.trigger_client import trigger_client

tc = trigger_client('IP','PORT')
tc.create_socket()
tc.connect()
```
Then you are ready to start the recording.

```
tc.send_msg(b'start')
```
Labels can be sent asynchronously during the recording and will be stored as events in the EDF user file.

```
tc.send_msg(b'happy')
```

To stop the recording and save the temporal series in the user EDF file.

```
tc.send_msg(b'stop')
```


# CITATION:
@DOI: 10.5281/zenodo.3759262 

# AUTHOR DETAILS AND CONTACT
Author: Mikel Val Calvo
Institution: Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED)
Email: mikel1982mail@gmail.com
