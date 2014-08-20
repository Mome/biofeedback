import serial
import time
from thread import start_new_thread

print "opening Serial port ..."

ser = serial.Serial('/dev/ttyUSB0', 115200)

time.sleep(2)
print "Initialize Complete"

end = False

def end_m():
    global end
    raw_input()
    end = True

start_new_thread(end_m,())

f = open('ecg_record','a')

while not end :
    line = ser.readline()
    line = line.replace('\0','')
    #print line
    f.write(line)

f.close()
ser.close()
