# -*- coding: utf-8 -*-
"""
constants class for managing configuration constants.

@author: Mikel Val Calvo
@email: mikel1982mail@gmail.com
@institution: Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED)
@DOI: 10.5281/zenodo.3759306
"""


class constants():
    """
    A class for managing configuration constants.
    """

    def __init__(self, seconds=6, sample_rate=250, baud=115200, channels=8, ndims=8, signal='eeg', lowcut=1, highcut=45,
                 order=5):
        """
        Initialize an instance of the constants class with default values.

        :param seconds: The number of seconds for data collection.
        :param sample_rate: The sample rate for data collection.
        :param baud: The baud rate for communication.
        :param channels: The number of data channels.
        :param ndims: The number of dimensions.
        :param signal: The type of signal (e.g., 'eeg').
        :param lowcut: The lowcut frequency.
        :param highcut: The highcut frequency.
        :param order: The order for signal processing.
        """
        ############### CONSTANTS ######################
        self.E4_server_ADDRESS = 'localhost'
        self.EMPATICA_PORT = 8000

        self.ADDRESS = 'localhost'
        self.PORT = 10000
        self.BVP_SECONDS = 12
        self.GSR_SECONDS = 60
        self.TMP_SECONDS = 60
        self.ACC_SECONDS = 12

    def update(self, name, value):
        """
        Update a specific constant value.

        :param name: The name of the constant to update.
        :param value: The new value for the constant.
        :return: None
        """
        if name == 'bvp_seconds':
            self.BVP_SECONDS = value
        elif name == 'gsr_seconds':
            self.GSR_SECONDS = value
        elif name == 'tmp_seconds':
            self.TMP_SECONDS = value
        elif name == 'acc_seconds':
            self.ACC_SECONDS = value
        elif name == 'port':
            self.PORT = value
        elif name == 'IP':
            self.ADDRESS = value
        elif name == 'E4_server_ADDRESS':
            self.E4_server_ADDRESS = value
