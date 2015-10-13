from pylab import * 
import sys

if len(sys.argv) >= 2 :
    file_name = sys.argv[1]
else :
    file_name = 'ecg_gsr_record'

data = open(file_name).readlines()
data = [d.split(' ') for d in data]

ecg = [d[0] for d in data]
gsr = [d[1] for d in data]

plot(ecg)
title('EKG')
xlabel(r'hunderstel sekunden')
figure()
plot(gsr)
title('Galvanic Skin Response')
xlabel(r'hunderstel sekunden')
ylabel(r'Skin Conductance ($\mu S$)')
grid()
show()
