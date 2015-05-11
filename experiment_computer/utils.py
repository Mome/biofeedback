"""Gather wild functions."""

import os

def is_float(num):
    try :
        float(num)
        return True
    except :
        return False


def is_int(num):
    try :
        int(num)
        return True
    except :
        return False


def create_singelton():
    home_folder = os.path.expanduser('~')
    open(home_folder + os.sep + 'physio_singleton_lock','w')


def remove_singleton():
    home_folder = os.path.expanduser('~')
    os.remove(home_folder + os.sep + 'physio_singleton_lock')


def singleton_exists():
    home_folder = os.path.expanduser('~')
    return os.path.exists(home_folder + os.sep + 'physio_singleton_lock')
