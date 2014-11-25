import subprocess
import socket
import sys
from threading import Thread

class BufferedClient:
    
    def __init__(self, port=49152, buffer_size=1024):
        self.port = port
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',port))
        self.stop=True
        self.buffer=[0]*buffer_size
        self.index=0
        
    def start(self):
        def run():
            while not self.stop:
                data, addr = self.sock.recvfrom(1024)
                self.buffer[self.index]=data
                self.index+=1
                if self.index == self.buffer_size:
                    self.index = 0
                    print 'Buffer_overflow!'
            print 'BufferedClient: Stop running!'
  
        if not self.stop :
            print 'Already running!'
        else :
            self.stop=False
            Thread(target=run).start()
            print 'Reading udp-socket buffered at port: ' + str(self.port) + ' !'
           
    def stop(self):
        self.stop=True
    
    def read(self):
        while not self.stop :
            out = self.buffer[:self.index]
            self.index = 0
            return out
            

def runProcess(exe):    
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
        retcode = p.poll() #returns None while subprocess is running
        line = p.stdout.readline()
        yield line
        if(retcode is not None):
            break

def server(app):
    ip = '10.42.0.1'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for line in runProcess(app):
        sock.sendto(line.strip(), (ip, port))

def client():
    ip = '10.42.0.2'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('',port))
    while 1:
        data, addr = sock.recvfrom(1024)
        print "received message:", data

if __name__=='__main__':
    if sys.argv[1]=='server':
        server(sys.argv[2:])
    elif sys.argv[1]=='client':
        client()
