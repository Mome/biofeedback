# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 16:02:50 2015

@author: Lukas, Mome
@desc: Data access module. Contains all the methods to grab data from the 
sqlite-Database and the .csv-files for the physiological data.
"""
import os
import pathlib
import sqlite3

import pandas as pd


PATH_TO_DB = 'C:/Users/Lukas/SkyDrive/Dokumente/Master/02 Semester/inlusio/InlusioDB_2015-01-26.sqlite'
PHYSIO_PATH = os.path.expanduser('~/inlusio_data') #this makes it a little bit more platform independent


def get_game_data(subject_number, session_id = None, trial_id = None):    
    con = sqlite3.connect(PATH_TO_DB)
    sql = "select * from TRIALS_WITH_STATUS_NOT_NULL where Subject_number = " + str(subject_number)
    if (session_id is not None ):
        sql += " and Session_id = " + str(session_id)
    if (trial_id is not None ):
        sql += " and Trial_id = " + str(trial_id)
    
    df = pd.read_sql(sql, con)
    return df



def get_physio_data(subject_id, session_id):
    """reads data of physiological measurement from csv. Concatinates multiple records for one session."""
    subject_id = str(subject_id)
    session_id = str(session_id)
    subject_path = pathlib.Path(PHYSIO_PATH + '/subject_' + subject)
    
    if not subject_path.exists() :
        raise Exception('Subject folder not found !')
    
    # load metadata

    # load recodrs
    pd.read_csv




