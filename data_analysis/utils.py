import sys

def print_percent(num):
    num = int(num)*100
    if num < 10 :
        num = '0' + str(num)
    else :
        num = str(num)
    print('\b\b\b' + num + '%', end='')
    sys.stdout.flush()
