# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from COM import TCP_IP_COM as sock
from GUI.biosignals_GUI_01 import GUI
from COM.trigger_server_3 import trigger_server
from GENERAL.slots_manager import SlotsManager
from GENERAL.constants_00 import constants
from PyQt5 import QtWidgets, QtCore
import sys


class MyApp(QtWidgets.QApplication):
    def __init__(self):
        """
        Initialize the application.
        """
        # Call the constructor of the parent class
        QtWidgets.QApplication.__init__(self, [''])
        self.aboutToQuit.connect(self.close_windows)

        # Create an instance of the constants class to manage configuration constants
        self.constants = constants()

        # Initialize logic control variables
        self.trigger_control = False
        self.pause_control = True

        # Initialize states and substates
        self.state = "SERVER"
        self.substate = ""
        self.trigger_server_activated = False

        # Initialize the GUI
        self.gui = GUI(self,
                       callbacks=[self.server, self.refresh, self.connect, self.start, self.launch_trigger_server])

        # Initialize the slots manager
        self.slots = SlotsManager()

        # Initialize data managers
        self.dmgs = self.gui.getDmgs()
        for dmg in self.dmgs:
            dmg.trigger_control = self.trigger_control
        self.dmgs[0].buffer.emitter.connect(self.slots.trigger)

    def launch_trigger_server(self):
        """
        Launch the trigger server if not already activated, or close it if it's already running.

        :return: None
        """
        if self.trigger_server_activated:
            # Close the trigger server and clean up resources
            self.trigger_server.close_socket()
            del self.trigger_server
            self.trigger_server_activated = False
        else:
            # Create and start the trigger server
            self.trigger_server = trigger_server(self.constants)
            self.trigger_server.socket_emitter.connect(self.trigger_event)
            self.trigger_server.log_emitter.connect(self.gui.log.myprint)
            self.trigger_server_activated = self.trigger_server.create_socket()
            if self.trigger_server_activated:
                self.trigger_server.start()
            else:
                del self.trigger_server

    @QtCore.pyqtSlot(str)
    def trigger_event(self, action):
        """
        Handle trigger events and perform actions based on the current state.

        :param action: The trigger action received.
        :return: None
        """
        if self.state == "VIEW":
            if not self.trigger_control:
                if self.substate == "OFF":
                    # Create a file for each data manager
                    for dmg in self.dmgs:
                        dmg.create_file()
                    self.start()
                else:
                    # Clean the screen
                    for dmg in self.dmgs:
                        dmg.clearBuffer()
                self.thread.flag.set()
                # Perform online annotations for each data manager
                for dmg in self.dmgs:
                    dmg.online_annotation(action)
                self.trigger_control = True  # Start recording
            else:
                if action != 'start' and action != 'stop':
                    # Online annotations
                    for dmg in self.dmgs:
                        dmg.online_annotation(action)
                else:
                    self.start()
                    self.thread.flag.clear()
                    self.trigger_control = False  # Stop recording
                    for dmg in self.dmgs:
                        dmg.online_annotation(action)
                        dmg.save_streamData()
                        dmg.reset_data_store()
                        dmg.current_trial += 1
                        dmg.running_window = 0
        else:
            self.gui.log.myprint_error('Trigger event: device not connected.')

    def start(self):
        """
        Start data recording or pause/unpause based on the current state and substate.

        :return: None
        """
        if self.state == "VIEW":
            if self.substate == "OFF":
                self.thread.pause("OFF")
                self.substate = "WAIT_PAUSE"
            elif self.substate == "ON":
                self.thread.pause("ON")
                self.substate = "WAIT_PAUSE"
            elif self.substate == "WAIT_PAUSE":
                self.gui.log.myprint_error("Waiting for the server's response. There is a delay in the server.")

    #STATE CHANGES    
    def server(self):
        """
        Handle the server button action. Connect or disconnect from the Empatica Server based on the current state.

        :return: None
        """
        if self.state == "SERVER":
            try:
                # Create and start the mysocket thread
                self.thread = sock.mysocket(self.gui.log, self.dmgs,
                                            callbacks=[self.device_list_slot, self.device_connect_slot,
                                                       self.data_pause_slot, self.data_subscribe_slot])
                print(self.constants.E4_server_ADDRESS, self.constants.EMPATICA_PORT)
                self.thread.openPort(self.constants.E4_server_ADDRESS, self.constants.EMPATICA_PORT)
                self.thread.start()
                self.state = "DEVICE"
                self.substate = "WAIT_BUTTON"
                self.thread.listDevice()
                self.gui.contextDevice()
            except:
                self.gui.log.myprint_error('Can not connect to Empatica Server')
        else:
            # Close the mysocket thread and disconnect from the server
            self.thread.closePort()
            self.state = "SERVER"
            self.substate = ""
            self.gui.bio_graph.device_comboBox.clear()
            self.gui.clear_plots()
            self.gui.contextServer()

    def connect(self):
        """
        Handle the connect button action. Establish a connection with the selected device or disconnect if already connected.

        :return: None
        """
        if self.state == "DEVICE":
            if self.substate == "WAIT_BUTTON":
                self.thread.connectDevice(
                    self.gui.bio_graph.device_comboBox.itemText(self.gui.bio_graph.device_comboBox.currentIndex()))
                self.substate = "WAIT_CONNECT"
            else:
                self.gui.log.myprint_error('The connection is already in process')
        elif self.state == "VIEW":
            # Disconnect from the device
            self.thread.disconnectDevice()

    @QtCore.pyqtSlot(bool)
    def device_connect_slot(self, device_connect):
        """
        Handle the device connect slot based on the device connection status.

        :param device_connect: True if device is connected, False otherwise.
        :return: None
        """
        if self.state == "DEVICE":
            if self.substate == "WAIT_CONNECT":
                if device_connect:
                    self.thread.pause("ON")
                    self.substate = "WAIT_PAUSE"
                else:
                    self.gui.log.myprint_error('The connection could not be established')
                    self.substate = "WAIT_BUTTON"
        if self.state == "VIEW":
            if not device_connect:
                self.state = "DEVICE"
                self.substate = "WAIT_BUTTON"
                self.thread.listDevice()
                self.gui.clear_plots()
                self.gui.contextDevice()
            else:
                self.gui.log.myprint_error('Unable to disconnect the device')

    @QtCore.pyqtSlot(bool)
    def data_pause_slot(self, data_pause):
        """
        Handle the data pause slot based on the data pause status.

        :param data_pause: True if data is paused, False otherwise.
        :return: None
        """
        self.pause_control = data_pause
        if self.state == "DEVICE":
            if self.substate == "WAIT_PAUSE":
                if data_pause:
                    self.thread.subscribe("ON")
                    self.substate = "WAIT_SUBSCRIBE"
                else:
                    self.gui.log.myprint_error('The data was not paused')
                    self.substate = "WAIT_BUTTON"
        elif self.state == "VIEW":
            if self.substate == "WAIT_PAUSE":
                if data_pause:
                    self.gui.stopTimers()
                    self.gui.bio_graph.btn_start.setText("Start")
                    self.gui.bio_graph.btn_server.setEnabled(True)
                    self.gui.bio_graph.btn_connect.setEnabled(True)
                    self.substate = "OFF"
                else:
                    self.gui.startTimers()
                    self.gui.bio_graph.btn_start.setText("Stop")
                    self.gui.bio_graph.btn_server.setEnabled(False)
                    self.gui.bio_graph.btn_connect.setEnabled(False)
                    self.substate = "ON"

    @QtCore.pyqtSlot(int)
    def data_subscribe_slot(self, data_subscribe):
        """
        Handle the data subscribe slot based on the data subscription status.

        :param data_subscribe: Data subscription status: 1 if subscribed to all signals, 0 if not, -1 if there was an error.
        :return: None
        """
        if self.state == "DEVICE":
            if self.substate == "WAIT_SUBSCRIBE":
                if data_subscribe == 1:
                    self.state = "VIEW"
                    self.substate = "OFF"
                    self.gui.contextView()
                else:
                    self.gui.log.myprint_error('Could not subscribe to all signals')
                    self.substate = "WAIT_BUTTON"

    # DISCOVER DEVICES
    def refresh(self):
        """
        Handle the refresh button action to discover devices.

        :return: None
        """
        if (self.state == "DEVICE") & (self.substate == "WAIT_BUTTON"):
            self.thread.listDevice()

    @QtCore.pyqtSlot(list)
    def device_list_slot(self, device_list):
        """
        Handle the device list slot to update the list of available devices.

        :param device_list: List of available devices.
        :return: None
        """
        if (self.state == "DEVICE") & (self.substate == "WAIT_BUTTON"):
            self.gui.bio_graph.device_comboBox.clear()
            self.gui.bio_graph.device_comboBox.addItems(device_list)

    # OPENING AND CLOSING
    def close_windows(self):
        """
        Close the application and stop timers when closing the windows.

        :return: None
        """
        self.gui.stopTimers()
        if not self.state == "SERVER":
            self.thread.closePort()

    def execute_gui(self):
        """
        Execute the GUI application.

        :return: None
        """
        ret = self.exec_()
        sys.exit(ret)

main = MyApp()
main.execute_gui()

