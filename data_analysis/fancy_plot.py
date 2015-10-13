from __future__ import division

from datetime import datetime
from collections import namedtuple
import copy
import os
import time

from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.collections as collections
import numpy as np

import data_preprocessing as dpp
import data_access as da


def plot_subject(subject, session, options):
    """Load, Process and plot data for one subject/session pair.

       Possible options: ('ecg','gsr','blocks','trials','plot_beats','show','save')
    """

    # transform all keys to lower case
    options = {key.lower():value for key, value in options.items()}

    # add missing keys to options and transform to namedtuple
    option_keys =('do_ecg','do_gsr','do_blocks','do_trials')
    default_opts = dict.fromkeys(option_keys, False)
    default_opts.update(options)

    if 'figsize' not in default_opts:
        default_opts['figsize'] = (15,10)

    options = namedtuple('Options', default_opts.keys())(**default_opts)

    physio_data, trials, time_range = da.get_data(subject, session)
    results = dpp.process_data(physio_data, trials, subject, session, options)
    names,figs = plot_results(results, options)

    start_time = datetime.fromtimestamp(time_range[0]).strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.fromtimestamp(time_range[1]).strftime('%Y-%m-%d %H:%M:%S')

    print 'start_time:', start_time, ' end_time:', end_time

    if options.save:
        for name,fig in zip(names,figs):
            filename = subject + '_' + session + '_' + name
            save_plot(filename, fig)

    if options.show:
        plt.show()

    
def plot_results(results, options) :
    r = results
    figs = []
    names = []
    
    if options.do_trials :
        # plot raw data and beats for trials
        fig = plt.figure(figsize=options.figsize)
        yrange = (min(r.raw_ecg), max(r.raw_ecg)-min(r.raw_ecg))
        plot_bg_colors(r.trial_starts, r.trial_ends, r.trial_conditions, fig, yrange)
        if options.do_ecg:
            plt.plot(r.time_scale, r.raw_ecg)
            beats = r.ecg_signal.beats
            height = np.ones(len(beats))*np.median(r.raw_ecg)
            plt.scatter(beats, height)
        if options.do_gsr:
            plt.plot(r.time_scale, r.raw_gsr)
        name = 'raw_data_with_trials'
        plt.title(name)
        figs.append(fig)
        names.append(name)
    
        # plot filtered data for trials
        fig = plt.figure(figsize=options.figsize)
        plot_bg_colors(r.trial_starts, r.trial_ends, r.trial_conditions, fig)
        if options.do_ecg:
            plt.plot(r.ecg_signal.time_scale, r.ecg_signal.signal)
        if options.do_gsr:
            plt.plot(r.gsr_signal.time_scale, r.gsr_signal.signal)
        name = 'filtered_gsr_with_trials'
        plt.title(name)
        figs.append(fig)
        names.append(name)

        # plot plot means for trials
        fig = plt.figure(figsize=options.figsize)
        plot_bg_colors(r.trial_starts, r.trial_ends, r.trial_conditions, fig)
        mean_trial_time = (r.trial_starts+r.trial_ends)/2
        if options.do_ecg:
            plt.plot(mean_trial_time, r.mean_hr_for_trials, label='HR')
            plt.plot(mean_trial_time, r.mean_hrv_for_trials, label='HRV')
        if options.do_gsr:
            plt.plot(mean_trial_time, r.mean_gsr_for_trials, label='GSR')
        plt.legend()
        name = 'mean_with_trials'
        plt.title(name)
        figs.append(fig)
        names.append(name)

    if options.do_blocks:
        """# plot raw data and beats for blocks
        fig = plt.figure(figsize=options.figsize)
        yrange = (min(r.raw_gsr), max(r.raw_gsr)-min(r.raw_gsr))
        plot_bg_colors(r.block_starts, r.block_ends, r.block_conditions, fig, yrange)
        if options.do_ecg:
            plt.plot(r.time_scale, r.raw_ecg)
            beats = r.ecg_signal.beats
            height = np.ones(len(beats))*np.median(r.raw_ecg)
            plt.scatter(beats, height)
        if options.do_gsr:
            plt.plot(r.time_scale, r.raw_gsr)
        name = 'raw_data_with_blocks'
        plt.title(name)
        figs.append(fig)
        names.append(name)"""
    
        # plot filtered data for blocks
        fig = plt.figure(figsize=options.figsize)
        yrange = (0,max(r.gsr_signal.signal))
        plot_bg_colors(r.block_starts/60, r.block_ends/60, r.block_conditions, fig, yrange)
        if options.do_ecg:
            plt.plot(r.ecg_signal.time_scale, r.ecg_signal.signal)
        if options.do_gsr:
            time_scale, gsr_signal = r.gsr_signal.get_signal_with_nans()
            plt.plot(time_scale/60, gsr_signal)
            plt.ylim(yrange)
            plt.xlabel('time in minutes')
        name ='filtered_gsr_with_blocks'
        plt.title('filtered gsr with blocks')
        figs.append(fig)
        names.append(name)

        # plot plot means for blocks
        """fig = plt.figure(figsize=options.figsize)
        yrange = (0, max(r.mean_gsr_for_blocks)-min(r.mean_gsr_for_blocks))
        plot_bg_colors(r.block_starts, r.block_ends, r.block_conditions, fig, yrange)
        mean_block_time = (r.block_starts+r.block_ends)/2
        if options.do_ecg:
            plt.plot(mean_block_time, r.mean_hr_for_blocks, label='HR')
            plt.plot(mean_block_time, r.mean_hrv_for_blocks, label='HRV')
        if options.do_gsr:
            plt.plot(mean_block_time, r.mean_gsr_for_blocks, label='GSR')
        name = 'mean_for_blocks'
        plt.legend()
        plt.title(name)
        figs.append(fig)
        names.append(name)"""
    
    return names, figs


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


def plot_bg_colors(start_times, end_times, conditions, fig=None, yrange=None) :

    if yrange is None:
        yrange = [0,10]
    
    #start_times, end_times, condtitions = \
    #    da.join_trials_to_blocks(start_times, end_times, conditions)

    if fig == None :
        fig = plt.figure()

    ax = fig.add_subplot(111)

    xranges = [(s,(e-s))  for s,e in zip(start_times, end_times)]
    
    def color_choice(cond):

        if cond == 'Easy':
            return 'green'
        if cond == 'Hard':
            return 'red'
        if cond == 'Explain':
            return 'yellow'
        if cond == 'PreBaseline':
            return 'grey'
        if cond == 'PostBaseline' :
            return 'grey'
        if cond == 'Easy-False':
            return 'blue'
        if cond == 'Hard-False':
            return 'purple'

        print('Cannot assign color to condition:', cond)
        return 'black'

    colors = [color_choice(cond) for cond in conditions]
    
    for i in range(len(xranges)) :
        coll = collections.BrokenBarHCollection([xranges[i]], yrange, facecolor=colors[i], alpha=0.5)
        ax.add_collection(coll)

    return fig
 

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
        ax.ar_collection(coll)

    return figure

def save_plot(name, fig):
    directory = os.path.expanduser('~/inlusio_plots')
    if not os.path.exists(directory):
        print('mkdir', directory)
        os.mkdir(directory)
    
    font = {#'family' : 'normal',
        'weight' : 'bold',
        'size'   : 40
    }
    rc('font', **font)
    
    filename = directory + os.sep + name + '.png'
    fig.savefig(filename)


def save_all_plots():
    print('database:', da.PATH_TO_DB)
    print('PHYSIO_PATH', da.PATH_TO_DB)
    import os
    directory = os.path.expanduser('~/inlusio_plots')
    if not os.path.exists(directory):
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

if __name__=='__main__':
    import sys
    args = sys.argv[1:]

    #subjects = [312, 315, 317, 320, 322, 329, 330] 
    # [327, 331, 332, 333,

    if 'save' in args:
        #subjects = [401, 405, 406, 407, 409, 410, 413, 417]
        subjects = range(400,440)
        sessions = [1,2]
        options = {

            'do_gsr' : True,
            'do_blocks' : True,
            'figsize' : (60,30),
            'show' : False,
            'save' : True,
        }
    else:
        subjects = raw_input('Enter Subject IDs: ').split()
        sessions = raw_input('Enter Session IDs: ').split()
        options = {
            'do_gsr' : True,
            'do_blocks' : True,
            'show' : True,
            'save' : False,
        }

    for sub in subjects:
        for ses in sessions:
            sub = str(sub); ses = str(ses)
            print 'Do Subject:', sub, 'Session:', ses
            try:
                plot_subject(sub, ses, options)
            except da.DataAccessError as e:
                print 'Could not plot Subject:', sub, 'Session:', ses, '; ', type(e).__name__, ':', e
            except Exception as e:
                print 'Unexpected Error!!!', sub, 'Session:', ses, '; ', type(e).__name__, ':', e
                print 'Call Moritz: 015774714787'
            print


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
