import serial
import time

print "opening Serial port ..."

#arduino = serial.Serial(2, 9600, timeout=1)
#ser = serial.Serial('/dev/tty.usbserial', 9600)
ser = serial.Serial('/dev/ttyUSB0', 115200)

time.sleep(2)
print "Initialize Complete"

while 1:
    print ser.readline()
    #print ser.readline()
    #print ser.readline()
    #time.sleep(1)
       
