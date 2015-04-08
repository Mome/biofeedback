from __future__ import division

from sys import argv

from pylab import *

import data_access as da
import signal_classes as signal

subject = argv[1]
session = argv[2]

game_data = da.get_game_data2(subject, session)

physio_data = da.get_physio_data(subject, session)
time_scale = array(physio_data['time'])

# convert time scales to minues
time_scale /= 60
mts = min(time_scale)
time_scale = time_scale-mts

ecg_signal = signal.EcgSignal( time_scale, physio_data['ecg'] )
ecg_signal.interpolate_nans()
ecg_signal.detect_beats()
#ecg_signal.interpolate_unrecognized_beats()
#ecg_signal.remove_holes()

gsr_signal = signal.GsrSignal( time_scale, physio_data['gsr'] )
gsr_signal.interpolate_nans()
gsr_signal.remove_invalid_values()

plot(ecg_signal.time_scale, ecg_signal.signal)
scatter(ecg_signal.beats, 2.5*ones(len(ecg_signal.beats)))
plot(gsr_signal.time_scale, gsr_signal.signal)
show()

"""
if len(physio_time) == 0 :
    raise Exception('not physio data')

physio_start = physio_time[0]

# using my block times extraction
trails = dpp.extract_trail_times(game_data)
if len(trails[0]) == 0 :
    raise Exception('no trails extracted')   
blocks = dpp.join_trails_to_blocks(*trails)
blocks = zip(*blocks) """