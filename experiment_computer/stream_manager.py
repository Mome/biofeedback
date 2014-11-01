import itertools
import math
import os
import random
import socket
import subprocess
import sys
import threading
import time

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import serial

import configurations as conf


class UdpStreamReader:
    
    def __init__(self, port=49152):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',port))

    def read(self):
        data, addr = self.sock.recvfrom(1024)
        return data


class SerialStreamReader():

    def __init__(self, port, baud=115200):    
        self.port = port
        self.baud = baud
        self.ser = serial.Serial(port, baud)
    
    def read(self):
        return self.ser.readline().strip()
    
    @classmethod
    def list_serial_ports(cls):
        """Lists serial ports

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result 


class DummyStreamReader:
    
    def __init__(self, mean_sleep=0.1, std_sleep=0.001, funcs=['ecg','sin']):
        self.port = 'DummyPort'

        for i,func in enumerate(funcs) :
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
            elif func == 'cos' :
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

    def __init__(self, filename, timed=True):
        
        if not os.path.exists(conf.data_path) :
            os.makedirs(conf.data_path)
        
        path = os.path.normpath(conf.data_path + '/' + filename)
        
        if os.path.exists(path) :
            raise Exception('Datafile ' + path + ' already exists !')

        self.file = open(path,'a')
        self.filename = filename
        self.timed=timed
        self.set_starting_time()

    def set_starting_time(self,starting_time=None) :
        if starting_time == None :
            self.starting_time = time.time()
        else :
            self.starting_time = starting_time

    def write(self,data):
        if self.timed :
            time_elapse = str(int(round((time.time()-self.starting_time) * 1000)))
            self.file.write(time_elapse + conf.data_delimiter + data + '\n')
        else :
            self.file.write(data + '\n')

    def close(self):
        self.file.close()

    @classmethod
    def construct_filename(cls,subject_id,record_number=None):

        # add additional zeros 
        if subject_id < 10 :
            subject_id = '00' + str(subject_id)
        elif subject_id <= 100 :
            subject_id = '0' + str(subject_id)
        else :
            subject_id = str(subject_id)

        # find right file ending for data_delimiter
        if conf.data_delimiter == ',' :
            ending = '.csv'
        elif conf.data_delimiter == '\t' :
            ending = '.tsv'
        elif conf.data_delimiter == ' ' :
            ending = '.ssv'
        else :
            ending = '.dsv'

        if record_number == None :
            file_list = os.listdir(conf.data_path)
            file_list = [f[4:-4] for f in file_list if f.startswith(subject_id)]
            file_list = [int(f) for f in file_list if f.isdigit()]
            if file_list == [] :
                record_number = 0
            else :
                record_number = max(file_list)+1

        # add additional zeros 
        if record_number < 10 :
            record_number = '00' + str(record_number)
        elif record_number <= 100 :
            record_number = '0' + str(record_number)
        else :
            record_number = str(record_number)
        
        file_name = subject_id + '_' + record_number + ending

        #if os.path.exists(file_ path) :
        #    raise Exception('File already exists. Wont overwrite data!')

        return file_name

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

    def write(self, data):
        print data


class GraphicalWriter:
    
    def __init__(self, lanes, data_buffer_size=3000, plot_type=1):
        self.lanes = lanes
        self.data_buffer_size = data_buffer_size
        self.plot_type = plot_type
        self.app = QtGui.QApplication([])

        self.plots = []
        self.curves = []
        self.indices = []

        for l in lanes :
            p = pg.plot()
            p.setWindowTitle('Inlusio Live-Plot: ' + str(l))
            p.showGrid(True,True)
            p.showButtons()
            p.setMenuEnabled()
            #p.setYRange(-1.1,8000,False)
            #p.setXRange(0,data_buffer_size,False)
            self.plots.append(p)
            self.curves.append(p.plot())
        
        self.index = 0
        
        if type(lanes) == int :
            lanes=[lanes]
        self.data = np.zeros((len(lanes),data_buffer_size))
    
    def write(self,new_data):
        new_data = np.array([float(d) for d in new_data.split(conf.data_delimiter)])
        new_data = new_data[self.lanes]
        self.data[:,self.index] = new_data
        # silly noise reduction #
        #prev_index = (self.index-1)%self.data_buffer_size
        #self.data[:,prev_index] = (self.data[:,prev_index]*0.999 + self.data[:,self.index]*0.001)
        # --------------------- #
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


class StreamManager:

    def __init__(self,stream_reader):
        self.stream_reader = stream_reader
        self.writers = []
        self.is_running = False

    def addWriter(self,writer):
        self.writers.append(writer)

    def start(self):
        if self.is_running :
            raise Exception('StreamManager already running!')
        self.is_running = True
        threading.Thread(target=self._run).start()
        print 'StreamManager reading at port: ' + str(self.stream_reader.port) + ' !'

    def _run(self) :
        while self.is_running :
            data = self.stream_reader.read()
            for w in self.writers :
                w.write(data)

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
    """ Calls a programm and streams stdout to some port via udp"""
    
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
 