import argparse
import time

import configurations as conf
import metadata
import stream_manager

def main():
    parser = argparse.ArgumentParser(description='Read a stream and print it to some output interface.')
    parser.add_argument('-i', '--input', choices=['arduino','raspi','dummy'])
    parser.add_argument('-o', '--output', nargs='+', choices=['terminal','graphical','file'])
    parser.add_argument('-p', '--port')
    #parser.add_argument('-f', '--filename')
    parser.add_argument('-id', '--subject_id')
    parser.add_argument('-s', '--session')
    args = parser.parse_args()

    
    if args.input == None :
        i = raw_input('Choose one platform - 1 for Arduino,  2 for RasPi, 3 for Dummy  : ')
        args.input = ['arduino','raspi','dummy'][int(i)-1]
    
    if args.output == None :
        num = raw_input('Choose any output - 1 for Terminal ,  2 for Graphical  or  3 for File : ')
        choices = ['terminal','graphical','file']
        args.output=[]
        for i in num :
            args.output.append(choices[int(i)-1])
    
    if args.port==None and args.input=='arduino' :
        ports = stream_manager.SerialStreamReader.list_serial_ports()
        print 'Available ports:', ports
        if len(ports) > 1 :
            args.port = raw_input('Choose a port: ')
        elif len(ports) == 1 :
            args.port = ports[0]
            print 'chose port', args.port
        else :
            print 'No ports found!'
            exit()
    elif args.port==None and args.input=='raspi' :
        args.port = conf.default_raspi_port

    if args.input == 'raspi':
        reader = stream_manager.UdpStreamReader(args.port)      
    elif args.input == 'arduino' :
        reader = stream_manager.SerialStreamReader(args.port)
    elif args.input == 'dummy':
        reader = stream_manager.DummyStreamReader()

    manager = stream_manager.StreamManager(reader)
    
    if 'terminal' in args.output :
        t_writer = stream_manager.TermWriter()
        manager.addWriter(t_writer)

    if 'graphical' in args.output :
        graph = stream_manager.GraphicalWriter([1,0])
        manager.addWriter(graph)
        graph.start()

    if 'file' in args.output :

        if args.subject_id == None:
            subject_id = raw_input('subject_id: ')
            if subject_id == '' : subject_id = 0
        else :
            subject_id = args.subject_id
        subject_id = int(subject_id)

        if args.session == None:
            session = raw_input('session: ')
            if session == '' : session = -1
        else :
            session = args.session
        session = int(session)


        subject = metadata.Subject(subject_id)
        record_number = subject.get_next_record_number()

        file_name = stream_manager.FileWriter.construct_filename(subject_id,record_number)

        f_writer = stream_manager.FileWriter(file_name)
        manager.addWriter(f_writer)

        start_time = time.time()
        sample_rate = conf.default_sample_rate
        column_labels = conf.default_coloumn_labels
        marker = False
        comment = ''
        source = args.input
        subject.add_record(record_number, file_name, session, start_time, source, sample_rate, column_labels, marker, comment)

    manager.start()
    
    # ------------------------------ #
    raw_input('Press ENTER to stop!!')
    # ------------------------------ #
    
    manager.stop()
    print 'zuende'

if __name__=='__main__':
    main()