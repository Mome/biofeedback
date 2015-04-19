import time

import matplotlib.pyplot as plt
import matplotlib.collections as collections

import data_preprocessing as dpp
import data_access as da


def get_filtered_plot(subject, session):
    
    physio_data = da.get_physio_data(subject, session)  

    physio_data = da.get_physio_data(subject, session)
    physio_time = array(physio_data['time'])
    ecg_signal = array(physio_data['ecg'])
    gsr_signal = array(physio_data['gsr'])

    if len(physio_time) == 0 :
        raise Exception('not physio data')

    physio_start = physio_time[0]

    # using my block times extraction
    trails = dpp.extract_trail_times(game_data)
    if len(trails[0]) == 0 :
        raise Exception('no trails extracted')    
    blocks = dpp.join_trails_to_blocks(*trails)
    blocks = zip(*blocks)

    #blocks = da.get_block_times(subject, session)
    #blocks = dpp.change_block_times_format(blocks)

    no_filter_lot = plot_with_backcolors(blocks, gsr_signal, physio_time)
    title('no filter ' + subject + ' ' + session) 

    #nans = isnan(gsr_signal)
    #print('any(nans)', any(nans))

    gsr_signal, physio_time = dpp.process_gsr(gsr_signal, physio_time)

    # below 5 set to 5
    #gsr_signal[gsr_signal < 5] = 5

    # reinject nans for plotting
    #gsr_signal[nans] = float('nan')

    filter_lot = plot_with_backcolors(blocks, gsr_signal, physio_time)
    title('filter ' + subject + ' ' + session)
    xlabel('minutes')

    block_time_str=dpp.blocks_to_str(blocks,'blocks '+subject+' '+session, physio_start)

    return no_filter_lot, filter_lot, block_time_str


def plot_bg_colors(start_times, end_times, conditions, figure, yrange=[0,10]) :
    
    ax = figure.add_subplot(111)

    # Plot your own data here
    ax.plot(time_scale, signal)

    starts, ends, colors = zip(*block_times)


    xranges = [(s,(e-s))  for s,e in zip(start_times, end_times)]
    
    def color_choice(condition):

        if condition == 'Easy':
            return 'green'
        if condition == 'Hard':
            return 'red'
        if condition == 'Explain':
            return 'yellow'
        if condition == 'PreBaseline':
            return 'grey'
        if condition == 'PostBaseline' :
            return 'grey'
        if condition == 'Easy-False':
            return 'blue'
        if condition == 'Hard-False':
            return 'purple'

        print('Cannot assign color to condition:', condition)
        return 'black'

    colors = [color_choice(color_code) for color_code in colors]
    
    for i in range(len(xranges)) :
        coll = collections.BrokenBarHCollection([xranges[i]], yrange, facecolor=colors[i], alpha=0.5)
        ax.add_collection(coll)

    return figure
 

def plot_with_backcolors(block_times, signal, time_scale):

    # convert to minutes and normalize
    time_scale = time_scale/60
    mts = min(time_scale)
    time_scale = time_scale - mts
    block_times = [(bt[0]/60-mts, bt[1]/60-mts, bt[2]) for bt in block_times]

    figure = plt.figure(figsize=(60, 30))
    ax = figure.add_subplot(111)

    # Plot your own data here
    ax.plot(time_scale, signal)

    starts, ends, colors = zip(*block_times)


    xranges = [(start, (end-start)) for start, end in zip(starts, ends)]
    yrange = (min(signal), max(signal)-min(signal))

    def color_choice(condition):
        
        if condition == 'Easy':
            return 'green'
        if condition == 'Hard':
            return 'red'
        if condition == 'Explain':
            return 'yellow'
        if condition == 'PreBaseline':
            return 'grey'
        if condition == 'PostBaseline' :
            return 'grey'
        if condition == 'Easy-False':
            return 'blue'
        if condition == 'Hard-False':
            return 'purple'
        
        print('WTF dunno condition:', condition)
        return 'black'

    colors = [color_choice(color_code) for color_code in colors]

    for i in range(len(xranges)) :
        coll = collections.BrokenBarHCollection([xranges[i]], yrange, facecolor=colors[i], alpha=0.5)
        ax.add_collection(coll)

    return figure


def save_all_plots():
    print('database:', da.PATH_TO_DB)
    print('PHYSIO_PATH', da.PATH_TO_DB)
    import os
    directory = os.path.expanduser('~/inlusio_plots')
    if not os.path.exists(directory) :
        print('mkdir', directory)
        os.mkdir(directory)
    subject_folders = os.listdir(da.PHYSIO_PATH)
    subject_numbers = [folder.split('_')[-1] for folder in subject_folders]
    subject_numbers.sort()

    report = open(directory + os.sep + 'report','a')
    block_file = open(directory + os.sep + 'blocks','a')
    import datetime
    report.write('\n report created at ' + str(datetime.datetime.utcnow()) + '\n')

    font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 40}

    rc('font', **font)

    for subject in subject_numbers :
        for session in ['1','2'] :
            print('Try: subject', subject, 'session', session)
            no_filter, filter_ = [None,None]
            close("all")
            try :
                no_filter, filter_ , bt_str = get_filtered_plot(subject, session)
                report.write(subject + ' ' + session + ' ' + 'success\n')
                block_file.write(bt_str)
            except Exception as e :
                print('plotting failed', subject, session)
                report.write(subject + ' ' + session + ' ' + str(e) + '\n')
                report.flush()

            if no_filter != None :
                filename = directory + os.sep + subject + '_' + session + '_gsr_no-filter.svg'
                #no_filter.savefig(filename)
                
                filename = directory + os.sep + subject + '_' + session + '_gsr_filtered.svg'
                filter_.savefig(filename)
            

if __name__ == '__main__':
    import sys
    args = sys.argv

    if len(args) == 1 :
        print('need input arguments')
    elif args[1] == 'save':
        save_all_plots()
    else :
        subject = args[1]
        session = args[2]
        get_filtered_plot(subject, session)
        show()


def main():
    import sys
    args = sys.argv

    subject = args[1]
    session = args[2]
    
    print('database:', da.PATH_TO_DB)
    game_data = da.get_game_data3(subject, session)

    physio_data = da.get_physio_data(subject, session)
    physio_time = array(physio_data['time'])
    ecg_signal = array(physio_data['ecg'])
    gsr_signal = array(physio_data['gsr'])

    #raw_blocks = da.raw_block_times(subject, session)
    #raw_blocks = dpp.change_block_times_format(raw_blocks)

    #blocks = dpp.extract_block_times_form_game_data(game_data)

    blocks = da.get_block_times(subject, session)
    blocks = dpp.change_block_times_format(blocks)

    print(dpp.blocks_to_str(blocks,'blocks'))


    #beats, hr, hrv = dpp.process_ecg(ecg_signal, physio_time)

    plot_with_backcolors(blocks, gsr_signal, physio_time)

    nans = isnan(gsr_signal)
    #print('any(nans)', any(nans))

    gsr_signal = dpp.process_gsr(gsr_signal, physio_time)

    # below 5 set to 5
    gsr_signal[gsr_signal < 5] = 5

    # reinject nans for plotting
    gsr_signal[nans] = float('nan')


    plot_with_backcolors(blocks, gsr_signal, physio_time)

    show()
