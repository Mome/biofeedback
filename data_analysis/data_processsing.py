from pylab import *
from numpy import gradient
import rpeakdetect as peak
import time

def load_data(path):
    with open(path) as csv_file:
        data = csv_file.readlines()
    # test if first row float
    data = [line.strip().split(',') for line in data if line.strip()!='']
    data = array(data).T
    out= []
    for i,line in enumerate(data) :
        try:
            line = array(line,dtype='float32')
        except :
            print 'not convertable', path, i
        out.append(line)
    return out

def convert_time_array(time_array):
    for s in time_array :
        s, rest = s.split('.')
        subseconds, rest = rest.split('+')
        date = time.strptime(s, '%Y-%m-%dT%H:%M:%S')
        timestamp = calendar.timegm(date.timetuple())
        timestamp += float('0.'+subseconds)

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

def align_times(start_times, relative_times):
    start_times = array(start_times, dtype='float32')
    relative_times = array(relative_times)
    index = argmin(start_times)
    start_times-=start_times[index]
    for i,_ in enumerate(relative_times):
        relative_times[i]+=start_times[i]
    return relative_times
    

def process_data(path = '../data/011_000.csv'):
    print pi
    s = 1000
    e = -1000
    data = load_data(path)
    data = data[2]
    data_filtered = low_pass(data,'cos',1000)
    grad = gradient(data_filtered)
    grad_filtered = low_pass(grad, 'cos', 10000)
    plot(data[s:e])
    figure()
    plot(data_filtered[s:e])
    figure()
    plot(grad[s:e])
    half = int(len(data)/2)
    s1 = sum(data[s:half])
    s2 = sum(data[half:e])
    print 'first',s1, ' second',s2
    print 'ratio', s1/s2

if __name__ == '__main__' :
    gsr = False
    ecg = False
    time_ = False
    munis_data = True 
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
        
        conditions = parameters[8]
        success = parameters[9]
        status = trail_stessors[3]
        
        print len(parameters[0]), len(te_angles[0]), len(trail_stessors[0])

        
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
 

