"""Command line interface to record e-Health data.

-i, --input : arduino, raspi, dummy

"""



import argparse
import os
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
        num = raw_input('Choose any output - 1 for Terminal ,  2 for Graphical,  3 for File  or 4 for Audio: ')
        choices = ['terminal','graphical','file','audio']
        args.output=[]
        for i in num :
            args.output.append(choices[int(i)-1])
    
    if args.port==None and args.input=='arduino' :
        #ports = stream_manager.SerialStreamReader.list_serial_ports()
        ports = [port_tuple[0] for port_tuple in stream_manager.list_comports()]
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
        plot_mask = [2,1]
    elif args.input == 'arduino' :
        reader = stream_manager.SerialStreamReader(args.port)
        plot_mask = [0,1]
    elif args.input == 'dummy':
        reader = stream_manager.DummyStreamReader()
        plot_mask = [0,1]

    # plot_labels = ['ecg','gsr']

    manager = stream_manager.StreamManager(reader)
    
    if 'terminal' in args.output :
        t_writer = stream_manager.TermWriter()
        manager.addWriter(t_writer)

    if 'graphical' in args.output :
        graph = stream_manager.GraphicalWriter(plot_mask)
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

        filepath = stream_manager.FileWriter.construct_filepath(subject_id,session,record_number)

        f_writer = stream_manager.FileWriter(filepath)
        manager.addWriter(f_writer)

        start_time = time.time()
        sample_rate = conf.default_sample_rate
        column_labels = conf.default_coloumn_labels
        marker = False
        comment = ''
        source = args.input
        subject.add_record(record_number, filepath, session, start_time, source, sample_rate, column_labels, marker, comment)
    
    if 'audio' in args.output :
        t_writer = stream_manager.AudioWriter(plot_mask)
        manager.addWriter(t_writer)
    
    manager.start()
    
    # ------------------------------ #
    raw_input('Press ENTER to stop!!')
    # ------------------------------ #
    
    manager.stop()
    print 'zuende'

def create_singelton():
    home_folder = os.path.expanduser('~')
    open(home_folder + os.sep + 'physio_singleton_lock','w')

def remove_singleton():
    home_folder = os.path.expanduser('~')
    os.remove(home_folder + os.sep + 'physio_singleton_lock')

def singleton_exists():
    home_folder = os.path.expanduser('~')
    return os.path.exists(home_folder + os.sep + 'physio_singleton_lock')

if __name__=='__main__':
    if not singleton_exists() :
        try :
            create_singelton()
            main()
        finally :
            remove_singleton()
    else :
        print 'Programm already running.'
        print 'Close other instances !! If you are sure no other instance is running remove the file "physio_singleton_lock" from your home directory.'
        raw_input('Press ENTER to continue.')
