from __future__ import division

import data_access as da
from matplotlib.pyplot import *
from datetime import datetime
import numpy as np

subject = raw_input('Enter Subject id: ')
session = raw_input('Enter Session id: ')

physio_data = da.get_physio_data(subject, session)

time = np.array(physio_data['time'])
start_time = time[0]
end_time = time[-1]
start_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
end_time = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
print 'start_time:', start_time
print 'end_time:', end_time
time = time - time[0]
time = time/60.0

if 'ecg' in physio_data:
	figure()
	plot(time, physio_data['ecg'])
	xlabel('time in minutes')
	title('ECG of Subject: '+subject+' Sesison: ' + session)
if 'gsr' in physio_data:
	figure()
	plot(time, physio_data['gsr'])
	xlabel('time in minutes')
	title('GSR of Subject: '+subject+' Sesison: ' + session)

show()