from pylab import *
from numpy import gradient
def load_data(path):
    with open(path) as csv_file:
        data = csv_file.readlines()
    data = [line.strip().split(',')[1:-1] for line in data if line.strip()!='']
    data = array(data,dtype='float32').T
    return data

def low_pass(signal, kernel_type, kernel_size):
    if kernel_type == 'rect':
        kernel = 1.0/kernel_size * ones(kernel_size)
    elif kernel_type == 'cos':
	N = kernel_size
        kernel = 0.5*(1-cos(2*pi*arange(N)/(N-1)))
    else :
        raise Exception('No such kernel: ' + kernel_type) 
    return convolve(signal, kernel, mode='same')

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
    data = load_data('../data/trail_data/102/Parameters.csv')
    plot(data[8])
    show()
