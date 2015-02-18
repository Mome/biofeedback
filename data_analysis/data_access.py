# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 16:02:50 2015

@author: Lukas
@desc: Data access module. Contains all the methods to grab data from the 
sqlite-Database and the .csv-files for the physiological data.
"""
import sqlite3
import pandas as pd

PATH_TO_DB = 'C:/Users/Lukas/SkyDrive/Dokumente/Master/02 Semester/inlusio/InlusioDB_2015-01-26.sqlite'

def get_game_data(subject_number, session_id = None, trial_id = None):    
    con = sqlite3.connect(PATH_TO_DB)
    sql = "select * from TRIALS_WITH_STATUS_NOT_NULL where Subject_number = " + str(subject_number)
    if (session_id is not None ):
        sql += " and Session_id = " + str(session_id)
    if (trial_id is not None ):
        sql += " and Trial_id = " + str(trial_id)
    
    df = pd.read_sql(sql, con)
    return df

def get_physio_data(subject_number, session_id = None)