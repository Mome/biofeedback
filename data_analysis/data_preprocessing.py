# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 13:48:34 2015

@author: Lukas
"""
from pylab import *

from data_access import *
from rpeakdetect import detect_beats
import scipy.ndimage


def process_ecg(ecg_signal, time_scale) :
    # detect spikes
    sampling_rate = 1/mean(diff(time_scale))
    print('sampleing rate:', sampling_rate)
    beats = detect_beats(ecg_signal, sampling_rate)
    plot(ecg_signal)
    print(beats)
    heart_rate = 1/mean(diff(beats))
    # fill unrecognized zones
    # calculate heart rate
    rate = None
    # calculate HRV
    hrv = None
    return beats, heart_rate, hrv

"""
gsr_signal := list of gsr values? Moritz? --> die get_physio_data gibt dir den dataframe, den du brauchst
"""
def filter_gsr(gsr_signal):

    # resample signal with cubic interpolation --> glättet Graph ein wenig
    gsr_signal = scipy.ndimage.zoom(gsr_signal, 2, order=3)
    # filter signal somehow?? e.g. http://neuroelf.net/wiki/doku.php?id=gsr_data_analysis
    

# my low pass function replace with something propper
def low_pass(signal, kernel_type, kernel_size):
    N = kernel_size

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
    factor = sum(signal)/sum(out)
    
    return out*factor


def change_block_times_format(df):
    list = []
    for index, row in df.iterrows():
        tupel = (row['StartTimeTrial'],row['EndTimeTrial'], row['Type'])
        list.append(tupel)
    return list
