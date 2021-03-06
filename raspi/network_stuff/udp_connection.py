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

def server(app):
    #ip = '10.42.0.1' # ad_hoc
    ip = '131.173.37.185' # windows pc (carpo)
    #ip = '131.173.37.182' # shitty pc (dolly10)
    #ip = '131.173.36.240' 3 dhcp ip for moses
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for line in runProcess(app):
        #print line.strip()
	line = line.strip().replace(' ',',')
        sock.sendto(line.strip(), (ip, port))

def client():
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
