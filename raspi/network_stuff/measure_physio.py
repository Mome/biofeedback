import argparse
import socket
import serial
import subprocess
import threading

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
        self.stop=True
        self.index=0
        
    def start(self):
        if not self.stop :
            print 'Already running!'
        else :
            self.stop=False
            threading.Thread(target=self._run).start()
            print 'Reading udp-socket buffered at port: ' + str(self.port) + ' !'

    def _run(self):
        while not self.stop:
            data = self.stream_reader.read()
            self.buffer[self.index]=data
            self.index+=1
            if self.index == self.buffer_size:
                self.index = 0
                print 'Buffer_overflow!'
        print 'BufferedClient: Stop running!'
        
    def stop(self):
        self.stop=True
    
    def read(self):
        while not self.stop :
            out = self.buffer[:self.index]
            self.index = 0
            return out


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
    parser.add_argument('-o', '--output', nargs='+', choices=['terminal','graphical','file'])
    parser.add_argument('-p', '--port')
    parser.add_argument('-f', '--filename')
    args = parser.parse_args()
    
    if args.port==None and args.input=='serial' :
        ports = SerialStreamReader.list_serial_ports()
        print 'Available ports:', ports
        if len(ports) > 1 :
            port = raw_input('Choose a port: ')
        elif len(ports) == 1 :
            port = ports[0]
        else :
            print 'No ports found!'
            exit()
    
    if args.port==None and args.input=='network' :
        port = 49152
        
    if filename==None and 'file' in args.output:
        filename = raw_input('Please enter filename:')
           
    if args.input == 'network'  :
        stream_reader = UdpStreamReader(port)
        
    if args.input == 'serial' :
        stream_reader = SerialStreamReader(port)
    
    bsr = BufferedStreamReader(stream_reader)
    
    bfs.start()
    
    import time
    for i in range(100):
        print bfs.read()
        time.sleep(1)
    

if __name__=='__main__':
    main()
