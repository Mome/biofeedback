# collect metainformation of data

import os
import sys

from pylab import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import data_access as da
import data_preprocessing as dpp
import fancy_plot

global_plot_storage = []


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
        file_names = os.listdir(da.PHYSIO_PATH)
        for name in file_names :
            print(name)
            if os.path.isdir(da.PHYSIO_PATH + os.sep + name) and name.startswith('subject_'):
                self.addItem(name)

    def handle_action(self):
        subject_folder = str(self.currentItem().text())

        self.file_list.set_file_items(subject_folder)

        subject_id = subject_folder.split('_')[1]

        session_dict = get_session_files(subject_id)

        seblf.tab_widget.clear()
        print(session_dict)
        for name in session_dict :
            if is_int(name) :
                tab = PlotSettingsWidget(session_dict[name], session_dict['physio_meta'])
                self.tab_widget.addTab(tab, 'Session '+str(name))


class FileListWidget(QListWidget):

    def __init__(self):
        QListWidget.__init__(self)
        self.itemDoubleClicked.connect(self.open_file)
        self.setMaximumWidth(200)

    def set_file_items(self, folder_name):
        file_names = os.listdir(da.PHYSIO_PATH + os.sep + folder_name)
        self.folder_name = str(folder_name)
        self.clear()
        for name in file_names :
            self.addItem(name)

    def open_file(self):
        file_name = str(self.currentItem().text())
        path = da.PHYSIO_PATH + os.sep + self.folder_name + os.sep + file_name
        cmd = conf.editor + ' ' + path
        QProcess.startDetached(cmd)


class PlotSettingsWidget(QWidget):

    def __init__(self, session_d, meta_file):
        QWidget.__init__(self)
        print('inti')

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
        self.session_d = session_d
        print('session_d',session_d)
        self.meta_file = meta_file
        print('done in the middle')

    def plot_data(self) :
        print('go')
        #plot_window = pylab_embedd.Window()
        plt = fancy_plot.easy_plot(320,1)
        #plot_window.canvas.draw()
        #plot_window.show()
        global_plot_storage.append(plt)
        print(global_plot_storage)
        print('done')

# constructs a dict that categorizes filenames of a subject folder
def get_session_files(subject_id):

    folder = da.PHYSIO_PATH + os.sep + 'subject_' + str(subject_id)
    files = os.listdir(folder)

    session_files = {}


    for name in files :
        parts = name.split('.')[0]
        parts = parts.split('_')

        # find session
        if parts[0] == 'physio' and parts[1] == 'record' :

            session = parts[3]

            if session not in session_files :
                session_files[session] = {'physio_record':[],'parameters':None,'smallspread':None}

            session_files[session]['physio_record'] += [name]

        elif parts[0] == 'Smallspread' :

            session = parts[2]

            if session not in session_files :
                session_files[session] = {'physio_record':[],'parameters':None,'smallspread':None,'scores':None}

            session_files[session]['smallspread'] = name

        elif parts[0] == 'parameters' :

            session = parts[2]

            if session not in session_files :
                session_files[session] = {'physio_record':[],'parameters':None,'smallspread':None,'scores':None}

            session_files[session]['parameters'] = name

        elif name == 'SubjectScores.csv' :
            session_files['scores'] = name

        elif parts[0] == 'physio' and parts[1] == 'meta' :
            session_files['physio_meta'] = name

        else :
            if 'other' not in session_files :
                session_files['other'] = []
            session_files['other'] += [name]

    return session_files

def main(args):
    app = QApplication(args)
    table = DataTable(data, 5, 3)
    table.show()
    sys.exit(app.exec_())

def is_int(num):
    try :
        int(num)
    except :
        return False
    return True
 
if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())