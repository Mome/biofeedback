from __future__ import division
import calendar
import os
import sys
import time

sys.path.append('../experiment_computer')

from pylab import *
from numpy import gradient
import yaml

import configurations as conf


#import rpeakdetect as peak

distances = lambda a : array([0]+[a[i+1]-a[i] for i in xrange(len(a)-1)])


def load_data(path):
    with open(path) as csv_file:
        data = csv_file.readlines()
    data = [ line.strip().split(',') for line in data if line.strip()!='']

    return data


def prepare_munis_data(data) :

    # check for equal depth
    depth = len(data[0])
    for row in data :
        if len(row)!=depth :
            raise Exception('Rows must have equal lenght!')

    # transpose
    data = zip(*data)

    # converte float lists to arrays
    data = [array(coloumn, dtype='float64') if is_float(coloumn[0]) else array(coloumn) \
            for coloumn in data]

    return data


def load_physio_data(path):

    data = load_data(path)

    # replace empty string with -1
    for i in xrange(len(data)) : 
        for j in xrange(len(data[i])) :
            if data[i][j] == '' :
                data[i][j] = '-1'

    # remove rows with less than 3 coloumns
    data = [row for row in data if len(row)==3]

    # convert to integrers
    data = array(data, dtype='float64')

    # transpose data
    data = data.T

    return data


def convert_time_array(time_array):
    out = zeros(len(time_array),dtype='float64')
    for i,s in enumerate(time_array) :
        s, subseconds = s.split('.')
        subseconds = subseconds[:-1]
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


def median_filter(signal):
    z = zeros(len(signal)-2)
    for i in xrange(1,len(z)-1):
        m = median([signal[i-1],signal[i],signal[i+1]])
        z[i-1] = m
    return z

def baseline_adaption(signal, filter_size):
    baseline = low_pass(signal, 'cos', filter_size)
    return 

def process_ecg(signal):
    pulse = None
    return pulse


def divide_into_epoches(criterium_tup, data_tup):
    #criterium_indices = where(criterium_data[1] == criterium)[0]
    #criterium_times = array(criterium_indices, criterium_data[0])

    criterium_times = criterium_tup[0]
    criterium = criterium_tup[1]
    data_times = data_tup[0][data_tup[0] > criterium_times[0]]
    data = data_tup[1]
    print data_times
    print data_tup[0]
    print data_tup[1]

    epoch_dict = {}
    d_index = 0
    for ct_index in xrange(len(criterium_times)-1):
        tmp_times = []
        tmp_data = []
        while criterium_times[ct_index+1] >= data_times[d_index] :
            tmp_times.append(data_times[d_index])
            tmp_data.append(data[d_index])
            d_index+=1
            if d_index == len(data_times):
                break
        c = criterium[ct_index]
        if c not in epoch_dict.keys() :
            epoch_dict[c] = []
        epoch_dict[c].append((tmp_times,tmp_data))
        # what for criterium_times[ct_index] == data_times[d_index] ???

    return epoch_dict


def plot_with_background_color(x_axis_divisions,colors, graph_data):
    import matplotlib.pyplot as plt
    import matplotlib.collections as collections

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Plot your own data here
    ax.plot(graph_data[0], graph_data[1])

    xad = list(copy(x_axis_divisions))
    #xad.append(graph_data[0][-1])
    xranges = [(xad[i],xad[i+1]-xad[i]) for i in xrange(len(xad)-1)]
    yrange = (0, 15)
    def color_choice(color_code):
        if color_code == 0:
            return 'purple'
        elif color_code == 1:
            return 'green'
        elif color_code == 2:
            return 'red'
        elif color_code == 3:
            return 'yellow'
        elif color_code == 4:
            return 'blue'
        elif color_code == 5:
            return 'grey'
        elif color_code == 6:
            return 'white'

    colors = [color_choice(color_code) for color_code in colors]

    for i in xrange(len(xranges)) :
        coll = collections.BrokenBarHCollection([xranges[i]], yrange, facecolor=colors[i], alpha=0.5)
        ax.add_collection(coll)

    plt.show()


def process_gsr(signal):
    front_cut_off = 300

    filtered_signal = low_pass(signal,'cos',5000)

    baseline = None
    
    grad = gradient(filtered_signal)

    filtered_grad = None#low_pass(grad, 'cos', 10000)

    return filtered_signal, grad, filtered_grad,baseline


def process_data():

    subject_id = str(205)
    session = str(2)
    train_number = str(1)

    # file paths
    subject_folder = conf.data_path + os.sep + 'subject_' + subject_id
    physio_file_name='physio_record_' + subject_id +'_'+ session +'_'+ train_number +'.csv'
    physio_data_path =  subject_folder + os.sep + physio_file_name
    meta_path = subject_folder + os.sep + 'physio_meta_' + subject_id +'.yml'
    parameters_path = subject_folder + os.sep + 'parameters_' + subject_id + '_' + session +'.csv'
    smallspread_path = subject_folder + os.sep + 'Smallspread_' + subject_id + '_' + session +'.csv'
    scores_path = subject_folder + os.sep + 'SubjectScores.csv'

    # load all data
    physio_data = load_physio_data(physio_data_path)
    parameters = load_data(parameters_path)
    smallspread = load_data(smallspread_path)
    scores = load_data(scores_path)

    # prepare_data
    parameters = prepare_munis_data(parameters)
    smallspread = prepare_munis_data(smallspread)
    scores = prepare_munis_data(scores)

    # get physio starting time from yaml file
    with open(meta_path) as yaml_file :
        meta = yaml.load(yaml_file.read())
    physio_times_start = -1
    for record in meta['records']:
        if record['file_name'].endswith(physio_file_name) :
            physio_times_start = float(record['start_time'])
    if physio_times_start == -1 :
        raise Exception(record_file_name + 'not found!')    

    """path = data_path + str(subject_id) + '/Trial-Error-Angles.csv'
    te_angles = load_data(path)
    path = data_path + str(subject_id) + '/Trial-Stressors.csv'
    trail_stessors = load_data(path)"""

    # convert dates to seconds
    physio_times = array(physio_data[0], dtype='float64')/1000.0
    p_times = convert_time_array(parameters[0])
    s_times = convert_time_array(smallspread[0])

    # get start times
    p_times_start = p_times[0]
    s_times_start = s_times[0]

    # absolute time to relative time representation
    p_times -= p_times[0]
    s_times -= s_times[0]

    print 'p_times', len(p_times), p_times[0]
    print 's_times', len(s_times), s_times[0]
    print 'p_times_start',p_times_start
    print 's_times_start', s_times_start
    print 'physio_times_start', physio_times_start

    # align timescales
    physio_times,p_times,s_times =\
    align_times((physio_times_start,p_times_start,s_times_start),\
        [physio_times,p_times,s_times])

    # (time,data) tuples
    ecg_data = (physio_times,physio_data[1])
    gsr_data = (physio_times,physio_data[2])
    conditions = (p_times,parameters[8]) # trail type
    print(set(conditions[1]))

    # process physio data
    pulse = process_ecg(ecg_data[1])
    gsr_f, gsr_g, gsr_f_g, gsr_b = process_gsr(gsr_data[1])
    #filtered_signal,grad,filtered_grad,baseline

    filtered_gsr_data = (physio_times,gsr_f)

    #epochs_gsr = divide_into_epoches(conditions,filtered_gsr_data)

    di = distances(conditions[0])

    #x_axis_divisions = append(conditions[0],filtered_gsr_data[0][-1])
    x_axis_divisions = [conditions[0][0]]
    colors = [conditions[1][0]]
    last_c = conditions[1][0]
    for i,c in enumerate(conditions[1]) :
        if last_c != c :
            x_axis_divisions.append(conditions[0][i])
            colors.append(c)
            last_c = c    

    plot_with_background_color(x_axis_divisions,colors,filtered_gsr_data)


    #figure()
    #plot(ecg_data[0],ecg_data[1])
    #figure()
    #plot(gsr_data[0],gsr_f)
    #figure()
    #step(conditions[0],conditions[1])
    #figure()
    #figure()
    #step(status[0],status[1])
    show()

def is_float(number):
    try :
        float(number)
        return True
    except :
        return False

if __name__ == '__main__' :
    ecg = False
    process = True

    if process :
        process_data()
        sys.exit(0)

    path = '../data/trail_data/records/102_000.csv'
    data = load_data(path)
        
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
