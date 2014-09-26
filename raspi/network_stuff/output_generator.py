from math import sin,cos
from time import sleep
step=0.1
msec=500
i=0
for _ in [1,2,3,4,5,6] :
    print(i,sin(i),cos((i*i)/10))
    i+=step
    sleep(msec/1000)

