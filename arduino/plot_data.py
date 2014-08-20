from pylab import * 

data = open('ecg_record').readlines()
plot(data)
title('Galvanic Skin Response')
xlabel(r'Milisekunden ($msec$)')
ylabel(r'Skin Conductance ($\mu S$)')
grid()
show()
