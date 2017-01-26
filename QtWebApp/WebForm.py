#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
"""
import os, sys

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QWaitCondition, QMutex

lib_path = os.path.abspath('../QtWebApp')

class WebForm(QWebEngineView):

    loadUrlSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        #self.load(QUrl("file:///C:/Users/Nick/Desktop/usb/QtWebApp/Demo1/etc/docroot/index.html"))
        #self.show()

    @staticmethod
    def interact(jsonData):    
        import sys
        from PyQt5.QtWidgets import QApplication

        print("interact")
        #app = QApplication(sys.argv)
        print("interact app___")
        wf = WebForm()
        wf.load(QUrl("file:///C:/Users/Nick/Desktop/usb/QtWebApp/Demo1/etc/docroot/index.html"))
        wf.show()
        print("interact wf")
        #wf.loadUrlSignal.connect(self.loadUrlSlot)
        #self.loadUrlSignal.emit()
        #ex.show()
        #sys.exit(app.exec_())

    @pyqtSlot()
    def loadUrlSlot(self):
        # Show that the slot has been called.

        print("WebForm.loadUrlSlot")
        wf = WebForm()
        print("WebForm.loadUrlSlot--")
        wf.load(QUrl("file:///C:/Users/Nick/Desktop/usb/QtWebApp/Demo1/index.html"))
        wf.show()

        print("interact1 wf")
        print("loadUrlSignal signal received")

    @staticmethod
    def interact1(jsonData):  
        # Connect the trigger signal to a slot.
        print("WebForm.interact1")
        #wf = WebForm()

        """
        print("WebForm.before emit")
        # Emit the signal.
        mutex = QMutex()
        mutex.lock()
        wf.loadUrlSignal.emit()
        waiter = QWaitCondition()
        waiter.wait(mutex)
        mutex.unlock()
        print("WebForm.after emit")
        """
        print("WebForm.interact1")
        wf = WebForm()
        print("WebForm.interact1--")
        wf.load(QUrl("file:///C:/Users/Nick/Desktop/usb/QtWebApp/Demo1/index.html"))
        wf.show()

        print("interact1 wf")
        
        #ex.show()
