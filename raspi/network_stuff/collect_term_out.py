from subprocess import Popen, PIPE

p = Popen(['python','output_generator.py'],stdout=PIPE)
print(p.communicate())
print(dir(p))
