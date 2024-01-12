from GENERAL.ring_buffer_02 import RingBuffer as buffer
from threading import Lock
import numpy as np


class data_manager():

    def __init__(self, signal=None, signal_numbers=None, seconds=None, sample_rate=None):
        """
        Initialize the data manager.

        Args:
        - signal (str): The type of signal being managed (e.g., 'bvp', 'gsr', 'tmp', 'acc').
        - signal_numbers (int): The number of signal channels.
        - seconds (float): The duration of the data window in seconds.
        - sample_rate (int): The sampling rate in Hz.

        """
        ############### CONSTANTS ######################
        self.PATH = './datos/'
        self.filename = 'undefined'
        self.SIGNAL = signal
        self.SIGNAL_NUMBERS = signal_numbers
        self.SECONDS = seconds
        self.SAMPLE_RATE = sample_rate
        self.WINDOW = self.SAMPLE_RATE * self.SECONDS
        self.freqTask = self.SAMPLE_RATE
        ############### data save trigger
        self.allData = []
        self.triggers = []
        self.current_trial = 0
        self.cur_index = 0
        ############### buffer ########################
        self.buffer = buffer(channels=self.SIGNAL_NUMBERS + 1, num_samples=self.WINDOW, sample_rate=self.SAMPLE_RATE)
        # self.trigger_control = None
        ###### mutex lock
        self.mutexBuffer = Lock()

    def create_file(self):
        self.filename = self.PATH + '_' + self.SIGNAL + '_trial_' + str(self.current_trial) + '.npy'

    def reset_data_store(self):
        """
        Reset the data store, clearing recorded data and triggers.

        """
        self.allData = []
        self.triggers = []

    def online_annotation(self, notation):
        """
        Record an online annotation.

        Args:
        - notation (str): The annotation to be recorded.

        """
        instant = self.cur_index / self.SAMPLE_RATE
        self.triggers.append((notation, instant))

    def save_streamData(self):
        """
        Save the recorded data to a file.

        """
        if self.SIGNAL == 'bvp':
            columns = ['time', 'bvp']
            dimension = 'mili_volts'
        elif self.SIGNAL == 'gsr':
            columns = ['time', 'gsr']
            dimension = 'micro_siemens'
        elif self.SIGNAL == 'tmp':
            columns = ['time', 'tmp']
            dimension = 'grades'
        elif self.SIGNAL == 'acc':
            columns = ['time', 'x', 'y', 'z']
            dimension = 'meters'

        self.allData = np.array(self.allData)
        print(self.allData.shape, self.SIGNAL)
        self.allData[:, 0] = self.allData[:, 0] - self.allData[0, 0]
        data_dict = {'sample_rate': self.SAMPLE_RATE, 'dimension': dimension, 'columns': columns, 'data': self.allData,
                     'triggers': self.triggers}
        np.save(self.filename, data_dict, allow_pickle=True)

    def setWindow(self, seconds):
        """
        Set the duration of the data window in seconds.

        Args:
        - seconds (float): The new duration of the data window in seconds.

        """
        self.mutexBuffer.acquire()
        self.SECONDS = seconds
        self.WINDOW = self.SAMPLE_RATE * self.SECONDS
        self.mutexBuffer.release()

    def getWindow(self):
        """
        Get the current duration of the data window in samples.

        Returns:
        - int: The duration of the data window in samples.

        """
        return self.WINDOW

    def clearBuffer(self):
        """
        Clear the buffer.

        """
        self.mutexBuffer.acquire()
        self.buffer.reset()
        self.mutexBuffer.release()

    def appendSample(self, sample):
        """
        Append a sample to the buffer.

        Args:
        - sample (list): The sample data to be appended.

        """
        self.mutexBuffer.acquire()
        self.buffer.append(sample)
        self.cur_index += 1
        self.mutexBuffer.release()

    def getSamples(self):
        """
        Get samples from the buffer.

        Returns:
        - numpy.ndarray: An array containing the sample data.

        """
        self.mutexBuffer.acquire()
        plot_data = self.buffer.get()
        self.mutexBuffer.release()
        return plot_data
