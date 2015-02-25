# collect metainformation of data

import os
import sys
from thread import start_new_thread

from pylab import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append('../../experiment_computer')

import configurations as conf
from fancy_physio_plot import process_data
from data_preparation import get_session_files
from utils import *


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.resize(700, 500)
        self.setWindowTitle('Inlusio Data Viewer')

        tab_widget = QTabWidget()
        file_list = FileListWidget()
        subject_list = SubjectListWidget(file_list, tab_widget)

        main_box = QHBoxLayout()
        main_box.addWidget(subject_list)
        main_box.addWidget(file_list)
        main_box.addWidget(tab_widget)

        main_widget = QWidget()
        main_widget.setLayout(main_box)

        self.setCentralWidget(main_widget)
 

class SubjectListWidget(QListWidget):

    def __init__(self, file_list, tab_widget):
        QListWidget.__init__(self)
        self.add_subjects()
        self.file_list = file_list
        self.tab_widget = tab_widget
        self.currentItemChanged.connect(self.handle_action)
        self.setMaximumWidth(150)

    def add_subjects(self):
        file_names = os.listdir(conf.data_path)
        for name in file_names :
            print name
            if os.path.isdir(conf.data_path + os.sep + name) and name.startswith('subject_'):
                self.addItem(name)

    def handle_action(self):
        subject_folder = str(self.currentItem().text())

        self.file_list.set_file_items(subject_folder)

        subject_id = subject_folder.split('_')[1]

        session_dict = get_session_files(subject_id)

        self.tab_widget.clear()
        print session_dict
        for name in session_dict :
            if is_int(name) :
                tab = PlotSettingsWidget(session_dict[name], session_dict['physio_meta'], session_dict['scores'])
                self.tab_widget.addTab(tab, 'Session '+str(name))


class FileListWidget(QListWidget):

    def __init__(self):
        QListWidget.__init__(self)
        self.itemDoubleClicked.connect(self.open_file)
        self.setMaximumWidth(200)

    def set_file_items(self, folder_name):
        file_names = os.listdir(conf.data_path + os.sep + folder_name)
        self.folder_name = str(folder_name)
        self.clear()
        for name in file_names :
            self.addItem(name)

    def open_file(self):
        file_name = str(self.currentItem().text())
        path = conf.data_path + os.sep + self.folder_name + os.sep + file_name
        cmd = conf.editor + ' ' + path
        QProcess.startDetached(cmd)


class PlotSettingsWidget(QWidget):

    def __init__(self, session_d, meta_file, scores_file):
        QWidget.__init__(self)
        print 'inti'

        self.plots = []

        b_plot = QPushButton("Plot")

        lower_box = QHBoxLayout()
        lower_box.addStretch(1)
        lower_box.addWidget(b_plot)

        main_box = QVBoxLayout()
        main_box.addStretch(1)
        main_box.addLayout(lower_box)

        self.setLayout(main_box)

        b_plot.clicked.connect(self.plot_data)
        show(block=False)
        self.session_d = session_d
        self.meta_file = meta_file
        self.scores_file = scores_file

    def plot_data(self) :
        physio_record_file = self.session_d['physio_record'][0] #this is assumed to have length one at this point
        parameters_file = self.session_d['parameters']
        smallspread_file = self.session_d['smallspread']
        print 'go'
        #plot_window = pylab_embedd.Window()
        plt = process_data(physio_record_file, parameters_file, smallspread_file, self.meta_file, self.scores_file, None)#plot_window.figure)
        #plot_window.canvas.draw()
        #plot_window.show()
        self.plots.append(plt)
        print 'done'


def main(args):
    app = QApplication(args)
    table = DataTable(data, 5, 3)
    table.show()
    sys.exit(app.exec_())
 
if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())