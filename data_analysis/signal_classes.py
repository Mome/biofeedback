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
        """ Tries to get rid of nans in array. Just makes an linear interpolation. """

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

    def remove_nans(self):
        where_no_nans = ~np.isnan(self.signal)
        self.signal = self.signal[where_no_nans]
        self.time_scale = self.time_scale[where_no_nans]

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
        self.gaps = None

    def detect_beats(self):
        self.beat_indices = rpeakdetect.detect_beats(self.signal, self.sampling_rate)
        self.beats = self.time_scale[self.beat_indices]

    def remove_invalid_values(self):
        # 5.0 or 4.5 or lower
        super(EcgSignal,self).remove_invalid_values(lower_bound = 0, upper_bound=4.5)

    def _detect_gaps(self, max_factor=1.5) :

        dist = np.diff(self.beats)
        mm = moving_median(dist)
        gaps = []

        for i in range(len(dist)) :
            if dist[i] >= max_factor*mm[i] :
                index1 = self.beats[i]
                index2 = self.beats[i+1]
                order = int(dist[i]/mm[i]+0.5) 
                gaps.append((index1,index2,i,order))
        
        self.gaps = gaps

    def _detect_compressions(self, min_factor=0.5) :

        dist = np.diff(self.beats)
        mm = moving_median(dist)
        compressions = []

        for i in range(len(dist)) :
            if  dist[i] < min_factor*mm[i]:
                index1 = self.beats[i]
                index2 = self.beats[i+1]
                ratio = dist[i]/mm[i]
                compressions.append((index1,index2,dist[i],mm[i],ratio))

        self.compressions = compressions

    def fill_gaps(self, max_order = 3) :

        if self.beats is None :
            raise Exception('No beats calculated, yet !')

        self._detect_gaps()

        new_beats = []

        for gap in self.gaps :
            order = gap[-1]
            if order > max_order :
                continue
            if order <= 1 :
                raise Exception('Something went very wrong: order <= 1')
            last_beat = gap[0]
            first_beat = gap[1]
            filler = list(np.linspace(last_beat,first_beat,order+1))[1:-1]
            new_beats += filler
        
        self.beats = np.concatenate((self.beats,new_beats), axis=0)
        self.beats.sort()        

    def beat_intervalls_by_gaps(self) :
        
        self._detect_gaps()
        gap_indices = [gap[2] for gap in self.gaps]
        starts = [0] + gap_indices
        ends = [i+1 for i in gap_indices] + [len(self.beats)-1]

        intervalls = [self.beats[s:e] for s,e in zip(starts,ends) ]

        self.beat_intervalls = intervalls

    def remove_small_intervalls(self, min_size=7) :
        tmp = [bi for bi in self.beat_intervalls if len(bi)>min_size]
        self.beat_intervalls = tmp

    def mean_value_for_blocks(self, blocks, measure, silent=True) :

        if measure.lower() == 'hr' :
            measure = EcgSignal.heart_rate_for_intervall
        elif measure.lower() == 'hrv' :
            measure = EcgSignal.hrv_rate_for_intervall

        heart_rates = []

        for block in blocks :
            # look for beginning intervall
            start = block[0]
            end = block[1]
            containing_intervalls = [ bi[(bi>=start)*(bi<=end)] for bi in self.beat_intervalls ]
            containing_intervalls = [ ci for ci in containing_intervalls if len(ci)>2 ]
            #return containing_intervalls
            mean_rates = [ measure(ci) for ci in containing_intervalls]
            intervall_lens = [len(ci) for ci in containing_intervalls ]

            if len(mean_rates) == 0 :
                if not silent : print 'No mean rates could be calculated!'
                heart_rates.append(-1)
                continue

            combined_hr = sum([l*hr for l,hr in zip(mean_rates,intervall_lens)]) / sum(intervall_lens)

            heart_rates.append(combined_hr)

        return heart_rates

    @staticmethod
    def hrv_rate_for_intervall(beats):

        if any(np.isnan(beats)) :
            print 'beats, Naaaaaans!'

        hr = 1.0 / np.diff(beats)

        if any(np.isnan(hr)) :
            print 'hr, Naaaaaans!'

        hrv = np.abs(np.diff(hr))

        if any(np.isnan(hrv)) :
            print 'hrv, Naaaaaans!'

        if len(hrv) == 0 :
            print 'hrv==0'
            return -1

        return np.mean(hrv)

    @staticmethod
    def heart_rate_for_intervall(beats):
        # beats per time scale
        time_range = beats[-1] - beats[0]

        # add some smoothing
        time_range += np.mean(np.diff(beats))

        HR = len(beats)/time_range

        return HR

    """ probabliy not really needed any more """
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

    def mean_gsr_for_blocks(self, blocks) :

        mean_gsr = []

        for block in blocks :
            start = block[0]
            end = block[1]
            ts = self.time_scale
            intervall = self.signal[(ts>=start)*(ts<=end)]
            if len(intervall) > 0 :
                mean_gsr.append(np.mean(intervall))
            else :
                mean_gsr.append(-1)

        return mean_gsr
    
