#!/usr/bin/python

# menubar.py 

import sys
import stream_manager
import configurations as conf
import threading

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(700, 500)
        self.setWindowTitle('Inlusio Experiment Manager')

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

        # ---- for demostration ----
        reader = stream_manager.DummyStreamReader()
        bfs = stream_manager.BufferedStreamReader(reader)
        # --------------------------

        animated_plotter = AnimatedPlotter(bfs)
        record = QtGui.QPushButton("Record")
        record.setCheckable(True)
        
        top_box = QtGui.QHBoxLayout()
        top_box.addWidget(animated_plotter)

        bottom_box = QtGui.QHBoxLayout()
        bottom_box.addStretch(1)
        bottom_box.addWidget(record)

        main_box = QtGui.QVBoxLayout()
        main_box.addLayout(top_box)
        main_box.addLayout(bottom_box)

        main_widget = QtGui.QWidget()
        main_widget.setLayout(main_box)
        self.setCentralWidget(main_widget)

        bfs.start()
        animated_plotter.start()
        print 'This is the end'

        self.show()
        
        raw_input('enter to quit')
        bfs.stop()


class AnimatedPlotter(pg.PlotWidget):

    def __init__(self,bfs,lane,display_len=100,plot_type='cont'):
        pg.PlotWidget.__init__(self)
        self.bfs = bfs
        self.display_len=display_len
        self.lane = lane
        pg.setConfigOption('foreground', 'y')
        if plot_type in ['cont','overflow'] :
            self.x = list(range(display_len))
            self.y = [0]*display_len
        elif plot_type == 'quetsch' :
            self.x = list(range(10000))
            self.y = [-1]
        self.plot_type = plot_type
        self.plot_index = 0

    def update(self):
        data = self.bfs.read()
        data = [float(d.split(conf.data_delimiter)[self.lane]) for d in data]
        if self.plot_type=='cont':
            self.y.extend(data)
            self.plot(self.x,self.y[-self.display_len:],clear=True)
            for i in range(-len(data),0):
                if min(self.y[i],self.y[i-1])!=-1 :
                    self.y[i]=(self.y[i]+self.y[i-1])/2
                
        elif self.plot_type=='overflow':
            for d in data :
                self.y[self.plot_index]=d
                self.plot_index = (self.plot_index+1)%self.display_len
            self.plot(self.x,self.y,clear=True)
        
        elif self.plot_type=='quetsch':
            self.y.extend(data)
            self.plot(self.x[-len(self.y):],self.y,clear=True)
            for i in range(-len(data),0):
                if min(self.y[i],self.y[i-1])!=-1 :
                    self.y[i]=(self.y[i]+self.y[i-1])/2

    def start(self):
        self.time=QtCore.QTimer()
        self.time.timeout.connect(self.update)
        self.time.start(60)


def display_plotter_only(buffered_pipe,lane):
    print 1
    app = QtGui.QApplication(sys.argv)
    print 2
    window = QtGui.QMainWindow()
    print 3
    window.resize(500, 500)
    print 4
    window.setWindowTitle('Biofeedback Plot')
    print 5
    animated_plotter = AnimatedPlotter(buffered_pipe,lane)
    print 6
    window.setCentralWidget(animated_plotter)
    print 7
    animated_plotter.start()
    print 8
    window.show()
    print 9
    app.exec_()
    print 10
    

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = QtGui.QMainWindow()
    #if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #    QtGui.QApplication.instance().exec_()
    sys.exit(app.exec_())
