from pylab import *
import sys

file_name = sys.argv[1]

data = open(file_name).readlines()
data = [point.strip().split() for point in data if point.strip()!='']
data = array(data)
plot(data.T[0],data.T[1])
savefig('ecg.svg')
show()
