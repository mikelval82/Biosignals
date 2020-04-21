# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 18:17:11 2018

@author: LENOVO
"""
from PyQt5 import QtGui, QtCore

class log():  
    
    def __init__(self,logger):
        self.logger = logger
        self.logger.setCenterOnScroll(True)
        self.tf = QtGui.QTextCharFormat()
        self.tf_green = QtGui.QTextCharFormat()
        self.tf_red = QtGui.QTextCharFormat()
        self.tf_green.setForeground(QtGui.QBrush(QtCore.Qt.green))
        self.tf_red.setForeground(QtGui.QBrush(QtCore.Qt.red))
        
        
    def myprint(self, text):
        self.logger.setCurrentCharFormat(self.tf)
        self.logger.appendPlainText(text)
        self.logger.centerCursor()
        
    def myprint_in(self, text):
        self.logger.setCurrentCharFormat(self.tf_green)
        self.logger.appendPlainText("< "+text)
        self.logger.centerCursor()
    
    def myprint_out(self, text):
        self.logger.setCurrentCharFormat(self.tf_green)
        self.logger.appendPlainText("> "+text)
        self.logger.centerCursor()
        
    def myprint_error(self, text):
        self.logger.setCurrentCharFormat(self.tf_red)
        self.logger.appendPlainText(text)
        self.logger.centerCursor()
        
    def clear(self):
        self.logger.clear()
    
   