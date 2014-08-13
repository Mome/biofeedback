import serial, time
import numpy as np
from matplotlib import pyplot as plt

print "opening Serial port ..."
ser = None

try :
    ser = serial.Serial('/dev/ttyUSB0', 115200)
except :
    print 'cannot open /dev/ttyUSB0'

if ser == None :
    try :
        ser = serial.Serial('/dev/ttyUSB1', 115200)
    except :
        print 'cannot open /dev/ttyUSB1'
        print 'Abort everything!'

time.sleep(2)
print "Initialize Complete"


#end = False

#def end_m():
#    global end
#    raw_input()
#    end = True

#start_new_thread(end_m,())


plt.ion() # set plot to anumated

ydata = [0] * 50 

ax1=plt.axes()

# make plot
line, = plt.plot(ydata)
#plt.ylim([-1,10]) # set the y-range to -1 to 10

f = open('tmp_file','a')

# start data collection
while True: 
    data = ser.readline() # read data from serial port and strip line endings
    data = data.lstrip('\0')
    f.write(data)

    ymin = float(min(ydata))-10
    ymax = float(max(ydata))+10
    plt.ylim([ymin,ymax])
    ydata.append(data)
    del ydata[0]
    line.set_xdata(np.arange(len(ydata)))
    line.set_ydata(ydata)  # update the data
    plt.draw() # update the plot
