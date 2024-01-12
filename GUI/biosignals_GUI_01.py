# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759262 
"""
#%%
from QTDesigner.biosignals import Ui_MainWindows as ui
from GENERAL import Dynamic_Import as Dyn_import
from LOG.log import log
from PyQt5 import QtWidgets, QtCore
from DATA_MANAGERS.data_manager_02 import data_manager
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QFont
from qwt import QwtPlotCurve, QwtPlotItem, QwtText
import numpy as np

class GUI:
    """
    Class representing the graphical user interface.
    """

    def __init__(self, app, callbacks):
        """
        Initialize the GUI.

        :param app: PyQt5 application object.
        :param callbacks: List of callback functions.
        """
        self.app = app
        self.MainWindow = QtWidgets.QMainWindow()
        self.bio_graph = ui()
        self.bio_graph.setupUi(self.MainWindow)
        self.initQwtCurves()
        self.loadStyle()
        self.contextServer()
        self.MainWindow.show()
        self.log = log(self.bio_graph.logger)
        self.dmgs = []
        self.dmgs.append(data_manager(signal='bvp', signal_numbers=1, seconds=self.bio_graph.bvpWindowsSize_spinBox.value(), sample_rate=64))
        self.dmgs.append(data_manager(signal='gsr', signal_numbers=1, seconds=self.bio_graph.gsrWindowsSize_spinBox.value(), sample_rate=4))
        self.dmgs.append(data_manager(signal='tmp', signal_numbers=1, seconds=self.bio_graph.tmpWindowsSize_spinBox.value(), sample_rate=4))
        self.dmgs.append(data_manager(signal='acc', signal_numbers=3, seconds=self.bio_graph.accWindowsSize_spinBox.value(), sample_rate=32))
        self.bio_graph.btn_server.clicked.connect(callbacks[0])
        self.bio_graph.btn_refresh.clicked.connect(callbacks[1])
        self.bio_graph.btn_connect.clicked.connect(callbacks[2])
        self.bio_graph.btn_start.clicked.connect(callbacks[3])
        self.bio_graph.btn_trigger.clicked.connect(callbacks[4])
        self.bio_graph.bvpWindowsSize_spinBox.valueChanged.connect(lambda:  self.windowsSize(0))
        self.bio_graph.gsrWindowsSize_spinBox.valueChanged.connect(lambda:  self.windowsSize(1))
        self.bio_graph.tmpWindowsSize_spinBox.valueChanged.connect(lambda:  self.windowsSize(2))
        self.bio_graph.accWindowsSize_spinBox.valueChanged.connect(lambda:  self.windowsSize(3))
        self.bio_graph.PORT_spinBox.valueChanged.connect(lambda: self.set_PORT())
        self.bio_graph.IP_textEdit.textChanged.connect(lambda: self.set_IP())
        self.bio_graph.E4_server_IP_textEdit.textChanged.connect(lambda: self.set_E4_server_IP())
        self.bio_graph.btn_user.clicked.connect(self.saveFileDialog)
        self.bio_graph.btn_loadScript.clicked.connect(self.openFileNameDialog)
        self.bvp_timer = QtCore.QTimer()
        self.bvp_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.bvp_timer.timeout.connect(self.bvp_update)
        self.gsr_timer = QtCore.QTimer()
        self.gsr_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.gsr_timer.timeout.connect(self.gsr_update)
        self.tmp_timer = QtCore.QTimer()
        self.tmp_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.tmp_timer.timeout.connect(self.tmp_update)
        self.acc_timer = QtCore.QTimer()
        self.acc_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.acc_timer.timeout.connect(self.acc_update)

    def getDmgs(self):
        """
        Get the list of data managers.

        :return: List of data manager objects.
        """
        return self.dmgs

    def windowsSize(self, ind: int):
        """
        Set the window size for a specific data manager.

        :param ind: Index of the data manager in the list.
        :return: None
        """
        if ind == 0:
            self.dmgs[ind].setWindow(self.bio_graph.bvpWindowsSize_spinBox.value())
        elif ind == 1:
            self.dmgs[ind].setWindow(self.bio_graph.gsrWindowsSize_spinBox.value())
        elif ind == 2:
            self.dmgs[ind].setWindow(self.bio_graph.tmpWindowsSize_spinBox.value())
        elif ind == 3:
            self.dmgs[ind].setWindow(self.bio_graph.accWindowsSize_spinBox.value())

    def set_PORT(self):
        """
        Update the PORT constant in the application constants.

        :return: None
        """
        self.app.constants.update('port', self.bio_graph.PORT_spinBox.value())

    def set_IP(self):
        """
        Update the IP constant in the application constants.

        :return: None
        """
        self.app.constants.update('IP', self.bio_graph.IP_textEdit.text())

    def set_E4_server_IP(self):
        """
        Update the E4_server_ADDRESS constant in the application constants.

        :return: None
        """
        self.app.constants.update('E4_server_ADDRESS', self.bio_graph.E4_server_IP_textEdit.text())

    def startTimers(self):
        """
        Start data update timers and clear data buffers.

        :return: None
        """
        self.dmgs[0].clearBuffer()
        self.dmgs[1].clearBuffer()
        self.dmgs[2].clearBuffer()
        self.dmgs[3].clearBuffer()
        self.bvp_timer.start(int((1 / self.dmgs[0].freqTask) * 1000))
        self.gsr_timer.start(int((1 / self.dmgs[1].freqTask) * 1000))
        self.tmp_timer.start(int((1 / self.dmgs[2].freqTask) * 1000))
        self.acc_timer.start(int((1 / self.dmgs[3].freqTask) * 1000))

    def stopTimers(self):
        """
        Stop data update timers.

        :return: None
        """
        self.bvp_timer.stop()
        self.gsr_timer.stop()
        self.tmp_timer.stop()
        self.acc_timer.stop()

    def clear_plots(self):
        """
        Clear data plots.

        :return: None
        """
        self.bio_graph.bvp_plot.curve.setData([], [])
        self.bio_graph.bvp_plot.replot()
        self.bio_graph.gsr_plot.curve.setData([], [])
        self.bio_graph.gsr_plot.replot()
        self.bio_graph.tmp_plot.curve.setData([], [])
        self.bio_graph.tmp_plot.replot()
        self.bio_graph.acc_plot.curve1.setData([], [])
        self.bio_graph.acc_plot.curve2.setData([], [])
        self.bio_graph.acc_plot.curve3.setData([], [])
        self.bio_graph.acc_plot.replot()

    def bvp_update(self):
        """
        Update the BVP data plot with the latest samples.

        :return: None
        """
        val = self.dmgs[0].getSamples()
        self.bio_graph.bvp_plot.curve.setData(np.arange(len(val)), val[:, 1])
        self.bio_graph.bvp_plot.replot()

    def gsr_update(self):
        """
        Update the GSR data plot with the latest samples.

        :return: None
        """
        val = self.dmgs[1].getSamples()
        self.bio_graph.gsr_plot.curve.setData(np.arange(len(val)), val[:, 1])
        self.bio_graph.gsr_plot.replot()

    def tmp_update(self):
        """
        Update the Temperature data plot with the latest samples.

        :return: None
        """
        val = self.dmgs[2].getSamples()
        self.bio_graph.tmp_plot.curve.setData(np.arange(len(val)), val[:, 1])
        self.bio_graph.tmp_plot.replot()

    def acc_update(self):
        """
        Update the Accelerometer data plot with the latest samples.

        :return: None
        """
        val = self.dmgs[3].getSamples()
        self.bio_graph.acc_plot.curve1.setData(np.arange(len(val)), val[:, 1])
        self.bio_graph.acc_plot.curve2.setData(np.arange(len(val)), val[:, 2])
        self.bio_graph.acc_plot.curve3.setData(np.arange(len(val)), val[:, 3])
        self.bio_graph.acc_plot.replot()

    def saveFileDialog(self):
        """
        Open a file dialog for saving data and set the PATH for data managers.

        :return: None
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, filetype = QtWidgets.QFileDialog.getSaveFileName(self.MainWindow, "QFileDialog.getSaveFileName()", "",
                                                                   "Numpy Files (*.npy)", options=options)
        if fileName:
            # set path
            self.dmgs[0].PATH = fileName
            self.dmgs[1].PATH = fileName
            self.dmgs[2].PATH = fileName
            self.dmgs[3].PATH = fileName

    def openFileNameDialog(self, btn):
        """
        Open a file dialog for opening a Python script file and execute it.

        :param btn: The button that triggered this action.
        :return: None
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        f

    def contextDevice(self):
        """
        Set the context for the device-related UI elements.

        :return: None
        """
        self.bio_graph.btn_user.setEnabled(True)
        self.bio_graph.btn_loadScript.setEnabled(True)
        self.bio_graph.btn_server.setEnabled(True)
        self.bio_graph.btn_refresh.setEnabled(True)
        self.bio_graph.btn_connect.setEnabled(True)
        self.bio_graph.btn_start.setEnabled(False)
        self.bio_graph.device_comboBox.setEnabled(True)
        self.bio_graph.btn_server.setText("E4 server unlink")
        self.bio_graph.btn_connect.setText("Connect")
        self.bio_graph.btn_start.setText("Start")

    def contextView(self):
        """
        Set the context for the view-related UI elements.

        :return: None
        """
        self.bio_graph.btn_user.setEnabled(True)
        self.bio_graph.btn_loadScript.setEnabled(True)
        self.bio_graph.btn_server.setEnabled(True)
        self.bio_graph.btn_refresh.setEnabled(False)
        self.bio_graph.btn_connect.setEnabled(True)
        self.bio_graph.btn_start.setEnabled(True)
        self.bio_graph.device_comboBox.setEnabled(False)
        self.bio_graph.btn_server.setText("Empatica server disconnect")
        self.bio_graph.btn_connect.setText("Disconnect")
        self.bio_graph.btn_start.setText("Start")

    def initQwtCurves(self):
        """
        Initialize QwtPlotCurve objects for different signal plots (BVP, GSR, TMP, ACC).

        :return: None
        """
        # BVP
        self.bio_graph.bvp_plot.enableAxis(2, 0)
        self.bio_graph.bvp_plot.curve = QwtPlotCurve()
        self.bio_graph.bvp_plot.curve.setPen(QPen(Qt.darkBlue))
        self.bio_graph.bvp_plot.curve.setStyle(QwtPlotCurve.Lines)
        self.bio_graph.bvp_plot.curve.setRenderHint(QwtPlotItem.RenderAntialiased)
        self.bio_graph.bvp_plot.curve.setPen(QPen(Qt.green))
        self.bio_graph.bvp_plot.curve.attach(self.bio_graph.bvp_plot)
        self.bio_graph.bvp_plot.setAutoReplot(False)

        # GSR
        self.bio_graph.gsr_plot.enableAxis(2, 0)
        self.bio_graph.gsr_plot.curve = QwtPlotCurve()
        self.bio_graph.gsr_plot.curve.setPen(QPen(Qt.darkBlue))
        self.bio_graph.gsr_plot.curve.setStyle(QwtPlotCurve.Lines)
        self.bio_graph.gsr_plot.curve.setRenderHint(QwtPlotItem.RenderAntialiased)
        self.bio_graph.gsr_plot.curve.setPen(QPen(Qt.green))
        self.bio_graph.gsr_plot.curve.attach(self.bio_graph.gsr_plot)
        self.bio_graph.gsr_plot.setAutoReplot(False)

        # TMP
        self.bio_graph.tmp_plot.enableAxis(2, 0)
        self.bio_graph.tmp_plot.curve = QwtPlotCurve()
        self.bio_graph.tmp_plot.curve.setPen(QPen(Qt.darkBlue))
        self.bio_graph.tmp_plot.curve.setStyle(QwtPlotCurve.Lines)
        self.bio_graph.tmp_plot.curve.setRenderHint(QwtPlotItem.RenderAntialiased)
        self.bio_graph.tmp_plot.curve.setPen(QPen(Qt.green))
        self.bio_graph.tmp_plot.curve.attach(self.bio_graph.tmp_plot)
        self.bio_graph.tmp_plot.setAutoReplot(False)

        # ACC
        self.bio_graph.acc_plot.enableAxis(2, 0)
        self.bio_graph.acc_plot.curve1 = QwtPlotCurve()
        self.bio_graph.acc_plot.curve1.setPen(QPen(Qt.darkBlue))
        self.bio_graph.acc_plot.curve1.setStyle(QwtPlotCurve.Lines)
        self.bio_graph.acc_plot.curve1.setRenderHint(QwtPlotItem.RenderAntialiased)
        self.bio_graph.acc_plot.curve1.setPen(QPen(Qt.red))
        self.bio_graph.acc_plot.curve1.attach(self.bio_graph.acc_plot)

        self.bio_graph.acc_plot.curve2 = QwtPlotCurve()
        self.bio_graph.acc_plot.curve2.setPen(QPen(Qt.darkBlue))
        self.bio_graph.acc_plot.curve2.setStyle(QwtPlotCurve.Lines)
        self.bio_graph.acc_plot.curve2.setRenderHint(QwtPlotItem.RenderAntialiased)
        self.bio_graph.acc_plot.curve2.setPen(QPen(Qt.magenta))
        self.bio_graph.acc_plot.curve2.attach(self.bio_graph.acc_plot)

        self.bio_graph.acc_plot.curve3 = QwtPlotCurve()
        self.bio_graph.acc_plot.curve3.setPen(QPen(Qt.darkBlue))
        self.bio_graph.acc_plot.curve3.setStyle(QwtPlotCurve.Lines)
        self.bio_graph.acc_plot.curve3.setRenderHint(QwtPlotItem.RenderAntialiased)
        self.bio_graph.acc_plot.curve3.setPen(QPen(Qt.cyan))
        self.bio_graph.acc_plot.curve3.attach(self.bio_graph.acc_plot)

        self.bio_graph.acc_plot.setAutoReplot(False)

    def styleQwtPlot(self, name, elem):
        """
        Apply styling to a QwtPlot element.

        :param name: The name/title for the element.
        :param elem: The QwtPlot element to be styled.
        :return: None
        """
        font = QFont()
        font.setPixelSize(12)
        title = QwtText(name)
        title.setFont(font)
        elem.setTitle(title)
        canvas = elem.canvas()
        canvas.setLineWidth(0)
        elem.setCanvas(canvas)

    def loadStyle(self):
        """
        Load styles for QwtPlot elements and apply CSS styles to the application.

        :return: None
        """
        self.styleQwtPlot("BVP", self.bio_graph.bvp_plot)
        self.styleQwtPlot("GSR", self.bio_graph.gsr_plot)
        self.styleQwtPlot("Temperature", self.bio_graph.tmp_plot)
        self.styleQwtPlot("ACC", self.bio_graph.acc_plot)

        # Apply CSS
        with open("QTDesigner/style.css") as f:
            self.app.setStyleSheet(f.read())

