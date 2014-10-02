#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
import socket

class LivePlotter :
    
    def __init__(self):
        self.app = QtGui.QApplication([])
        p = pg.plot()
        p.setWindowTitle('live plot from serial')
        self.curve = p.plot()
        port = 49152
        self.data = [0]*200
        self.ptr = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('',port))

    def update(self):
        #line = raw.readline()
        line = -1
        #while line == -1 :
        line, addr = sock.recvfrom(1024)
        line = float(line.split()[1])
        self.data[ptr%200] = line
        xdata = np.array(self.data, dtype='float64')
        #print xdata
        self.curve.setData(xdata)
        self.ptr += 1
        self.app.processEvents()

    def start(self) :
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(0)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    
    lp = LivePlotter()
    lp.start()
    
