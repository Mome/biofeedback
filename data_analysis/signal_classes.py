from __future__ import division

import numpy as np

import rpeakdetect

from data_preprocessing import moving_median


class Signal(object) :

    def __init__(self, time_scale, signal):

        # copy imput arrays
        self.time_scale = np.array(time_scale)
        self.signal = np.array(signal)

        self.sampling_rate = 1 / np.median(np.diff(time_scale))

    def remove_invalid_values(self, lower_bound=float('-inf'), upper_bound=float('inf')) :
        valid_indices = (lower_bound < self.signal) * (self.signal < upper_bound)
        self.time_scale = self.time_scale[valid_indices]
        self.signal = self.signal[valid_indices]

    def interpolate_nans(self):
        """Trys to get rid of nans in array. Just makes an linear interpolation."""

        signal = self.signal

        # check for more than one nan in row
        for i in range(len(signal)-1) :
            if np.isnan(signal[i]) and np.isnan(signal[i+1]) :
                raise Exception('There are two nans in a row ask moritz what to do !')

        if np.isnan(signal[0]) :
            np.signal[0] = signal[1]
        if np.isnan(signal[-1]) :
            signal[-1] = signal[-2]

        for i in range(1,len(signal)-1) :
            if np.isnan(signal[i]):
                signal[i] = (signal[i-1] + signal[i+1])/2

    def filter_median(self,size=5):
        signal = self.signal
        out = np.zeros(len(signal))
        for i in range(len(signal)) :
            if i < size :
                l = 0
            else :
                l = i-size
            if i+size >= len(signal) :
                r = len(signal)-1
            else :
                r  = i+size
            med = np.median(signal[l:r])
            out[i] = med
        self.signal = out


class EcgSignal(Signal):

    def __init__(self, time_scale, signal):
        super(EcgSignal, self).__init__(time_scale, signal)
        self.beats = None
        self.holes = None

    def detect_beats(self):
        self.beat_indices = rpeakdetect.detect_beats(self.signal, self.sampling_rate)
        self.beats = self.time_scale[self.beat_indices]

    def remove_invalid_values(self):
        # 5.0 or 4.5 or lower
        super(EcgSignal,self).remove_invalid_values(lower_bound = 0, upper_bound=4.5)

    def interpolate_unrecognized_beats(self, max_beat_gaps = 3):
        """adds beats to a beat train"""

        if self.beats == None :
            raise Exception('No beats calculated, yet !')

        beats = self.beats

        new_beats = []
        dist = np.diff(beats)
        mm = moving_median(dist)

        for gap_size in range(2,max_beat_gaps+1) :
            for i in range(len(dist)) :
                if (gap_size-0.5)*mm[i] < dist[i] < (gap_size+0.5)*mm[i] :
                    print('gap',gap_size, 'at', i)
                    # add additional beat
                    index1 = beats[i]
                    index2 = beats[i+1] 
                    temp = list(np.linspace(index1,index2,gap_size+1))[1:-1]
                    new_beats += temp
                    print('left_index:', index1, 'right_index:', index2, 'new_beat', temp)

        beats = np.concatenate((beats,new_beats), axis=0)
        beats.sort()

        dist = np.diff(beats)
        holes = []
        mm = moving_median(dist)
        for i in range(len(dist)) :
            if 1.5*mm[i] < dist[i] :
                index1 = beats[i]
                index2 = beats[i+1]
                holes.append((index1,index2,dist[i],mm[i]))

        self.beats = beats
        self.holes = holes

    def remove_holes(self, smoothing_factor=0.75):
        if self.beats == None :
            raise Exception('No beats calculated, yet !')
        if self.holes == None :
            raise Exception('No holes calculated, yet !')

        joint_bool_indices = ones(len(time_scale)) == 1

        for hole in self.holes :
            # add some time to last and fist beat around hole
            start = hole[0] + hole[2]*smoothing_factor
            end = hole[1] - hole[2]*smoothing_factor

            hole_bool_indices = (time_scale < start) * (time_scale > end)
            joint_bool_indices *= hole_bool_indices

        # actually remove holes from timescale and signal
        self.time_scale = self.time_scale[joint_bool_indices]
        self.signal = self.signal[joint_bool_indices]


class GsrSignal(Signal) :

    def remove_invalid_values(self):
        super(GsrSignal,self).remove_invalid_values(lower_bound=-1)
    