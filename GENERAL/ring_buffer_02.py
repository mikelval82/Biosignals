from PyQt5 import QtCore
import numpy as np
import copy

class RingBuffer(QtCore.QThread):
    """A class that implements a not-yet-full buffer."""

    emitter = QtCore.pyqtSignal()

    def __init__(self, channels=None, num_samples=None, sample_rate=None, parent=None):
        """
        Initialize a RingBuffer object.

        Args:
        - channels (int): The number of data channels.
        - num_samples (int): The maximum number of samples in the buffer.
        - sample_rate (int): The sampling rate of the data.
        - parent (QObject): The parent QObject for this buffer.

        Attributes:
        - channels (int): The number of data channels.
        - max (int): The maximum number of samples in the buffer.
        - data (numpy.ndarray): A 2D array to store the data samples.
        - cur (int): A pointer to the current position in the buffer.
        - cur_show (int): A pointer to the current position for display purposes.
        - sample_rate (int): The sampling rate of the data.
        - seconds (int): The number of seconds for display control.
        - control (int): Control variable for displaying data.

        The RingBuffer is used to store and manage data samples.
        """
        super(RingBuffer, self).__init__(parent)
        self.channels = channels
        self.max = num_samples
        self.data = np.zeros((self.max, self.channels))
        self.cur = copy.copy(self.max)
        self.cur_show = copy.copy(self.max)
        self.sample_rate = sample_rate
        self.seconds = 6
        self.control = self.sample_rate * self.seconds

    def reset(self):
        """Reset the RingBuffer to its initial state."""
        self.data = np.zeros((self.max, self.channels))
        self.cur = copy.copy(self.max)
        self.cur_show = copy.copy(self.max)

    def append(self, x):
        """Append an element at the end of the buffer."""
        self.cur = self.cur % self.max
        self.data[self.cur, :] = np.array(x)
        self.cur = self.cur + 1
        if self.cur_show > 0:
            self.cur_show -= 1
        if (self.cur_show == 0) and ((self.cur % self.control) == 0):
            self.emitter.emit()

    def get(self):
        """
        Return a list of elements from the oldest to the newest.

        Returns:
        - numpy.ndarray: A 2D array containing the data samples.
        """
        data = np.vstack((self.data[self.cur:, :], self.data[:self.cur, :]))
        data = data[self.cur_show:, :]
        return data
