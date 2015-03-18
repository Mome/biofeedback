# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 13:48:34 2015

@author: Lukas
"""
import datetime
import time

import pandas as pd
import pylab as pl
import scipy.ndimage
from scipy.signal import butter, lfilter, freqz

import data_access as da
from rpeakdetect import detect_beats


def process_gsr(gsr_signal, time_scale):

    gsr_signal = interpolate_nans(gsr_signal)
    gsr_signal = low_pass(gsr_signal, 'cos', 10000)

    #sampling_rate = 1/pl.mean(pl.diff(time_scale))
    #signal = butter_lowpass_filter(gsr_signal, cutoff=5.0, fs=sampling_rate)

    return gsr_signal


def process_ecg(ecg_signal, time_scale) :
    # remove nans
    ecg_signal = interpolate_nans(ecg_signal)

    # detect spikes
    sampling_rate = 1/pl.mean(pl.diff(time_scale))
    beats = detect_beats(ecg_signal, sampling_rate)

    # fill unrecognized zones
    beats = interpolate_unrecognized_beats(beats)

    # calculate heart rate
    heart_rate = 1/pl.mean(pl.diff(beats))

    # calculate HRV
    hrv = None
    return beats, heart_rate, hrv


def interpolate_nans(signal):
    """Trys to get rid of nans in array. Just makes an linear interpolation."""
    # check for more than one nan in row
    for i in range(len(signal)-1) :
        if pl.isnan(signal[i]) and pl.isnan(signal[i+1]) :
            raise Exception('There are two nans in a row ask moritz what to do !')

    if pl.isnan(signal[0]) :
        signal[0] = signal[1]
    if pl.isnan(signal[-1]) :
        signal[-1] = signal[-2]

    for i in range(1,len(signal)-1) :
        if pl.isnan(signal[i]):
            signal[i] = (signal[i-1] + signal[i+1])/2

    return signal


def interpolate_unrecognized_beats(beats):
    """adds """
    new_beats = []
    dist = pl.diff(beats)
    mm = moving_median(dist)

    for i in range(len(dist)) :
        if 1.5*mm[i] < dist[i] < 2.5*mm[i]  :
            # add additional beat
            index1 = beats[i]
            index2 = beats[i+1]
            # insert new beat at half of interfall
            new_beat = (index1+index2) / 2
            new_beats.append(new_beat)
            #print('found single hole at:', new_beat)
    dist = pl.diff(beats)
    mm = moving_median(dist)
    for i in range(len(dist)) :
        if 2.5*mm[i] < dist[i] < 3.5*mm[i]  :
            # add additional beat
            index1 = beats[i]
            index2 = beats[i+1]
            # insert new beat at half of interfall
            new_beat1 = (2*index1+index2) / 3
            new_beat2 = (index1+2*index2) / 3
            new_beats.append(new_beat1)
            new_beats.append(new_beat2)
            #print('found double hole at:', new_beat1,new_beat2)

    beats = pl.concatenate((beats,new_beats),axis=0)
    beats.sort()

    dist = pl.diff(beats)
    holes = []
    mm = moving_median(dist)
    for i in range(len(dist)) :
        if 1.5*mm[i] < dist[i] :
            index1 = beats[i]
            index2 = beats[i+1]
            holes.append((index1,index2,dist[i]))

    if holes != [] :
        print('found more holes at:')
        for h in holes :
            print(h)

    return beats


def moving_median(signal,size=5):

    out = pl.zeros(len(signal))
    for i in range(len(signal)) :
        if i < size :
            l = 0
        else :
            l = i-size
        if i+size >= len(signal) :
            r = len(signal)-1
        else :
            r  = i+size
        med = pl.median(signal[l:r])
        out[i] = med
    return out

    
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y


def low_pass(signal, kernel_type, kernel_size):
    N = kernel_size
    cos = pl.cos
    pi = pl.pi
    arange = pl.arange
    convolve = pl.convolve
    nansum = pl.nansum


    # filter nans
    #nans_index = (signal!=signal)
    #signal[nans_index]

    if kernel_type == 'rect':
        kernel = 1.0/N * ones(N)

    elif kernel_type == 'cos':
        N = kernel_size
        kernel = 0.5*(1-cos(2*pi*arange(N)/(N-1)))

    elif kernel_type == 'turkey':

        def turkey(n,N,alpha) :
            bound_1 = alpha*(N-1)/2
            bound_2 = (N-1)*(1-alpha/2)
            if 0 <= n < bound_1 :
                return (1/2)*(1+cos(pi*(2*n/(alpha*(N-1))-1)))
            elif bound_1 <= n <= bound_2 :
                return 1.0
            elif bound_2 < n <= N-1 :
                return (1/2)*(1+cos(pi*(2*n/(alpha*(N-1))-alpha/2+1)))
            else :
                return 0

        turkey = vectorize(turkey)
        #kernel = turkey()
    else :
        raise Exception('No such kernel: ' + kernel_type) 
    out = convolve(signal, kernel, mode='same')
    factor = nansum(signal)/nansum(out)
    
    return out*factor


def extract_block_times_form_game_data(df):

    print('shape', df.shape)

    times = df['Zeitpunkt']
    types = df['BlockType']
    status = df['Status']

    times = pd.to_datetime(times)
    times = ( times - datetime.timedelta(hours=1) - datetime.datetime(1970,1,1) ) / pl.timedelta64(1,'s')

    starts = (status == 'StartTimeTrial')
    ends = (status == 'EndTimeTrial')

    print('starts')
    print(starts)
    print()

    print('ends')
    print(ends)
    print()

    blockover = (types != 'BLOCKOVER')
    starts *= blockover
    ends *= blockover

    print('len(starts)', sum(starts))
    print('len(ends)', sum(ends))

    start_times = pl.array(times[starts])
    end_times = pl.array(times[ends])

    start_types = pl.array(types[starts])

    #for i in range(len(start_times)):
    #    print(start_times[i], ' | ' ,end_times[i], ' | ', start_types[i])

    # determine change of type
    change_of_types = [start_types[i]!=start_types[i+1] for i in range(len(start_types)-1)]
    
    start_times_index = pl.array([True] + change_of_types)
    end_times_index = pl.array(change_of_types + [True])

    start_times = start_times[start_times_index]
    end_times = end_times[end_times_index]
    start_types = start_types[start_times_index]

    #print('#-------------------------------#')
    #for s,e,c in zip(start_times,end_times,start_types) :
    #    print(s,' | ',e,' | ',c)

    return zip(start_times, end_times, start_types)


def change_block_times_format(df):
    list = []
    for index, row in df.iterrows():
        tupel = (row['StartTimeTrial'],row['EndTimeTrial'], row['Type'])
        list.append(tupel)
    return list


def print_blocks(blocks, convert=True):
    print('#-------------------------------#')
    for s,e,c in blocks :
        if convert and is_float(s) :
            s = time.asctime( time.gmtime(s) )
        if convert and is_float(e) :
            e = time.asctime( time.gmtime(e) )
        print(s,' | ',e,' | ',c)
    print('#-------------------------------#')


def test_block_times(subject, session):
    print('test blocktimes', subject, session)

    gd = da.get_game_data(subject, session)
    my_blocks= extract_block_times_form_game_data(gd)
    print_blocks(my_blocks)

    print()

    lukas_blocks = da.get_block_times(subject, session)
    lukas_blocks = change_block_times_format(lukas_blocks)
    print_blocks(lukas_blocks)

    print()
    
    raw_blocks = da.raw_block_times(subject, session)
    raw_blocks = change_block_times_format(raw_blocks)
    print_blocks(raw_blocks)


def is_float(num):
    try:
        float(num)
    except :
        return False
    return True

if __name__ == '__main__':
    import sys
    args = sys.argv
    subject = args[1]
    session = args[2]
    test_block_times(subject,session)

