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
        #super(MyApp, self).__init__(['']) 
        QtWidgets.QApplication.__init__(self,[''])
        self.aboutToQuit.connect(self.closeWindows)
        ########## GENERAL CONSTANT VALUES ##################
        self.constants = constants()
         ####### logic control #######
        self.trigger_control = False
        self.pause_control = True
        ####### States and Substates #########
        self.state = "SERVER"
        self.substate = ""
        self.trigger_server_activated = False
        ################# init GUI ################################
        self.gui = GUI(self,callbacks = [self.server, self.refresh, self.connect, self.start, self.launch_trigger_server])   
        ########## slots manager #########
        self.slots = SlotsManager()
        ######### data managers #################
        self.dmgs = self.gui.getDmgs()
        for dmg in self.dmgs:
            dmg.trigger_control = self.trigger_control
        self.dmgs[0].buffer.emitter.connect(self.slots.trigger)
        
    def launch_trigger_server(self):
        if self.trigger_server_activated:
            self.trigger_server.close_socket()
            del self.trigger_server
            self.trigger_server_activated = False
        else:
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
        if self.state == "VIEW": 
            if not self.trigger_control:
                if self.substate == "OFF":
                    for dmg in self.dmgs:# create file
                        dmg.create_file()
                    self.start()
                else:  
                    for dmg in self.dmgs:# CLEAN THE SCREEN
                        dmg.clearBuffer()
                self.thread.flag.set()
                for dmg in self.dmgs:
                    dmg.online_annotation(action)
                    
                self.trigger_control = True# START RECORDING
            else:
                if action != 'start' and action != 'stop':# ONLINE ANNOTATIONS
                    for dmg in self.dmgs:
                        dmg.online_annotation(action)
                else:
                    self.start()
                    self.thread.flag.clear()
                    self.trigger_control = False# STOP RECORDING
                    for dmg in self.dmgs:
                        dmg.online_annotation(action)
                        dmg.save_streamData()
                        dmg.reset_data_store()
                        dmg.current_trial += 1
                        dmg.running_window = 0
        else:
            self.gui.log.myprint_error('Trigger event: device not connected.')
            
    def start(self):
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
        if self.state == "SERVER":
            try:
                ##THREAD CREATE
                self.thread = sock.mysocket(self.gui.log, self.dmgs, callbacks = [self.device_list_slot, self.device_connect_slot, self.data_pause_slot, self.data_subscribe_slot])       
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
            self.thread.closePort()
            self.state = "SERVER"
            self.substate = ""
            self.gui.bio_graph.device_comboBox.clear()
            self.gui.clear_plots()
            self.gui.contextServer()
        
    def connect(self):
        if self.state == "DEVICE": 
            if self.substate == "WAIT_BUTTON":
                self.thread.connectDevice(self.gui.bio_graph.device_comboBox.itemText(self.gui.bio_graph.device_comboBox.currentIndex()))
                self.substate = "WAIT_CONNECT"
            else:
                self.gui.log.myprint_error('The connection is already in process')
        elif self.state == "VIEW":
            self.thread.disconnectDevice()
                
    @QtCore.pyqtSlot(bool)  
    def device_connect_slot(self, device_connect):
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
        if self.state == "DEVICE":
            if self.substate == "WAIT_SUBSCRIBE":
                if data_subscribe == 1:
                    self.state = "VIEW"
                    self.substate = "OFF"
                    self.gui.contextView()
                else:
                    self.gui.log.myprint_error('Could not subscribe to all signals')
                    self.substate = "WAIT_BUTTON"
    
    #DISCOVER DEVICES    
    def refresh(self):
        if (self.state == "DEVICE") & (self.substate == "WAIT_BUTTON"):
            self.thread.listDevice()
        
    @QtCore.pyqtSlot(list)  
    def device_list_slot(self, device_list):
        if (self.state == "DEVICE") & (self.substate == "WAIT_BUTTON"):
            self.gui.bio_graph.device_comboBox.clear()
            self.gui.bio_graph.device_comboBox.addItems(device_list)
    
    #OPENING AND CLOSING    
    def closeWindows(self):
        self.gui.stopTimers()
        if not self.state == "SERVER":
            self.thread.closePort()
        
    def execute_gui(self):
        ret = self.exec_()
        sys.exit(ret)

            
main = MyApp()
main.execute_gui()
