import subprocess
import socket
import sys

port = 49152

def runProcess(exe):    
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
        retcode = p.poll() #returns None while subprocess is running
        line = p.stdout.readline()
        yield line
        if(retcode is not None):
            break

def server():
    #ip = '10.42.0.1'
    ip = 'localhost'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for line in runProcess(['ping','localhost']):
        sock.sendto(line, (ip, port))

def client():
    #ip = '10.42.0.2'
    ip = 'localhost'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip,port))
    while 1:
        data, addr = sock.recvfrom(1024)
        print "received message:", data



if __name__=='__main__':
    if sys.argv[1]=='server':
        server()
    elif sys.argv[1]=='client':
        client()
