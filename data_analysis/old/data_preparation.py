from __future__ import print_function
import os
import sys

import pandas as pd

sys.path.append('../experiment_computer')
import configurations as conf


def load_subject_data(subject_id, session):
	""" load the data files from the subject folder and align the time axis"""

	path = conf.data_path + os.sep + 'subject_' + str(subject_id)

	session_dict = get_session_files(subject_id) #stores information about subject files

	file_names = session_dict[session]['physio_record']
	if len(file_names) > 1 :
		print('WARNING: more than one physio_record file !', file=sys.stderr)
		print('Will use',file_names[0], '!' ,file=sys.stderr)

	coloumn_names = ['relative_times','ecg','gsr']
	physio_record = load_csv(path + os.sep + file_names[0], coloumn_names)

	coloumn_names = ['system_time' ,'trial_number' , 'spawn_distance' , 'generated_angle' , 'time_took_to_point_stage' ,
	 'time_took_to_point', 'aborted_trials', 'average_error', 'trial_type' ,'orientation', 'error_angle','success']
	parameters = load_csv(path + os.sep + session_dict[session]['parameters'], coloumn_names)

	coloumn_names = ['system_time' ,'trial_number' ,'duration_for_response','time_since_startup', 'status']
	stressors = load_csv(path + os.sep + session_dict[session]['stressors'], coloumn_names)

	# convert physio time to seconds
	physio_record['relative_times'] /= 1000

	# get physio starting time from yaml file
    with open(path + os.sep + session_dict['physio_meta']) as yaml_file :
        physio_meta = yaml.load(yaml_file.read())
    physio_record_start = -1
    for record in physio_meta['records']:
        if record['file_name'].endswith(file_names[0]) :
            physio_record_start = float(record['start_time'])
    if physio_record_start == -1 :
        raise Exception('Filename ' + file_names[0] + 'of metafile not found in subject folder!')  

	

	return physio_record, parameters, stressors


def load_csv(path, names) :
	
	data_frame = pd.read_csv(
		path,
		comment='#',
		header=None,
		names = names
		)

	return data_frame


# constructs a dict that categorizes filenames of a subject folder
def get_session_files(subject_id):

    folder = conf.data_path + os.sep + 'subject_' + str(subject_id)
    files = os.listdir(folder)

    session_files = {}


    for name in files :
        parts = name.split('.')[0]
        parts = parts.split('_')

        # find session
        if parts[0] == 'physio' and parts[1] == 'record' :

            session = parts[3]

            if session not in session_files :
                session_files[session] = {'physio_record':[],'parameters':None,'smallspread':None}

            session_files[session]['physio_record'] += [name]

        elif parts[0] == 'Smallspread' :

            session = parts[2]

            if session not in session_files :
                session_files[session] = {'physio_record':[],'parameters':None,'smallspread':None,'scores':None}

            session_files[session]['smallspread'] = name

        elif parts[0] == 'parameters' :

            session = parts[2]

            if session not in session_files :
                session_files[session] = {'physio_record':[],'parameters':None,'smallspread':None,'scores':None}

            session_files[session]['parameters'] = name

        elif name == 'SubjectScores.csv' :
            session_files['scores'] = name

        elif parts[0] == 'physio' and parts[1] == 'meta' :
            session_files['physio_meta'] = name

        else :
            if 'other' not in session_files :
                session_files['other'] = []
            session_files['other'] += [name]

    return session_files