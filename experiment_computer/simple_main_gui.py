"""GUI for inlusio physiological data recording.

Other than the commandline interface the GUI supports by default recording from
arduino only. If the e-Health setup is plugged into a USB port a Window with
five different buttons will open.

Buttons :
plot ECG - open a pyqtgraph animated plot window, that shows the ecg input stream
plot GSR - open a pyqtgraph animated plot window, that shows the gsr input stream

"""

import os
import sys
import time

from PyQt4.QtGui import *

import configurations as conf
import metadata
import stream_manager
from utils import *


class MainWindow(QMainWindow):
    """Contains all the Buttons."""

    def __init__(self, manager, app, noecg, nogsr):
        QMainWindow.__init__(self)

        lanes = []
        if not noecg :
            lanes.append(0)
        if not nogsr :
            lanes.append(1)
        self.lanes = tuple(lanes)

        self.resize(200, 150)
        self.setWindowTitle('PhysioRecorder')
        self.setWindowIcon(QIcon('icon/ecg-icon.png'))

        upper_box = QHBoxLayout()
        if not noecg:
            ecg_plot = PlotButton('plot ECG', 'ecg', main_window=self)
            upper_box.addWidget(ecg_plot)
        if not nogsr:
            gsr_plot = PlotButton('plot GSR', 'gsr', main_window=self)
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
        self.noecg = noecg
        self.nogsr = nogsr
        self.recording = False

    def canExit(self):
        return not self.recording

    def closeEvent(self, event):
        # do stuff
        if self.canExit():
            event.accept() # let the window close
        else:
            QMessageBox.warning(
                self, 'Termination request refused !',
                'You cannot close the application while recording data!')
            event.ignore()


class SoundButton(QPushButton):
    """Button to activate an acoustic error signal if input data stream leaves
    valid region."""

    def __init__(self, manager):
        QPushButton.__init__(self)
        self.setIcon(QIcon('icons/sound_off_black.svg'))
        self.toggled.connect(self.handle_action)
        self.setCheckable(True)
        self.manager = manager

    def handle_action(self):
        if self.isChecked():
            self.setIcon(QIcon('icons/sound_on_black.svg'))
            self.setStyleSheet("background-color: orange")
            self.writer = stream_manager.AudioWriter()
            self.manager.addWriter(self.writer)
        else:
            self.manager.removeWriter(self.writer)
            self.setIcon(QIcon('icons/sound_off_black.svg'))
            self.setStyleSheet("background-color: none")


class RecordButton(QPushButton):
    """Button to start writing data to harddisk."""

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
        if self.ignore_check:
            self.ignore_check = False
            return

        if self.isChecked():

            rd = RecordDialog()

            if rd.exec_() == 0:
                self.ignore_check = True
                self.setChecked(False)
                return

            self.main_window.recording = True

            self.setStyleSheet("background-color: red")

            file_path = stream_manager.FileWriter.construct_filepath(rd.subject_id, rd.session)

            subject = metadata.Subject(rd.subject_id)
            record_number = subject.get_next_record_number(rd.session)
            session = rd.session
            filename = file_path.split(os.sep)[-1]
            start_time = time.time()
            source = 'arduino'
            sample_rate = conf.default_sample_rate

            column_labels = ['absolute_time']
            if not noecg :
                column_labels.append('ecg')
            if not nogsr :
                column_labels.append('gsr')

            subject.add_record(record_number, filename, session,
                               start_time, source, sample_rate,
                               column_labels)

            self.writer = stream_manager.FileWriter(
                file_path = file_path,
                timed = 'absolute',
                columns = column_labels,
                lanes = self.main_window.lanes,
                )
            self.manager.addWriter(self.writer)
        else:
            self.setStyleSheet("background-color: none")
            quit_msg = "Are you sure you want to stop recording ?"
            reply = QMessageBox.question(self, 'Message',
                                         quit_msg,
                                         QMessageBox.Yes,
                                         QMessageBox.No)

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
    """Button to toggle the life-plotting of an input stream."""

    def __init__(self, name, type_, main_window):
        QPushButton.__init__(self, name)
        self.toggled.connect(self.handle_action)
        self.setCheckable(True)
        if type_ == 'ecg':
            self.plot_mask = [0]
        elif type_ == 'gsr':
            self.plot_mask = [1]

        self.main_window = main_window

    def handle_action(self):
        if self.isChecked():
            self.setStyleSheet("background-color: green")
            self.graph = stream_manager.GraphicalWriter(self.plot_mask, app=self.main_window.app)
            self.main_window.manager.addWriter(self.graph)
            self.graph.start()

        else:
            self.setStyleSheet("background-color: none")
            self.main_window.manager.removeWriter(self.graph)


class TerminalButton(QPushButton):
    """Toggle printing input stream to stdout."""

    def __init__(self, manager):
        QPushButton.__init__(self, 'print to terminal')
        self.toggled.connect(self.handle_action)
        self.setCheckable(True)
        self.manager = manager

    def handle_action(self):
        if self.isChecked():
            self.setStyleSheet("background-color: yellow")
            self.writer = stream_manager.TermWriter()
            self.manager.addWriter(self.writer)
        else:
            self.setStyleSheet("background-color: none")
            self.manager.removeWriter(self.writer)

class RecordDialog(QDialog):
    """Dialog to enter subject and session ID."""

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
        if is_int(subject_id) and (100 <= int(subject_id) <= 999):
            self.subject_id = subject_id
        else:
            QMessageBox.warning(
                self, 'Invalid Subject ID !',
                'Please enter integer between 100 and 999.')
            return

        # test session
        session = str(self.session_le.text())
        if session in ['1', '2', '3', '666']:
            self.session = session
        else:
            QMessageBox.warning(
                self, 'Invalid Session !',
                'Please enter 1,2,3 or 666.\n(use 666 for testing only)')
            return

        self.accept()


def start_gui():
    noecg = False
    nogsr = False

    for arg in sys.argv[1:]:
        if arg == 'dummy':
            reader = stream_manager.DummyStreamReader()
        elif arg == 'noecg':
            noecg = True
        elif arg == 'nogsr':
            nogsr = False
        else:
            print 'unknown commandline parameter', sys.arv[1]
            sys.exit()

    # Use the serial reader for arduino as default
    if 'reader' not in locals():
        reader = stream_manager.SerialStreamReader('auto')

    manager = stream_manager.StreamManager(reader)

    manager.start()

    app = QApplication(sys.argv)
    main = MainWindow(manager, app, noecg, nogsr)
    main.show()
    ex = app.exec_()
    manager.stop()
    sys.exit(ex)


def main():
    if not singleton_exists() :
        try :
            create_singelton()
            start_gui()
        finally :
            remove_singleton()
    else :
        print 'Programm already running.'
        print 'Close all other instances !! If you are sure no other instance is running remove the file "physio_singleton_lock" from your home directory.'
        raw_input('Press ENTER to continue.')


if __name__ == '__main__':
    main()