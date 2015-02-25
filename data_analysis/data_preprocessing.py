from pylab import *

def filter_ecg(ecg_signal) :
	pass

def filter_gsr(gsr_signal):
	pass



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