# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 16:02:50 2015

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
import pylab as pl
import yaml


def get_data(subject, session) :
    """ Gets all data for a subject and session"""

    game_data = get_game_data3(subject, session, silent=True)
    physio_data = get_physio_data(subject, session)

    # using my block times extraction
    trials = extract_trial_times(game_data)
    if len(trials[0]) == 0 :
        raise Exception('no trials extracted')

    # transform to relative time scales
    min_tr0 = min(trials[0])
    min_tr1 = min(trials[1])
    min_phy = min(physio_data['time'])
    min_time = min(min_tr0, min_tr1, min_phy)
    physio_data['time'] -= min_time
    trials[0] -= min_time
    trials[1] -= min_time

    return physio_data, trials


def get_block_times(subject_number, session_number):
    if (subject_number is None):
        return None
    con = sqlite3.connect(PATH_TO_DB)
    sql = "select * from BLOCK_TIMES where Subject_number = " + str(subject_number)
    if (session_number is not None ):
        sql += " and SessionNumber = " + str(session_number)
    
    df = pd.read_sql(sql, con)

    # convert to seconds since epoche
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


def get_game_data3(subject_number, session_number = None, trial_id = None, silent=False):
    if not silent :
        print PATH_TO_DB
        print os.path.exists(PATH_TO_DB)
    con = sqlite3.connect(PATH_TO_DB)
    # original Lucas : "select * from TRIALS_WITH_STATUS where Subject_number = "
    # Kriz change : "select * from TRIALS_WITH_STATUS_NOT_NULL where Subject_number = "
    sql = "select * from TRIALS_WITH_STATUS_NOT_NULL_AND_TABLE_SUCCESS where Subject_number = " + str(subject_number)
    if (session_number is not None ):
        sql += " and SessionNumber = " + str(session_number)
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
    
    #print(subject_path)
    if not subject_path.exists() :
        raise Exception('Subject folder not found !')
    
    # open metadata file
    with meta_file_path.open() as yaml_file :
        physio_meta = yaml.load(yaml_file.read())

    # construct list of record starting times
    starting_times = [(rec['number'], float(rec['start_time'])) for rec in physio_meta['records']  if rec['session']==session_num]
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
        #record_number = int(record_path.stem.split('_')[-1])
        record_number = int(min(starting_times.keys()))
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


def only_get_physio_starting_times(subject_num):

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

    import time
    for i,j in starting_times.items() :
        print(i,j,time.asctime( time.gmtime(j) ))


def extract_trial_times(df):

    # filter out uncessessful
    df = df[df['Success']==1]

    times = df['Zeitpunkt']
    status = df['Status']
    #types = df['BlockType']
    types = df['Type']
    trial_ids = df['Trial_id']

    times = pd.to_datetime(times)
    times = ( times - datetime.timedelta(hours=1) - datetime.datetime(1970,1,1) ) / pl.timedelta64(1,'s')

    times = pl.array(times)
    status = pl.array(status)
    types = pl.array(types)
    trial_ids = pl.array(trial_ids)

    starts = (status == 'StartTimeTrial')
    ends = (status == 'EndTimeTrial')

    # remove BLOCKOVER types
    blockover = (types != 'BLOCKOVER')
    starts *= blockover
    ends *= blockover

    # ...
    start_ids = trial_ids[starts]
    end_ids = trial_ids[ends]

    start_types = types[starts]
    end_types = types[ends]

    start_times = times[starts]
    end_times = times[ends]

    #print('len(start_times)', len(start_times))

    #print(start_ids.head)
    #print(end_ids.head)

    # check for double trial_ids
    d = pl.sort(start_ids, axis=None)
    if any(d[d[1:] == d[:-1]]) :
        raise Exception('double start trial ids')
    d = pl.sort(end_ids, axis=None)
    if any(d[d[1:] == d[:-1]]) :
        raise Exception('double end trial ids')

    blocks = []
    for si in range(len(start_ids)) :
        sid = start_ids[si]
        match = pl.where(sid==end_ids)[0]

        if len(match) == 0 :
            continue

        ei = match[0]

        if start_types[si] != end_types[ei] :
            raise Exception('Unequal types for start and endtrial ' + str(sid))
        elif len(match) > 1 :
            raise Exception('more than one match')

        start_time = start_times[si]
        end_time = end_times[ei]
        trial_type = start_types[si]
        trial_id = trial_ids[si]

        if pl.isnan(start_time) or pl.isnan(end_time) :
            continue

        blocks.append((start_time,end_time,trial_type,sid))

    if blocks == [] :
        return [],[],[]

    start_times, end_times, start_types, start_ids = zip(*blocks)

    start_times = pl.array(start_times)
    end_times = pl.array(end_times)
    start_types = pl.array(start_types)
    start_ids = pl.array(start_ids)

    return [start_times, end_times, start_types, start_ids]


# joins trials to blocks
def join_trials_to_blocks(start_times, end_times, start_types):

    # determine change of type
    change_of_types = [start_types[i]!=start_types[i+1] for i in range(len(start_types)-1)]
    
    start_times_index = pl.array([True] + change_of_types)
    end_times_index = pl.array(change_of_types + [True])

    start_times = start_times[start_times_index]
    end_times = end_times[end_times_index]
    start_types = start_types[start_times_index]

    return [start_times, end_times, start_types]

config = load_configurations()

#PATH_TO_DB = os.path.expanduser('~/code/biofeedback/data/InlusioDB.sqlite')
#PATH_TO_DB = os.path.expanduser('~/inlusio_data/InlusioDB_150225.sqlite')
#PATH_TO_DB = os.path.expanduser('~/inlusio_data/InlusioDB_260225.sqlite')
#PATH_TO_DB = os.path.expanduser('~/SkyDrive/Dokumente/Master/02 Semester/inlusio/InlusioDB_150225.sqlite')
#PHYSIO_PATH = os.path.expanduser('~/code/biofeedback/data/inlusio_data')

PATH_TO_DB = config['PATH']['PATH_TO_DB']
PHYSIO_PATH = config['PATH']['PHYSIO_PATH']
subjects = [312,315,317,320,321,322,323,328,329,330]
