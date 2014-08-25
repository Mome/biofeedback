import serial
import time
from thread import start_new_thread

print "opening Serial port ..."

connect = False

try :
    ser = serial.Serial('/dev/ttyUSB0', 115200)
    connect = True
except :
    pass

if not connect :
    try :
        ser = serial.Serial('/dev/tty.usbserial-A900abvG', 115200)
        connect = False
    except :
        print 'cannot build connection'

time.sleep(2)
print "Initialize Complete"

end = False

def end_m():
    global end
    raw_input()
    end = True

start_new_thread(end_m,())

f = open('ecg_gsr_record','a')

while not end :
    line = ser.readline()
    line = line.replace('\0','')
    #print line
    f.write(line)

f.close()
ser.close()
