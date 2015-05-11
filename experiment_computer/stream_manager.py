import itertools
import math
import os
import random
import socket
import subprocess
import sys
import threading
import time

import numpy as np
try :
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtGui, QtCore
except ImportError as ie:
    print 'Print Graphical Plotting not possible :', str(ie)
from serial import Serial, SerialException

try :
    from serial.tools.list_ports import comports as list_comports
except :
    print 'autochoose port for arduino not available, possibly update pyserial'

try :
    import winsound
except :
    print 'Winsound not available !'


import configurations as conf
from utils import is_float


class UdpStreamReader:
    
    def __init__(self, port=49152):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',port))

    def read(self):
        data, addr = self.sock.recvfrom(1024)
        return data


class SerialStreamReader:
    """Reads data from USB-port."""

    def __init__(self, port, baud=115200):
        self.port = port
        self.baud = baud
        self.sleeping_time = 0.1
        self.connected = False
        self.reconnect()
    
    def read(self): 
        
        try :
            return self.ser.readline().strip()
        except SerialException:
            print 'Serial disconnected'
            self.connected = False
            self.reconnect()
            return self.ser.readline().strip()
    
    def reconnect(self):
    
        if self.port != 'auto':
            try :
                self.ser = Serial(self.port, self.baud)
                self.connected = True
                return
            except SerialException:
                self.connected = False
        
        while not self.connected :
            port = self.autochoose_port()
            while port == None :
                port = self.autochoose_port()
                time.sleep(self.sleeping_time)
            self.port = port
            try :
                self.ser = Serial(self.port, self.baud)
                self.connected = True
            except :
                self.connected = False
        
        print 'Connected to', self.port
    
    def autochoose_port(self):
        """Automatically chooses the comport where the device information is
           identically to a string saved in the configurations file.
           Trimmed to last information from pyserial's list_comports method"""
        
        if sys.platform.startswith('linux'):
            target_port_id = conf.linux_port_id_2
        elif sys.platform.startswith('win'):
            target_port_id = conf.win_port_id_2
        else :
            print 'Port autochoose not supported for', os.platform
        
        target_port = None
        
        for port, port_id_1, port_id_2  in list_comports():
            
            if port_id_2 == target_port_id:
                target_port = port
                break
        
        return target_port


class DummyStreamReader:
    """Stream dummy for testing."""
    
    def __init__(self, mean_sleep=0.1, std_sleep=0.001, funcs=['ecg','sin']):
        self.port = 'DummyPort'

        for i,func in enumerate(funcs):
            if func == 'ecg':
                mean_sleep = 0.0078125 #128Hz
                # reads lines from ecg file, puts it in an iterator and converts it to a function
                ecg_data_path = conf.module_path + os.sep + '..' + os.sep + 'data' + os.sep + 'sample_data' + os.sep + 'ecg_sample.csv'
                with open(ecg_data_path) as csv_file :
                    ecg_data=[float(line.strip()) for line in csv_file.readlines() if line.strip()!='' and line.strip()[0]!='#']
                    ecg_iter = itertools.cycle(ecg_data)
                    funcs[i] = lambda _ : ecg_iter.next()
            elif func == 'sin':
                funcs[i] = math.sin
            elif func == 'cos':
                funcs[i] = math.cos
            else :
                funcs[i] = lambda _ : 1

        self.mean_sleep = math.log(mean_sleep) + (std_sleep)**2
        #print self.mean_sleep
        self.std_sleep = std_sleep
        self.funcs = funcs

    def read(self):
        #print random.lognormvariate(self.mean_sleep,self.std_sleep)
        time.sleep(random.lognormvariate(self.mean_sleep,self.std_sleep))
        out_str = ''
        for func in self.funcs :
            out_str +=str(func(time.time())) + conf.data_delimiter
        return out_str[:-1]


class FileWriter:
    """Writes data to a file."""

    def __init__(self, file_path, timed='absolute', columns=None, lanes=None):
        
        # dont know if I still need that #
        if os.path.exists(file_path) :
            raise Exception('Datafile ' + file_path + ' already exists !')

        self.file = open(file_path,'a')
        self.file_path = file_path
        self.timed=timed
        self.set_starting_time()
        self.lanes = lanes
        self.columns = columns

        self.file.write(conf.data_delimiter.join(columns) + '\n')



    def set_starting_time(self,starting_time=None) :
        if starting_time == None :
            self.starting_time = time.time()
        else :
            self.starting_time = starting_time

    def write(self,data):

        data = data.split(conf.data_delimiter)

        if self.lanes != None :
            data = [data[i] for i in self.lanes]

        if self.timed == 'absolute':
            data = [time.time().__repr__()] + data
        elif self.timed == 'relative':
            time_elapse = str(int(round((time.time()-self.starting_time) * 1000)))
            data = [time_elapse] + data

        data = conf.data_delimiter.join(data)
        self.file.write(data + '\n')

    def close(self):
        self.file.close()

    @classmethod
    def construct_filepath(cls, subject_id, session, record_number=None):

        # add additional zeros 
        """if subject_id < 10 :
            subject_id = '00' + str(subject_id)
        elif subject_id <= 100 :
            subject_id = '0' + str(subject_id)
        else : """
        
        subject_id = str(subject_id)
        session = str(session)

        folder_path = os.path.normpath(conf.data_path + os.sep +'subject_' + subject_id)
        file_beginning = 'physio_record_' + subject_id + '_' + session + '_'

        # find right file ending for data_delimiter
        if conf.data_delimiter == ',' :
            ending = '.csv'
        elif conf.data_delimiter == '\t' :
            ending = '.tsv'
        elif conf.data_delimiter == ' ' :
            ending = '.ssv'
        else :
            ending = '.dsv'
        
        # put this to another place
        if not os.path.exists(folder_path) :
            os.makedirs(folder_path)

        if record_number == None :#and os.path.exists(folder_path):
            file_list = os.listdir(folder_path)
            file_list = [f[len(file_beginning):-len(ending)] for f in file_list if f.startswith(file_beginning)]
            file_list = [int(f) for f in file_list if f.isdigit()]
            if file_list == [] :
                record_number = 0
            else :
                record_number = max(file_list)+1

        # add additional zeros 
        """if record_number < 10 :
            record_number = '00' + str(record_number)
        elif record_number <= 100 :
            record_number = '0' + str(record_number)
        else :"""
        
        record_number = str(record_number)
        
        filename = file_beginning + record_number + ending
        
        file_path =  folder_path + os.sep + filename
        
        #if os.path.exists(file_ path) :
        #    raise Exception('File already exists. Wont overwrite data!')

        return file_path
        
        
class RamWriter:

    def __init__(self, data, maximum):
        self.ram = [None]*maximum
        self.index = 0

    def write(self, data):
        try :
            self.ram[self.index] = data
            self.index += 1
        except :
            return False
        return True


class TermWriter:
    """Write data to stdout."""

    def write(self, data):
        print data


class GraphicalWriter:
    """Animated plot using pyqtgraph."""
    
    def __init__(self, lanes, data_buffer_size=700, plot_type=1, app=None):
        self.lanes = lanes
        self.data_buffer_size = data_buffer_size
        self.plot_type = plot_type

        if app == None :
            self.app = QtGui.QApplication([])
        else :
            self.app = app

        self.plots = []
        self.curves = []
        self.indices = []

        for l in lanes :
            p = pg.plot()
            p.setWindowTitle('Inlusio Live-Plot: ' + str(l))
            p.showGrid(True,True)
            p.showButtons()
            p.setMenuEnabled()
            if l == 1 :
                p.setYRange(-1.1,15,False)
                p.setXRange(0,data_buffer_size,False)
            self.plots.append(p)
            self.curves.append(p.plot())
            self.plt = p
        
        self.index = 0
        
        if type(lanes) == int :
            lanes=[lanes]
        self.data = np.zeros((len(lanes),data_buffer_size))
    
    def write(self,new_data):
        try :
            new_data = np.array([float(d) for d in new_data.split(conf.data_delimiter)])
        except ValueError as ve:
            print str(ve), new_data
            return
        new_data = new_data[self.lanes]
        self.data[:,self.index] = new_data
        
        self.index = (self.index+1)%self.data_buffer_size
    
    def update(self):

        for l in range(len(self.lanes)) :
            plot_data = self.data[l]
            
            if self.plot_type==1:
                plot_data = np.hstack([plot_data[self.index:],plot_data[:self.index]])
                
            self.curves[l].setData(plot_data)
        self.app.processEvents()
    
    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16.6)

# fix this to be usable with lane parameter
class AudioWriter:
    """Plays a beep sound, if data recording leaves valid range."""
 
    def __init__(self):
        self.ecg_upper_limit = 5.0
        self.ecg_lower_limit = 0.0
        self.gsr_upper_limit = float('inf')
        self.gsr_lower_limit = -1.0
        
        self.data_error_freq = 1500
        self.gsr_freq = 1000
        self.ecg_freq = 500
        
        self.duration = 120 # msecs
        self.wait_time = 2.5

        self.sound_list = []
    
    def write(self, new_data) :
        
        if len(self.sound_list) != 0 :
            return
        
        new_data = new_data.split(',')

        if len(new_data) != 2 :
            self.sound_list.append('data_error')
            return

        ecg, gsr = new_data

        if not is_float(ecg) :
            self.sound_list.append('ecg')
            
        if not is_float(gsr) :
            self.sound_list.append('gsr')
        
        if not is_float(ecg) or not is_float(gsr) :
            return
        
        ecg = float(ecg) 
        gsr = float(gsr)
        
        if self.ecg_upper_limit <= ecg or ecg <= self.ecg_lower_limit :
            self.sound_list.append('ecg')
        if self.gsr_upper_limit <= gsr or gsr <= self.gsr_lower_limit :
            self.sound_list.append('gsr')
        
        if len(self.sound_list) != 0 :
            self.play_sound()

    def play_sound(self):
        threading.Thread(target=self._run).start()

    def _run(self):
        for kind in self.sound_list:
            if kind == 'data_error':
                winsound.Beep(self.data_error_freq, self.duration)
                print 'Input data format error !'
            elif kind == 'ecg':
                winsound.Beep(self.ecg_freq, self.duration)
                print 'ecg problem'
            elif kind == 'gsr':
                winsound.Beep(self.gsr_freq, self.duration)
                print 'gsr problem'
            else :
                raise ValueExeption('unknown kind', type(kind), str(kind))
        time.sleep(self.wait_time)
        self.sound_list = []


class StreamManager:
    """Manages the distribution of streams."""

    def __init__(self, stream_reader):
        self.stream_reader = stream_reader
        self.writers = []
        self.is_running = False
        self.jobs = []

    def addWriter(self, writer):
        if not self.is_running :
            self.writers.append(writer)
        else:
            self.jobs.append(('add',writer))

    def removeWriter(self, writer):
        if not self.is_running:
            self.writers.remove(writer)
        else:
            self.jobs.append(('rem',writer))

    def start(self):
        if self.is_running:
            raise Exception('StreamManager already running!')
        self.is_running = True
        threading.Thread(target=self._run).start()
        #print 'StreamManager reading at port: ' + str(self.stream_reader.port) + ' !'

    def _run(self) :
        while self.is_running :
            data = self.stream_reader.read()
            for w in self.writers:
                w.write(data)

            if self.jobs == []:
                continue

            jobs = self.jobs
            self.jobs = []

            for job in jobs :
                if job[0] == 'add':
                    self.writers.append(job[1])
                elif job[0] == 'rem':
                    self.writers.remove(job[1])
                else :
                    print 'No such job:', job[0]

            #print self.writers

    def stop(self):
        self.is_running = False


class StreamBuffer:
    
    def __init__(self, buffer_size=1024):
        self.buffer_size = buffer_size
        self.buffer=[0]*buffer_size
        self.index=0

    def write(self,data):
        self.buffer[self.index]=data
        self.index+=1
        if self.index == self.buffer_size:
            self.index = 0
            print 'Buffer overflow!'
    
    def read(self):
        out = self.buffer[:self.index]
        self.index = 0
        #print 'len(out):', len(out)
        return out
    
    def sleep_and_read(self,delay=0.1):
        time.sleep(delay)
        return self.read()


class UdpStreamer :
    """Call a programm and streams stdout to some port via udp."""
    
    def __init__(self, app_path, destination):
        if destination == 'adhock':
            self.ip='10.42.0.1'
        elif destination in ('win','carpo'):
            self.ip='131.173.37.185'
        else :
            self.ip=destination
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stop == True
    
    def start(self):
        if not self.stop :
            print 'Already running!'
        else :
            self.stop=False
            threading.Thread(target=self._run).start()
            print 'Streaming to - ip: ' + self.ip + 'port: ' + str(self.port) + ' !'
    
    def _run(self):
        for line in UdpStreamer.runProcess(app):
            self.sock.sendto(line.strip(), (self.ip, self.port))
            if self.stop:
                break
    
    def stop(self):
        self.stop=True
    
    @classmethod
    def runProcess(cls,exe):    
        p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while(True):
            retcode = p.poll() #returns None while subprocess is running
            line = p.stdout.readline()
            yield line
            if(retcode is not None):
                break
