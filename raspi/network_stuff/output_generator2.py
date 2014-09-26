import time
import subprocess
i = 0
while True:
    subprocess.call('echo ' + str(i))
    time.slee(1000)
    i+=1
