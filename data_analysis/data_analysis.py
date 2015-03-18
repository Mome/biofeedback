import data_access as da
import data_preprocessing as dpp
from numpy import array
from pylab import *

physio = da.get_physio_data(320,1)

ecg = array(physio['ecg'])
time = array(physio['time'])

beats, hr, hrv = dpp.process_ecg(ecg,time)

print('beats',len(beats))
print('hr',hr)
print('hrv',hrv)

plot(ecg)
scatter(beats,3.5*ones(len(beats)))

show()