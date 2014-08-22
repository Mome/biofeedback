from pylab import * 

data = open('ecg_record').readlines()
data = data[3860:]
data = [d.split(' ') for d in data]

ecg = [d[0] for d in data]
gsr = [d[1] for d in data]

plot(ecg)
figure()
plot(gsr)
title('Galvanic Skin Response')
xlabel(r'Milisekunden ($msec$)')
ylabel(r'Skin Conductance ($\mu S$)')
grid()
show()
