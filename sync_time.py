#! /usr/bin/python
import ntplib
import time
import sys
import os
import pickle

def sync_time(ip='10.42.0.1',c=None):
    
    if c == None :
        c = ntplib.NTPClient()
    try:
        r = c.request(ip)
        rt = r.recv_time
        gmt = time.gmtime(rt)
        time_str = time.strftime('%d %b %Y %H:%M:%S',gmt)
        time_str = time_str + '.' + str(rt-int(rt))[2:]
        #print time_str
        os.system('date -s ' + "'" + time_str + "'")
    except :
        print 'no connection to sync'


if 'sync' in sys.argv:
    sync_time()

if 'save' in sys.argv:
    rep = 1000
    c = ntplib.NTPClient()
    save = [None]*rep
    for i in range(rep) :
	sync_time()
        try :
            r = c.request('10.42.0.1')
            save[i]=r.offset
	    if 'show' in sys.argv :
                print r.offset
        except :
            save[i]=0
            print 'no connection to save'
        #time.sleep(0.1)
    pickle.dump(save, open('time_offset','w'))

elif 'show' in sys.argv :
    c = ntplib.NTPClient()
    while True :
        r = c.request('10.42.0.1')
        print r.offset
        time.sleep(1)
        
