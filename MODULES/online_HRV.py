from threading import Thread
from COM.tcpip_dict_client import tcpip_client as client
from HRV import pybvp
from GSR import pygsr
from typing import Dict


class Pipeline(Thread):
    """
    A class for sending data to a server using TCP/IP in a separate thread.

    Attributes:
    - app: The main application instance.
    - dmgs: List of data managers.
    - client: TCP/IP client for sending data to the server.
    """

    def __init__(self, app):
        """
        Initialize the Pipeline object.

        Args:
        - app: The main application instance.
        """
        Thread.__init__(self)
        self.app = app
        self.dmgs = self.app.gui.getDmgs()
        # Initialize the TCP/IP client with the server's address and port.
        self.client = client(self.app.toADDRESS, self.app.PORT)

    def run(self):
        """
        The main run method for the thread.
        This method adds the send_data method to the list of slots managed by the app.slots.
        """
        print('Module loaded')
        # Add the send_data method to the slots manager.
        self.app.slots.append(self.send_data)

    def send_data(self):
        """
        Send BVP and GSR data features to the server.
        """
        print('Sending data')
        # Get BVP and GSR data from the data managers.
        bvp = self.dmgs[0].getSamples()
        gsr = self.dmgs[1].getSamples()

        # Compute BVP features
        nni = pybvp.compute_nni(bvp[:, 1])
        bvp_features = pybvp.compute_features(nni)

        # Compute GSR features
        gsr_data = pygsr.extract_gsr_components(gsr)
        fs = 8
        seconds = len(gsr_data) / fs
        gsr_tonic_features = pygsr.compute_tonic_features(gsr_data['tonic'], fs, seconds, overlap=1)

        # Create a dictionary containing the computed BVP and GSR features.
        msg: Dict[str, Dict[str, float]] = {'bvp': bvp_features, 'gsr': gsr_tonic_features}

        # Send the dictionary data to the server using the TCP/IP client.
        self.client.send_msg(msg)
        print('Data sent')
