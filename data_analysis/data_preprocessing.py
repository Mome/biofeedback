# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 13:48:34 2015

@author: Lukas
"""
from data_access import *

def change_block_times_format(df):
    list = []
    for index, row in df.iterrows():
        tupel = (row['StartTimeTrial'],row['EndTimeTrial'], row['Type'])
        list.append(tupel)
    return list
