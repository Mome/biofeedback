# collect metainformation of data

import os
import sys
from time import sleep
from thread import start_new_thread

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import configurations as conf
import stream_manager
from utils import is_int


class MainWindow(QMainWindow):

    def __init__(self, manager, app):
        QMainWindow.__init__(self)

        self.resize(200, 150)
        self.setWindowTitle('Recorder')

        ecg_box = QHBoxLayout()
        ecg_plot = PlotButton('plot ECG', 'ecg', manager)
        ecg_sound = SoundButton(manager)
        ecg_box.addWidget(ecg_plot)
        ecg_box.addWidget(ecg_sound)
        ecg_box.addStretch(1)

        gsr_box = QHBoxLayout()
        gsr_plot = PlotButton('plot GSR', 'gsr', manager)
        gsr_sound = SoundButton(manager)
        gsr_box.addWidget(gsr_plot)
        gsr_box.addWidget(gsr_sound)
        gsr_box.addStretch(1)

        terminal = TerminalButton(manager)

        record = RecordButton(manager)

        main_box = QVBoxLayout()
        main_box.addLayout(ecg_box)
        main_box.addLayout(gsr_box)
        main_box.addWidget(terminal)
        main_box.addWidget(record)

        main_widget = QWidget()
        main_widget.setLayout(main_box)

        self.setCentralWidget(main_widget)

        #self.destroyed.connect

        self.manager = manager
        self.app = app


class SoundButton(QPushButton):

    def __init__(self, manager):
        QPushButton.__init__(self)
        self.setIcon(QIcon('icons/sound_off_black.svg'))
        self.toggled.connect(self.handle_action)
        self.setCheckable(True)
        self.manager = manager


    def handle_action(self):
        if self.isChecked() :
            self.setIcon(QIcon('icons/sound_on_black.svg'))
            self.setStyleSheet("background-color: orange")
            self.writer = stream_manager.AudioWriter()
            self.manager.addWriter(self.writer)
        else :
            self.manager.removeWriter(self.writer)
            self.setIcon(QIcon('icons/sound_off_black.svg'))
            self.setStyleSheet("background-color: none")



class RecordButton(QPushButton):

    def __init__(self, manager):
        QPushButton.__init__(self, 'RECORD')
        self.toggled.connect(self.handle_action)
        self.setCheckable(True)
        self.manager = manager
        self.ignore_check = False

    def handle_action(self):

        # This is neccessary because setting the button unchecked,
        # when the parameter dialog is canceled raises the toggled signal 
        if self.ignore_check :
            self.ignore_check = False
            return

        if self.isChecked() :
            
            rd = RecordDialog()

            if rd.exec_() == 0 :
                self.ignore_check = True
                self.setChecked(False)
                return


            self.setStyleSheet("background-color: red")
            file_path = stream_manager.FileWriter.construct_filepath(rd.subject_id, rd.session)
            self.writer = stream_manager.FileWriter(file_path)
            self.manager.addWriter(self.writer)

        else :
            self.setStyleSheet("background-color: none")
            quit_msg = "Are you sure you want to stop recording ?"
            reply = QMessageBox.question(self, 'Message', 
                    quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.manager.removeWriter(self.writer)
                sleep(1)
                self.writer.close()
            else:
                self.setStyleSheet("background-color: red")
                self.ignore_check = True
                self.setChecked(True)


class PlotButton(QPushButton):

    def __init__(self,name, type_, manager):
        QPushButton.__init__(self, name)
        self.toggled.connect(self.handle_action)
        self.setCheckable(True)
        if type_ == 'ecg' :
            self.plot_mask = [0]
        elif type_ == 'gsr' :
            self.plot_mask = [1]

        self.manager = manager

    def handle_action(self):
        if self.isChecked() :
            self.setStyleSheet("background-color: green")
            self.graph = stream_manager.GraphicalWriter(self.plot_mask, app=app)
            self.manager.addWriter(self.graph)
            #self.graph.plt.destroyed.connect(self.window_closed)
            self.graph.start()
            for d in dir(self.graph.plt) :
                print d
        else :
            self.setStyleSheet("background-color: none")
            self.manager.removeWriter(self.graph)

    def window_closed(self):
        print 'window_closed'


class TerminalButton(QPushButton):

    def __init__(self, manager):
        QPushButton.__init__(self, 'print to terminal')
        self.toggled.connect(self.handle_action)
        self.setCheckable(True)
        self.manager = manager

    def handle_action(self):
        if self.isChecked() :
            self.setStyleSheet("background-color: yellow")
            self.writer = stream_manager.TermWriter()
            self.manager.addWriter(self.writer)
        else :
            self.setStyleSheet("background-color: none")
            self.manager.removeWriter(self.writer)

class RecordDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self)

        id_label = QLabel('Subject ID:')
        self.subject_id_le = QLineEdit(self)    
        id_box = QHBoxLayout()
        id_box.addWidget(id_label)
        id_box.addWidget(self.subject_id_le)

        session_label = QLabel('Session:')
        self.session_le = QLineEdit(self)    
        session_box = QHBoxLayout()
        session_box.addWidget(session_label)
        session_box.addWidget(self.session_le)

        self.start = QPushButton('Start Recording !', self)
        self.start.clicked.connect(self.submit)

        layout = QVBoxLayout(self)
        layout.addLayout(id_box)
        layout.addLayout(session_box)
        layout.addWidget(self.start)
        self.setWindowTitle('Enter Parameters')

    def submit(self):

        #test subject_id
        if is_int(self.subject_id_le.text()) and 100<=int(self.subject_id_le.text())<=999 :
            self.subject_id = self.subject_id_le.text()     
        else:
            QMessageBox.warning(
            self, 'Invalid Subject ID !',
            'Please enter integer between 100 and 999.')
            return

        # test session
        if self.session_le.text() in ['1','2','3','666'] :
            self.session = self.session_le.text()
        else :
            QMessageBox.warning(
            self, 'Invalid Session !',
            'Please enter 1,2,3 or 666.\n(use 666 for testing only)')
            return

        self.accept()
 
if __name__ == '__main__':

    #reader = stream_manager.SerialStreamReader('auto')
    reader = stream_manager.DummyStreamReader()
    manager = stream_manager.StreamManager(reader)

    manager.start()

    app = QApplication(sys.argv)
    main = MainWindow(manager, app)
    main.show()
    ex = app.exec_()
    manager.stop()
    sys.exit(ex)