#!/usr/bin/python

# boxlayout.py

import sys
from PyQt4 import QtGui, QtCore


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.setWindowTitle('Inlusio Experiment Manager')
        
        menubar = self.menuBar()
 
        self.statusBar()        
 
        plot_widget = QtGui.QTextEdit()
        record = QtGui.QPushButton("Record")
        record.setCheckable(True)
        speed = QtGui.QDoubleSpinBox()        
        speed.setRange(0,1)
        speed.setSingleStep(0.1)

        plot_box = QtGui.QHBoxLayout()
        #plot_box.addStretch(1)
        plot_box.addWidget(plot_widget)

        plot_options = QtGui.QVBoxLayout()
        ecg_cb = QtGui.QCheckBox('plot ECG')
        gsr_cb = QtGui.QCheckBox('plot GSR')
        filter_noise = QtGui.QCheckBox('filter noise')
        plot_options.addWidget(ecg_cb)
        plot_options.addWidget(gsr_cb)
        plot_options.addWidget(filter_noise)
        plot_options.addWidget(speed)
        plot_options.addStretch(1)
        plot_box.addLayout(plot_options)        

        bottom_box = QtGui.QHBoxLayout()
        bottom_box.addStretch(1)
        bottom_box.addWidget(record)

        main_box = QtGui.QVBoxLayout()
        main_box.addLayout(plot_box)
        main_box.addLayout(bottom_box)

        main_widget = QtGui.QWidget()
        main_widget.setLayout(main_box)
        self.setCentralWidget(main_widget)

        self.resize(700, 500)

if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
