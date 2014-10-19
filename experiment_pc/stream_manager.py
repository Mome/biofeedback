import argparse
import experiment_manager
import math
import os
import random
import serial
import socket
import subprocess
import sys
import threading
import time
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
    
    def __init__(self, mean_sleep=0.1, std_sleep=0.01, func1=math.sin, func2=math.cos):
        self.mean_sleep = mean_sleep
        self.std_sleep = std_sleep
        self.func1 = func1
        self.func2 = func2
        self.port = 'DummyPort'

    def read(self):
        time.sleep(random.gauss(self.mean_sleep,self.std_sleep))
        v1 = self.func1(time.time())
        v2 = self.func2(time.time())
        return str(v1) + conf.data_delimiter + str(v2)


class FileWriter:

    def __init__(self, filename, timed=True):
        
        FileWriter.check_and_create_data_path()

        path = conf.data_path + filename
        if os.path.exists(path) :
            raise Exception('Datafile ' + path + ' already exists !')

        self.file = open(conf.data_path + filename,'a')
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
            #TODO find next record number 
            record_number = 0
        else :
            #TODO check for existing files
            pass

        return subject_id + '_' + str(record_number) +'.' + ending

    @classmethod
    def check_and_create_data_path(cls):
        path = [p for p in conf.data_path.split('/') if p!='']
        test_path = ''
        for p in path :
            test_path += '/' + p
            if os.path.exists(test_path) :
                if not os.path.isdir(test_path):
                    raise Exception(test_path + ' already exists, but is a file !!')
            else :
                os.mkdir(test_path)
                print 'mkdir ' + test_path

class TermWriter:

    def write(self, data):
        print data


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


class BufferedPipe:
    
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

    
def main():
    parser = argparse.ArgumentParser(description='Read a stream and print it to some output interface.')
    parser.add_argument('-i', '--input', choices=['network','serial'])
    parser.add_argument('-o', '--output', choices=['terminal','graphical','file'])
    parser.add_argument('-p', '--port')
    parser.add_argument('-f', '--filename')
    args = parser.parse_args()
    
    if args.input == None :
        i = raw_input('Choose platform - 1 for Arduino  or  2 for RasPi  : ')
        args.input = ['serial','network'][int(i)-1]
    
    if args.output == None :
        i = raw_input('Choose output - 1 for Terminal ,  2 for Graphical  or  3 for File : ')
        args.output = ['terminal','graphical','file'][int(i)-1]
    
    if args.port==None and args.input=='serial' :
        ports = SerialStreamReader.list_serial_ports()
        print 'Available ports:', ports
        if len(ports) > 1 :
            args.port = raw_input('Choose a port: ')
        elif len(ports) == 1 :
            args.port = ports[0]
            print 'chose port', args.port
        else :
            print 'No ports found!'
            exit()
    
    if args.port==None and args.input=='network' :
        args.port = 49152
        
    if args.filename==None and args.output == 'file':
        filename = raw_input('Please enter filename:')
           
    if args.input == 'network'  :
        stream_reader = UdpStreamReader(args.port)
        
    if args.input == 'serial' :
        stream_reader = SerialStreamReader(args.port)
    
    #print args
    #if raw_input('type exit to exit: ') == 'exit' : exit()
    
    bsr = BufferedStreamReader(stream_reader)
    
    
    if args.output == 'terminal' :
        bsr.start()
        for i in range(100):
            print bsr.read()
            time.sleep(1)
    
    if args.output == 'graphical' :
        plotter = AnimatedPlotter('Skin Conductance (GSR)',bsr,1)
        bsr.start()
        plotter.start()
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
        
    if args.output == 'file' :
        pass
    
    bsr.stop()
    print 'Regular termination !'
    

if __name__=='__main__':
    reader = DummyStreamReader()
    
    #t_writer = TermWriter()
    #f_writer = FileWriter('pusemuckel')
    buffered_pipe0  = BufferedPipe()
    buffered_pipe1  = BufferedPipe()

    manager = StreamManager(reader)
    #manager.addWriter(t_writer)
    #manager.addWriter(f_writer)
    manager.addWriter(buffered_pipe0)
    manager.addWriter(buffered_pipe1)
    manager.start()
    experiment_manager.display_plotter_only(buffered_pipe0,0)
    experiment_manager.display_plotter_only(buffered_pipe1,1)    

    manager.stop()
    print 'zuende'

