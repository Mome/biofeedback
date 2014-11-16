import calendar
import time
from copy import copy


from pylab import *
from numpy import gradient
import yaml

import rpeakdetect as peak

def load_data(path):
    with open(path) as csv_file:
        data = csv_file.readlines()
    # test if first row float
    data = [line.strip().split(',') for line in data if line.strip()!='']
    data = array(data).T
    out= []
    for i,line in enumerate(data) :
        try:
            line = array(line,dtype='float64')
        except :
            print 'not convertable', path, i
        out.append(line)
    return out


def convert_time_array(time_array):
    out = zeros(len(time_array),dtype='float64')
    for i,s in enumerate(time_array) :
        s, rest = s.split('.')
        subseconds, rest = rest.split('+')
        date = time.strptime(s, '%Y-%m-%dT%H:%M:%S')
        out[i] = float(calendar.timegm(date)) + float('0.'+subseconds)
    #print 'time_array 1', out[0:12]
    #print 'commatest',out[0] - int(out[0])
    return out


def align_times(start_times, relative_times):
    start_times = array(start_times, dtype='float64')
    relative_times = copy(relative_times)
    index = argmin(start_times)
    start_times-=start_times[index]
    for i,_ in enumerate(relative_times):
        relative_times[i]+=start_times[i]
    return relative_times


def low_pass(signal, kernel_type, kernel_size):
    if kernel_type == 'rect':
        kernel = 1.0/kernel_size * ones(kernel_size)
    elif kernel_type == 'cos':
	N = kernel_size
        kernel = 0.5*(1-cos(2*pi*arange(N)/(N-1)))
    else :
        raise Exception('No such kernel: ' + kernel_type) 
    return convolve(signal, kernel, mode='same')


def median_filter(signal):
    z = zeros(len(signal)-2)
    for i in xrange(1,len(z)-1):
        m = median([signal[i-1],signal[i],signal[i+1]])
        z[i-1] = m
    return z

def process_data(data_path='../data/trail_data/'):

    if not data_path.endswith('/'):
        data_path += '/'

    subject_id = '103'
    record_number = '000'

    record_file_name = str(subject_id) + '_' + str(record_number) + '.csv'

    # get physio starting time from yaml file
    with open(data_path + 'metadata/subject_' + str(subject_id) + '.yml') as yaml_file :
        meta = yaml.load(yaml_file.read())
    physio_times_start = -1
    for record in meta['records']:
        if record['file_name'] == record_file_name :
            physio_times_start = float(record['start_time'])
    if physio_times_start == -1 :
        raise Exception(record_file_name + 'not found!')

    #ECG & GSR
    path = data_path + 'records/' + record_file_name
    data = load_data(path)

    # get physiotimes and convert to seconds
    physio_times = array(data[0], dtype='float64')/1000.0

    # occulus data
    path = data_path + str(subject_id) + '/Parameters.csv'
    parameters = load_data(path)
    path = data_path + str(subject_id) + '/Trial-Error-Angles.csv'
    te_angles = load_data(path)
    path = data_path + str(subject_id) + '/Trial-Stressors.csv'
    trail_stessors = load_data(path)

    # convert dates to seconds
    p_times = convert_time_array(parameters[0])
    tea_times = convert_time_array(te_angles[0])
    ts_times = convert_time_array(trail_stessors[0])

    # get start times
    p_times_start = p_times[0]
    tea_times_start = tea_times[0]
    ts_times_start = ts_times[0]

    # convert start times to utc
    one_hour_in_seconds = 60*60
    p_times_start -= one_hour_in_seconds
    tea_times_start -= one_hour_in_seconds
    ts_times_start -= one_hour_in_seconds

    # absolute time to relative time representation
    p_times -= p_times[0]
    tea_times -= tea_times[0]
    ts_times -= ts_times[0]

    # align timescales
    physio_times,p_times,tea_times,ts_times =\
    align_times((physio_times_start,p_times_start,tea_times_start,ts_times_start),\
        [physio_times,p_times,tea_times,ts_times])

    # time data tuples
    ecg_data = (physio_times,data[1])
    gsr_data = (physio_times,data[2])
    conditions = (p_times,parameters[8])
    success = (p_times,parameters[9])
    status = (ts_times,trail_stessors[3])

    print physio_times_start, p_times_start, tea_times_start, ts_times_start
    raw_input()
    figure()
    plot(ecg_data[0],ecg_data[1])
    #figure()
    plot(gsr_data[0],gsr_data[1])
    #figure()
    step(conditions[0],conditions[1])
    #figure()
    step(success[0],success[1])
    #figure()
    step(status[0],status[1])
    show()




if __name__ == '__main__' :
    gsr = False
    ecg = False
    time_ = False
    munis_data = False 
    process = True

    if process :
        process_data()

    #data = load_data('../data/trail_data/102/Parameters.csv')
    path = '../data/trail_data/records/102_000.csv'
    data = load_data(path)
    if munis_data :
        path = '../data/trail_data/103/Parameters.csv'
        parameters = load_data(path)
        path = '../data/trail_data/102/Trial-Error-Angles.csv'
        te_angles = load_data(path)
        path = '../data/trail_data/102/Trial-Stressors.csv'
        trail_stessors = load_data(path)

        p_times = convert_time_array(parameters[0])
        tea_times = convert_time_array(te_angles[0])
        ts_times = convert_time_array(trail_stessors[0])

        p_times_start = p_times[0]
        tea_times_start = tea_times[0]
        ts_times_start = ts_times[0]

        p_times = append([0],gradient(p_times))
        tea_times = append([0],gradient(tea_times))
        ts_times = append([0],gradient(ts_times))
        
        conditions = (p_times,parameters[8])
        success = (p_times,parameters[9])
        status = (ts_times,trail_stessors[3])
        
    if time_ :
        time_data = data[0]
        plot(gradient(time_data[10000:10100]))
        print mean(gradient(time_data[1000:-1000]))
    if gsr :
        s = 1000
        e = -1000
        gsr_data = data[2]
        data_filtered = low_pass(gsr_data,'cos',1000)
        grad = gradient(data_filtered)
        grad_filtered = low_pass(grad, 'cos', 10000)
        plot(gsr_data[s:e])
        figure()
        plot(data_filtered[s:e])
        figure()
        plot(grad[s:e])
        half = int(len(grad)/2)
        s1 = sum(grad[s:half])
        s2 = sum(grad[half:e])
        print 'first',s1, ' second',s2
        print 'ratio', s1/s2
    if ecg :
        ecg_data = data[1]
        ecg_data = ecg_data[500:-1]
        rate = 73.80128266629275 
        beats = peak.detect_beats(ecg_data,rate)
        #ecg_data = low_pass(ecg_data, 'cos', 5)
        #plot(ecg_data)
        #scatter(beats,3.8*ones(len(beats)))
        #show()
        peak_distance = gradient(beats)
        plot(low_pass(peak_distance,'cos',100)) ; show()
        print 'heard rate:', mean(peak_distance) 
        print 'heard rate first half:', mean(peak_distance[0:int(len(peak_distance)/2)])
        print 'heard rate second half:', mean(peak_distance[int(len(peak_distance)/2):-1])
 

    #distances = lambda a : array([0]+[a[i+1]-a[i] for i in xrange(len(a)-1)])
