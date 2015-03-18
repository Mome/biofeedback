# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 16:02:50 2015

@author: Lukas, Mome
@desc: Data access module. Contains all the methods to grab data from the 
sqlite-Database and the .csv-files for the physiological data.
"""
import configparser
import datetime
import os
import pathlib
import sqlite3

import numpy
import pandas as pd
import yaml


def get_block_times(subject_number, session_number):
    if (subject_number is None):
        return None
    con = sqlite3.connect(PATH_TO_DB)
    sql = "select * from BLOCK_TIMES where Subject_number = " + str(subject_number)
    if (session_number is not None ):
        sql += " and SessionNumber = " + str(session_number)
    
    df = pd.read_sql(sql, con)

    # convert to seconds since epoche
    #print(df['EndTimeTrial'][0])
    df['StartTimeTrial'] = pd.to_datetime(df['StartTimeTrial'])
    df['EndTimeTrial']   = pd.to_datetime(df['EndTimeTrial'])
    #print(type(df['EndTimeTrial'][0]))
    df['StartTimeTrial'] = ( df['StartTimeTrial'] - datetime.timedelta(hours=1) - datetime.datetime(1970,1,1) ) / numpy.timedelta64(1,'s')
    df['EndTimeTrial']   = ( df['EndTimeTrial']   - datetime.timedelta(hours=1) - datetime.datetime(1970,1,1) ) / numpy.timedelta64(1,'s')
    
    # convert to UTC
    #df['StartTimeTrial'] -= 3600
    #df['EndTimeTrial'] -= 3600
    return df


def raw_block_times(subject_number, session_number):
    if (subject_number is None):
        return None
    con = sqlite3.connect(PATH_TO_DB)
    sql = "select * from BLOCK_TIMES where Subject_number = " + str(subject_number)
    if (session_number is not None ):
        sql += " and SessionNumber = " + str(session_number)
    
    df = pd.read_sql(sql, con)

    return df  


def get_game_data(subject_number, session_number = None, trial_id = None):    
    con = sqlite3.connect(PATH_TO_DB)
    sql = "select * from TRIALS_WITH_STATUS where Subject_number = " + str(subject_number)
    if (session_number is not None ):
        sql += " and SessionNumber = " + str(session_number)
    if (trial_id is not None ):
        sql += " and Trial_id = " + str(trial_id)
    
    df = pd.read_sql(sql, con)
    # ToDo: convert times to seconds
    return df


def get_physio_data(subject_num, session_num):
    """reads data of physiological measurement from csv. Concatinates multiple records for one session."""
    subject_num = str(subject_num)
    session_num = str(session_num)
    
    subject_path = pathlib.Path(PHYSIO_PATH + '/subject_' + subject_num)
    meta_file_path = subject_path.joinpath('physio_meta_' + subject_num + '.yml') 
    
    #print(subject_path)
    if not subject_path.exists() :
        raise Exception('Subject folder not found !')
    
    # open metadata file
    with meta_file_path.open() as yaml_file :
        physio_meta = yaml.load(yaml_file.read())

    # construct list of record starting times
    starting_times = [(rec['number'], float(rec['start_time']))  for rec in physio_meta['records']]
    starting_times = dict(starting_times)
    #print(starting_times)

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
    physio_data = physio_data.sort('time')
    
    return physio_data


def load_configurations() :
    """ Loads the location of the physio data and database.
    Creates configfile if no file can be found."""

    local_path = os.path.dirname(os.path.abspath(__file__))
    print(local_path)
    file_path = local_path + os.sep + 'conf.ini'
    parser = configparser.ConfigParser()

    if os.path.exists(file_path) :
        config = parser.read(file_path)
    else :
        parser['PATH'] = {}
        parser['PATH']['PATH_TO_DB'] = os.path.expanduser('~/inlusio_data/InlusioDB_260225.sqlite')
        parser['PATH']['PHYSIO_PATH'] = os.path.expanduser('~/inlusio_data')
        print('Creating new configuration file!!!')
        print('Please fit conf.ini to your local data path!')
        with open(file_path, 'w') as configfile:
            parser.write(configfile)

    return parser


config = load_configurations()

#PATH_TO_DB = os.path.expanduser('~/code/biofeedback/data/InlusioDB.sqlite')
#PATH_TO_DB = os.path.expanduser('~/inlusio_data/InlusioDB_150225.sqlite')
#PATH_TO_DB = os.path.expanduser('~/inlusio_data/InlusioDB_260225.sqlite')
#PATH_TO_DB = os.path.expanduser('~/SkyDrive/Dokumente/Master/02 Semester/inlusio/InlusioDB_150225.sqlite')
#PHYSIO_PATH = os.path.expanduser('~/code/biofeedback/data/inlusio_data')

PATH_TO_DB = config['PATH']['PATH_TO_DB']
PHYSIO_PATH = config['PATH']['PHYSIO_PATH']