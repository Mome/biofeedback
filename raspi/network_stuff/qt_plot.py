#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
import socket

app = QtGui.QApplication([])

p = pg.plot()
p.setWindowTitle('live plot from serial')
curve = p.plot()
port = 49152
data = [0]*200
ptr = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('',port))

def update():
    global curve, data, ptr
    #line = raw.readline()
    line = -1
    #while line == -1 :
    line, addr = sock.recvfrom(1024)
    line = float(line.split()[1])
    data[ptr%200] = line
    xdata = np.array(data, dtype='float64')
    print xdata
    curve.setData(xdata)
    ptr += 1
    app.processEvents()

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
