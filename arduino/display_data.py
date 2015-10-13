from pylab import *

lines = open('gsr_record').readlines()

lines = lines[1:]

def stuprint(l):
    print l
    return l

lines = [[float(l) for l in line.split('\t')] for line in lines]

lines = array(lines)

third = lines.T[0]

# first value ??

if third[0] == -1 :
    pass

for i,e in enumerate(third[1:]):
    if not e == -1 :
        continue
    
    prev = third[i-1]
    #find next value
    for j,f in enumerate(third[i:]):
        if not f == -1 :
            break

    if j+1  == len(third):
        pass

    thrid[i] = (j*prev + f)/(1+j)

plot(third)
show() 
