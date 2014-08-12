from pylab import * 

data = open('tmp_file').readlines()
plot(data)
title('Galvanic Skin Response')
xlabel(r'Time ($sec$)')
ylabel(r'Skin Conductance ($\mu S$)')
grid()
show()
