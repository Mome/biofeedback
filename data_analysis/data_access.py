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
import yaml


PATH_TO_DB = os.path.expanduser('~/code/biofeedback/data/InlusioDB.sqlite')
PHYSIO_PATH = os.path.expanduser('~/code/biofeedback/data/inlusio_data')


def get_game_data(subject_number, session_id = None, trial_id = None):    
    con = sqlite3.connect(PATH_TO_DB)
    sql = "select * from TRIALS_WITH_STATUS_NOT_NULL where Subject_number = " + str(subject_number)
    if (session_id is not None ):
        sql += " and Session_id = " + str(session_id)
    if (trial_id is not None ):
        sql += " and Trial_id = " + str(trial_id)
    
    df = pd.read_sql(sql, con)
    return df


def get_physio_data(subject_num, session_num):
    """reads data of physiological measurement from csv. Concatinates multiple records for one session."""
    subject_num = str(subject_num)
    session_num = str(session_num)
    
    subject_path = pathlib.Path(PHYSIO_PATH + '/subject_' + subject_num)
    meta_file_path = subject_path.joinpath('physio_meta_' + subject_num + '.yml') 
    
    if not subject_path.exists() :
        raise Exception('Subject folder not found !')
    
    # open metadata file
    with meta_file_path.open() as yaml_file :
        physio_meta = yaml.load(yaml_file.read())

    # construct list of record starting times
    starting_times = [(rec['number'], float(rec['start_time']))  for rec in physio_meta['records']]
    starting_times = dict(starting_times)
    print(starting_times)

    # load recodrs and set to absolute time
    column_names = ['time','ecg','gsr']
    physio_data = pd.DataFrame(columns=column_names)
    pattern = 'physio_record_' + subject_num + '_' + session_num + '_*.csv'

    for record_path in subject_path.glob(pattern) :
       
        # load physio_data
        physio_record = pd.read_csv(
            str(record_path),
            comment='#',
            header=None,
            names = column_names
            )
        
        # convert physio time to seconds
        physio_record['time'] /= 1000
        
        # convert to absolute time
        record_number = int(record_path.stem.split('_')[-1])
        s_time = starting_times[record_number]
        physio_record['time'] += s_time
        
        # concatinate to other records
        physio_data = physio_data.append(physio_record, ignore_index=True)
    
    # sort records by time
    # ... maybe not important
    physio_data = physio_data.sort('time')
   
    return physio_data
