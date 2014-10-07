import serial
import time
import sys
import glob

def serial_ports():
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


if __name__ == '__main__' :

    #arduino = serial.Serial(2, 9600, timeout=1)
    #ser = serial.Serial('/dev/tty.usbserial', 9600)
    #ser = serial.Serial('/dev/ttyUSB0', 115200)\
    
    baud = 115200

    ports = serial_ports()
    print 'Available ports:', ports
    if len(ports) > 1 :
        port = raw_input('Choose a port: ')
    elif len(ports) == 1 :
        port = ports[0]
    else :
        print 'No ports found!'
        exit()
    
    try :
        ser = serial.Serial(port, baud, timeout=0)
    except :
        print 'Could not open!'    
    
    print "Initialize Complete"

    while 1:
        print ser.readline()
        #time.sleep(0.2)
       
