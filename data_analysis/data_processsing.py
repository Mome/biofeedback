from numpy import gradient, convolve

def low_pass(signal, kernel_type, kernel_size):
    if kernel_type == 'rect':
        print 'kernel ' + kernel_type
        kernel = 1.0/kernel_size * ones(kernel_size)
        print kernel
    else :
        raise Exception('No such kernel: ' + kernel_type) 
    return convolve(signal, kernel, mode='same')
