from pylab import *

import data_preprocessing as dpp
import data_access as da

import time


def easy_plot(subject, session):

    physio_data = da.get_physio_data(subject, session)
    physio_time = array(physio_data['time'])
    ecg_signal = array(physio_data['ecg'])
    gsr_signal = array(physio_data['gsr'])

    blocks = da.get_block_times(subject, session)
    blocks = dpp.change_block_times_format(blocks)

    #beats, hr, hrv = dpp.process_ecg(ecg_signal, physio_time)

    #gsr_signal = dpp.low_pass(gsr_signal,'cos',100)
    #gsr_signal = dpp.process_gsr(gsr_signal, physio_time)

    plt = plot_with_backcolors(blocks, gsr_signal, physio_time)

    show(block=False)

    return plt


def plot_with_backcolors(block_times, signal, time_scale):
    import matplotlib.pyplot as plt
    import matplotlib.collections as collections

    figure = plt.figure()
    ax = figure.add_subplot(111)

    # Plot your own data here
    ax.plot(time_scale, signal)

    #xad = list(copy(x_axis_divisions))
    #xad.append(graph_data[0][-1])
    #xranges = [(xad[i],xad[i+1]-xad[i]) for i in range(len(xad)-1)]
    starts, ends, colors = zip(*block_times)

    #for s,e,c in block_times :
    #    print(time.asctime(time.gmtime(s)), ' | ', time.asctime(time.gmtime(e)), ' | ', c)

    #print('block start:', [time.asctime(time.gmtime(t)) for t in starts])
    #print('block ends:', time.asctime(time.gmtime(ends[-1])))

    xranges = [(start, (end-start)) for start, end in zip(starts, ends)]
    #print(xranges, colors)
    yrange = (0, 15)

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


if __name__ == '__main__' :
    import sys
    args = sys.argv

    subject = args[1]
    session = args[2]
    
    print('database:', da.PATH_TO_DB)
    game_data = da.get_game_data(subject, session)

    physio_data = da.get_physio_data(subject, session)
    physio_time = array(physio_data['time'])
    ecg_signal = array(physio_data['ecg'])
    gsr_signal = array(physio_data['gsr'])

    #raw_blocks = da.raw_block_times(subject, session)
    #raw_blocks = dpp.change_block_times_format(raw_blocks)

    #blocks = dpp.extract_block_times_form_game_data(game_data)

    blocks = da.get_block_times(subject, session)
    blocks = dpp.change_block_times_format(blocks)

    dpp.print_blocks(blocks)


    #beats, hr, hrv = dpp.process_ecg(ecg_signal, physio_time)

    plot_with_backcolors(blocks, gsr_signal, physio_time)

    nans = isnan(gsr_signal)
    print('any(nans)', any(nans))

    gsr_signal = dpp.process_gsr(gsr_signal, physio_time)

    # below 5 set to 5
    gsr_signal[gsr_signal < 5] = 5

    # reinject nans for plotting
    gsr_signal[nans] = float('nan')


    plot_with_backcolors(blocks, gsr_signal, physio_time)

    show()
