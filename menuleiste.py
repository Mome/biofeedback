#!/usr/bin/python

# menubar.py 

import sys
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(250, 150)
        self.setWindowTitle('menubar')

        exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
   
        settings = QtGui.QAction('Settings', self)
        
        ecg = QtGui.QAction('ECG plot',self,checkable=True)
        gsr = QtGui.QAction('GSR plot',self,checkable=True)
        noise_filter = QtGui.QAction('Noise Filter',self,checkable=True)

        self.statusBar()

        menubar = self.menuBar()
        f = menubar.addMenu('&File')
        f.addAction(exit)
        f.addAction(settings)
        
        v = menubar.addMenu('&View')
        v.addAction(ecg)
        v.addAction(gsr)
        v.addAction(noise_filter)
        

        


def toggle_plot_ecg() :
    print 'ecg_toggled'

def toggle_plot_gsr() :
    print 'gsr_toggled'

app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
