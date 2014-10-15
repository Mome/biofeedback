#!/usr/bin/python

# menubar.py 

import sys
from PyQt4 import QtGui, QtCore

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

        
class AnimatedPlotter :

    def __init__(self,title,bfs,lane,display_len=500,plot_type='quetsch') :
        self.bfs = bfs
        self.display_len=display_len
        self.lane = lane
        pg.setConfigOption('foreground', 'y')
        self.window=pg.plot(title=title)
        #print dir(self.window)
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
        data = [float(d.split()[self.lane]) for d in data]
        if self.plot_type=='cont':
            self.y.extend(data)
            self.window.plot(self.x,self.y[-self.display_len:],clear=True)
            for i in range(-len(data),0):
                if min(self.y[i],self.y[i-1])!=-1 :
                    self.y[i]=(self.y[i]+self.y[i-1])/2
                
        elif self.plot_type=='overflow':
            for d in data :
                self.y[self.plot_index]=d
                self.plot_index = (self.plot_index+1)%self.display_len
            self.window.plot(self.x,self.y,clear=True)
        
        elif self.plot_type=='quetsch':
            self.y.extend(data)
            self.window.plot(self.x[-len(self.y):],self.y,clear=True)
            for i in range(-len(data),0):
                if min(self.y[i],self.y[i-1])!=-1 :
                    self.y[i]=(self.y[i]+self.y[i-1])/2

    def start(self):
        self.time=QtCore.QTimer()
        self.time.timeout.connect(self.update)
        self.time.start(60)

        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
