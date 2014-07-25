data = []

for i in range(1,16)+['17a','17b'] :
    if type(i)==int and i<10 :
        filename = 'drivedb/drive0'+str(i)+'.txt'
    else :
        filename = 'drivedb/drive'+str(i)+'.txt'

    d = open(filename).readlines()

    print [[int(l) for l in line] for line in [line.split() for line in d]
    raw_input()
