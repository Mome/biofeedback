import argparse

import inlusio_gui
import stream_manager


def main():
    parser = argparse.ArgumentParser(description='Read a stream and print it to some output interface.')
    parser.add_argument('-i', '--input', choices=['arduino','raspi'])
    parser.add_argument('-o', '--output', choices=['terminal','graphical','file'])
    parser.add_argument('-p', '--port')
    parser.add_argument('-f', '--filename')
    args = parser.parse_args()
    
    if args.input == None :
        i = raw_input('Choose platform - 1 for Arduino  or  2 for RasPi  : ')
        args.input = ['arduino','raspi'][int(i)-1]
    
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
    
    if args.port==None and args.input=='raspi' :
        args.port = 49152
        
    if args.filename==None and args.output == 'file':
        filename = raw_input('Please enter filename:')
           
    if args.input == 'raspi':
        stream_reader = UdpStreamReader(args.port)
        
    if args.input == 'serial' :
        stream_reader = SerialStreamReader(args.port)
    
    #print args
    #if raw_input('type exit to exit: ') == 'exit' : exit()
    
    bsr = BufferedStreamReader(stream_reader)
    
    if args.output == 'terminal' :
        bsr.start()
        for i in range(100):
            print bsr.read()
            time.sleep(1)
    
    if args.output == 'graphical' :
        plotter = AnimatedPlotter('Skin Conductance (GSR)',bsr,1)
        bsr.start()
        plotter.start()
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
        
    if args.output == 'file' :
        pass
    
    bsr.stop()
    print 'Regular termination !'
    

if __name__=='__main__':
    #reader = DummyStreamReader()
    reader = stream_manager.SerialStreamReader('COM9')

    manager = stream_manager.StreamManager(reader)
    
    #t_writer = stream_manager.TermWriter()
    #manager.addWriter(t_writer)
    
    #f_writer = stream_manager.FileWriter('pusemuckel')
    #manager.addWriter(f_writer)
    
    
    graph = stream_manager.GraphicalWriter([0,1])
    manager.addWriter(graph)
    graph.start()
    
    manager.start()
    
    
    
    # ------------------------------ #
    raw_input('Press ENTER to stop!!')
    # ------------------------------ #
    
    manager.stop()
    print 'zuende'