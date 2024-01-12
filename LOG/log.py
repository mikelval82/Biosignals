from PyQt5 import QtGui, QtCore

class Log():
    """
    A class for managing and displaying log messages in a QTextEdit widget.
    """

    def __init__(self, logger):
        """
        Initialize the Log object.

        Args:
        - logger: QTextEdit widget for displaying log messages.
        """
        self.logger = logger
        self.logger.setCenterOnScroll(True)
        self.tf = QtGui.QTextCharFormat()
        self.tf_green = QtGui.QTextCharFormat()
        self.tf_red = QtGui.QTextCharFormat()
        self.tf_green.setForeground(QtGui.QBrush(QtCore.Qt.green))
        self.tf_red.setForeground(QtGui.QBrush(QtCore.Qt.red))

    def myprint(self, text):
        """
        Print a standard log message.

        Args:
        - text: The log message text.
        """
        self.logger.setCurrentCharFormat(self.tf)
        self.logger.appendPlainText(text)
        self.logger.centerCursor()

    def myprint_in(self, text):
        """
        Print an input log message (preceded by "<").

        Args:
        - text: The log message text.
        """
        self.logger.setCurrentCharFormat(self.tf_green)
        self.logger.appendPlainText("< " + text)
        self.logger.centerCursor()

    def myprint_out(self, text):
        """
        Print an output log message (preceded by ">").

        Args:
        - text: The log message text.
        """
        self.logger.setCurrentCharFormat(self.tf_green)
        self.logger.appendPlainText("> " + text)
        self.logger.centerCursor()

    def myprint_error(self, text):
        """
        Print an error log message in red.

        Args:
        - text: The log message text.
        """
        self.logger.setCurrentCharFormat(self.tf_red)
        self.logger.appendPlainText(text)
        self.logger.centerCursor()

    def clear(self):
        """
        Clear the log messages in the QTextEdit widget.
        """
        self.logger.clear()
