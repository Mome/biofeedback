import argparse
import serial
import socket
import subprocess
import sys
import threading
import time


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
    

class BufferedStreamReader:
    
    def __init__(self, stream_reader, buffer_size=1024):
        self.stream_reader = stream_reader
        self.buffer_size = buffer_size
        self.buffer=[0]*buffer_size
        self.is_stopped=True
        self.index=0
        
    def start(self):
        if not self.is_stopped :
            print 'Already running!'
        else :
            self.is_stopped=False
            threading.Thread(target=self._run).start()
            print 'Reading udp-socket buffered at port: ' + str(self.stream_reader.port) + ' !'

    def _run(self):
        while not self.is_stopped:
            data = self.stream_reader.read()
            self.buffer[self.index]=data
            self.index+=1
            if self.index == self.buffer_size:
                self.index = 0
                print 'Buffer overflow!'
        print 'BufferedStreamReader stopped!'
    
    def stop(self):
        self.is_stopped=True
    
    def read(self):
        out = self.buffer[:self.index]
        self.index = 0
        print 'len(out):', len(out)
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

                
class AnimatedPlotter :

    def __init__(self, bfs, display_len=200):
        self.bfs = bfs # buffered stream reader
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_ylim(-1.1, 3.0)
        #self.ax.set_xlim(0, 5)
        self.ax.grid()
        self.xdata = list(range(display_len))
        self.ydata = [0]*display_len

    def data_gen(self):
        t = 0
        while True :
            lines = self.bfs.read()           
            lines = [line.split()[1] for line in lines]
            if len(lines) > 0 :
                yield lines
            else :
                print 'No data received !'
                yield [0]
            t+=1
    
    #def data_gen(self):
    #    cnt = 0
    #    while cnt < 1000:
    #        cnt+=1
    #        self.t += 0.05
    #        yield self.t, np.sin(2*np.pi*self.t) * np.exp(-self.t/10.)
    
    def run(self, data):
        self.ydata = self.ydata[len(data):] + data
        print self.ydata
        self.line.set_data(self.xdata, self.ydata)
        return self.line,

    def start(self):
        ani = animation.FuncAnimation(self.fig, self.run, self.data_gen, blit=True, interval=10, repeat=False)
        plt.show()
    
    
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
    
    print args
    if raw_input('type exit to exit: ') == 'exit' : exit()
    
    bsr = BufferedStreamReader(stream_reader)
    
    
    if args.output == 'terminal' :
        bsr.start()
        for i in range(100):
            print bsr.read()
            time.sleep(1)
    
    if args.output == 'graphical' :
        plotter = AnimatedPlotter(bsr)
        bsr.start()
        plotter.start()
        
    if args.output == 'file' :
        pass
    
    bsr.stop()
    print 'Regular termination !'
    

if __name__=='__main__':
    main()
