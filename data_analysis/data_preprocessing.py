import datetime
import time

import pandas as pd
import pylab as pl
import scipy.ndimage
from scipy.signal import butter, lfilter, freqz

import data_access as da
from rpeakdetect import detect_beats


def process_gsr(gsr_signal, time_scale):

    assert type(gsr_signal) == type(time_scale) == type(pl.array([]))

    indies = pl.where(gsr_signal==-1)
    gsr_signal = pl.delete(gsr_signal,indies)
    time_scale = pl.delete(time_scale,indies)

    # split in segments where nans occur
    nans_bool = pl.isnan(gsr_signal)
    nan_indies = [0] + list(pl.where(nans_bool)[0]) + [-1]
    print(nan_indies)
    for i in range(len(nan_indies)-1) :
        block = gsr_signal[nan_indies[i]+1:nan_indies[i+1]]
        filtered = moving_median(block)
        if len(filtered) == 0:
            continue
        filtered = low_pass(filtered,'cos',30)
        gsr_signal[nan_indies[i]+1:nan_indies[i+1]] = filtered

    #gsr_signal = interpolate_nans(gsr_signal)
    #gsr_signal = low_pass(gsr_signal, 'cos', 10000)

    #sampling_rate = 1/pl.mean(pl.diff(time_scale))
    #signal = butter_lowpass_filter(gsr_signal, cutoff=5.0, fs=sampling_rate)

    return gsr_signal, time_scale


def process_ecg(ecg_signal, time_scale) :

    # remove nans
    ecg_signal = interpolate_nans(ecg_signal)

    # remove fucked up data

    # detect spikes
    sampling_rate = 1/pl.mean(pl.diff(time_scale))
    beats = detect_beats(ecg_signal, sampling_rate)

    # fill unrecognized zones
    beats, holes = interpolate_unrecognized_beats(beats)

    # remove 

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
        if pl.isnan(signal[i]) :
            signal[i] = (signal[i-1] + signal[i+1])/2

    return signal


def interpolate_unrecognized_beats(beats, max_beat_gaps = 3):
    """adds beats to a beat train"""

    new_beats = []
    dist = pl.diff(beats)
    mm = moving_median(dist)

    for gap_size in range(2,max_beat_gaps+1) :
        for i in range(len(dist)) :
            if (gap_size-0.5)*mm[i] < dist[i] < (gap_size+0.5)*mm[i] :
                # add additional beat
                index1 = beats[i]
                index2 = beats[i+1]
                new_beats += [int(n) for n in pl.linspace(index1,index2,gap_size-1)]

    beats = pl.concatenate((beats,new_beats),axis=0)
    beats.sort()

    dist = pl.diff(beats)
    holes = []
    mm = moving_median(dist)
    for i in range(len(dist)) :
        if 1.5*mm[i] < dist[i] :
            index1 = beats[i]
            index2 = beats[i+1]
            holes.append((index1,index2,dist[i],mm[i]))

    return beats, holes


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
            bound_2 = (extract_block_times_form_game_dataN-1)*(1-alpha/2)
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


def extract_trail_times(df):

    times = df['Zeitpunkt']
    status = df['Status']
    #types = df['BlockType']
    types = df['Type']
    trial_id = df['Trial_id']

    times = pd.to_datetime(times)
    times = ( times - datetime.timedelta(hours=1) - datetime.datetime(1970,1,1) ) / pl.timedelta64(1,'s')

    times = pl.array(times)
    status = pl.array(status)
    types = pl.array(types)
    trial_id = pl.array(trial_id)

    starts = (status == 'StartTimeTrial')
    ends = (status == 'EndTimeTrial')

    # remove BLOCKOVER types
    blockover = (types != 'BLOCKOVER')
    starts *= blockover
    ends *= blockover

    # ...
    start_ids = trial_id[starts]
    end_ids = trial_id[ends]

    start_types = types[starts]
    end_types = types[ends]

    start_times = times[starts]
    end_times = times[ends]

    #print(start_ids.head)
    #print(end_ids.head)

    # check for double trail_ids
    d = pl.sort(start_ids, axis=None)
    if any(d[d[1:] == d[:-1]]) :
        raise Exception('double start trail ids')
    d = pl.sort(end_ids, axis=None)
    if any(d[d[1:] == d[:-1]]) :
        raise Exception('double end trail ids')

    blocks = []
    for si in range(len(start_ids)) :
        sid = start_ids[si]
        match = pl.where(sid==end_ids)[0]

        if len(match) == 0 :
            continue

        ei = match[0]

        if start_types[si] != end_types[ei] :
            raise Exception('Unequal types for start and endtrail ' + str(sid))
        elif len(match) > 1 :
            raise Exception('more than one match')

        start_time = start_times[si]
        end_time = end_times[ei]
        trial_type = start_types[si]

        if pl.isnan(start_time) or pl.isnan(end_time) :
            continue

        blocks.append((start_time,end_time,trial_type))

    if blocks == [] :
        return [],[],[]

    start_times, end_times, start_types = zip(*blocks)

    start_times = pl.array(start_times)
    end_times = pl.array(end_times)
    start_types = pl.array(start_types)

    return start_times, end_times, start_types


# joins trails to blocks
def join_trails_to_blocks(start_times, end_times, start_types):

    # determine change of type
    change_of_types = [start_types[i]!=start_types[i+1] for i in range(len(start_types)-1)]
    
    start_times_index = pl.array([True] + change_of_types)
    end_times_index = pl.array(change_of_types + [True])

    start_times = start_times[start_times_index]
    end_times = end_times[end_times_index]
    start_types = start_types[start_times_index]

    return start_times, end_times, start_types


def assign_data_to_blocks(start_times, end_times, time_scale, *data) :
    assert len(start_times) == len(end_times)
    #assert len(time_scale) == len(ecg) == len(gsr)
    assert list(time_scale) == sorted(time_scale)

    block_number = len(start_times)
    data_number = len(data)

    # initializes a list to hold for each datavector a list of data correstponding to a block
    data_blocks = [[None]*block_number]*data_number

    # go through all data_vectors and cut out block data
    for i in range(block_number) :
        time_range = start_times[i] < time_scale < end_times[i]
        for j, data_vec in enumerate(data) :
            data_blocks[i][j] = data_vec[time_range]

    return data_blocks


def change_block_times_format(df):
    list = []
    for index, row in df.iterrows():
        tupel = (row['StartTimeTrial'],row['EndTimeTrial'], row['Type'])
        list.append(tupel)
    return list


def blocks_to_str(blocks, name, physio_start=None, convert=True):
    out = '#-----------------' + name + '----------------------#\n'
    if physio_start != None :
        out += 'Physio start: ' + time.asctime( time.gmtime(physio_start) ) + '\n'
    l = len(out)-3
    for s,e,c in blocks :
        if convert and is_float(s) :
            s = time.asctime( time.gmtime(s) )
        if convert and is_float(e) :
            e = time.asctime( time.gmtime(e) )
        out += str(s) + ' | ' + e + ' | ' + c + '\n'
    out += '#' + '-'*l + '#\n'
    return out



def test_block_times(subject, session):
    print('test blocktimes', subject, session)
    print()
    gd = da.get_game_data(subject, session)
    my_blocks= extract_block_times_form_game_data(gd)
    print_blocks(my_blocks,'my_blocks')

    print()
    lukas_blocks = da.get_block_times(subject, session)
    lukas_blocks = change_block_times_format(lukas_blocks)
    print_blocks(lukas_blocks,'lukas_blocks')

    print()
    raw_blocks = da.raw_block_times(subject, session)
    raw_blocks = change_block_times_format(raw_blocks)
    print_blocks(raw_blocks,'raw_blocks')


def is_float(num):
    try:
        float(num)
    except :
        return False
    return True

if __name__ == '__main__':
    print(da.PATH_TO_DB)
    import sys
    args = sys.argv
    subject = args[1]
    session = args[2]
    test_block_times(subject,session)
