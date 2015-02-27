from pylab import *

import data_preprocessing as dpp
import data_access as da


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
    print('starts', starts, diff(starts))
    print('ends', ends, diff(ends))
    xranges = [(start, end-start)for start, end in zip(starts, ends)]
    print(xranges, colors)
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

    game_data = da.get_game_data(subject, session)

    physio_data = da.get_physio_data(subject, session)
    physio_time = array(physio_data['time'])
    ecg_signal = array(physio_data['ecg'])
    gsr_signal = array(physio_data['gsr'])

    blocks = da.get_block_times(subject, session)
    blocks = dpp.change_block_times_format(blocks)

    print(blocks)

    #beats, hr, hrv = dpp.process_ecg(ecg_signal, physio_time)

    plot_with_backcolors(blocks, gsr_signal, physio_time)

    show()