from __future__ import print_function
import sys
import pdb

def cache(func) :
  saved = {}
  @wraps(func)
  def newfunc(*args):
    if args in saved:
        return newfunc(*args)
    result =func(*args)
    saved[args] = result
    return result
  return newfunc

def print_percent(num):
    num = int(num)*100
    if num < 10 :
        num = '0' + str(num)
    else :
        num = str(num)
    print('\b\b\b' + num + '%', end='')
    sys.stdout.flush()

def is_float(num):
    try:
        float(num)
    except :
        return False
    return True

BP = pdb.set_trace

""" 
with ignored(OSError):
	os.remove('somefile.tmp')
"""