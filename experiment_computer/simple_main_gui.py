# collect metainformation of data

import os
import sys
import time
from thread import start_new_thread

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import configurations as conf
import metadata
import stream_manager
from utils import is_int


class MainWindow(QMainWindow):

    def __init__(self, manager, app):
        QMainWindow.__init__(self)

        self.resize(200, 150)
        self.setWindowTitle('Recorder')
        self.setWindowIcon(QIcon('icon/ecg-icon.png'))

        upper_box = QHBoxLayout()
        ecg_plot = PlotButton('plot ECG', 'ecg', manager)
        gsr_plot = PlotButton('plot GSR', 'gsr', manager)
        upper_box.addWidget(ecg_plot)
        upper_box.addWidget(gsr_plot)

        middle_box = QHBoxLayout()
        terminal_button = TerminalButton(manager)
        sound_button = SoundButton(manager)
        middle_box.addWidget(terminal_button)
        middle_box.addWidget(sound_button)

        record = RecordButton(self, manager)

        main_box = QVBoxLayout()
        main_box.addLayout(upper_box)
        main_box.addLayout(middle_box)
        main_box.addWidget(record)

        main_widget = QWidget()
        main_widget.setLayout(main_box)

        self.setCentralWidget(main_widget)

        self.manager = manager
        self.app = app
        self.recording = False

    def canExit(self):
        return not self.recording

    def closeEvent(self, event):
        # do stuff
        if self.canExit() :
            event.accept() # let the window close
        else:
            QMessageBox.warning(
            self, 'Termination request refused !',
            'You cannot close the application while recording data!')
            event.ignore()


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

    def __init__(self, main_window, manager):
        QPushButton.__init__(self, 'RECORD')
        self.toggled.connect(self.handle_action)
        self.setCheckable(True)
        self.manager = manager
        self.ignore_check = False
        self.main_window = main_window

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

            self.main_window.recording = True

            self.setStyleSheet("background-color: red")

            file_path = stream_manager.FileWriter.construct_filepath(rd.subject_id, rd.session)

            subject = metadata.Subject(rd.subject_id)
            record_number = subject.get_next_record_number()
            session = rd.session
            filename = file_path.split(os.sep)[-1]
            start_time = time.time()
            source = 'arduino'
            sample_rate = conf.default_sample_rate
            column_labels = conf.default_coloumn_labels
            marker = False
            comment = ''      
            subject.add_record(record_number, filename, session, start_time, source, sample_rate, column_labels, marker, comment)

            
            self.writer = stream_manager.FileWriter(file_path)
            self.manager.addWriter(self.writer)
        else :
            self.setStyleSheet("background-color: none")
            quit_msg = "Are you sure you want to stop recording ?"
            reply = QMessageBox.question(self, 'Message', 
                    quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.manager.removeWriter(self.writer)
                time.sleep(1)
                self.writer.close()
                self.main_window.recording = False
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
            self.graph.start()
            
        else :
            self.setStyleSheet("background-color: none")
            self.manager.removeWriter(self.graph)


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
        subject_id = str(self.subject_id_le.text())
        if is_int(subject_id) and 100<=int(subject_id)<=999 :
            self.subject_id = subject_id    
        else:
            QMessageBox.warning(
            self, 'Invalid Subject ID !',
            'Please enter integer between 100 and 999.')
            return

        # test session
        session = str(self.session_le.text())
        if session in ['1','2','3','666'] :
            self.session = session
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