from collections import namedtuple
import itertools
import os

import numpy as np

import data_access as da
import data_preprocessing as dpp


def save_mean_table() :

    subjects = [403, 416, 421, 424, 430, 433, 434, 437,
        419, 420, 425, 426, 428, 429, 432, 436]

    path = da.config['PATH']['physio_path']
    path = os.path.join(path, 'gsr_results_table.csv')

    options = {
        'do_gsr' : True,
        'do_trials' : True,
        'only_success' : False,
        'silent' : True,
    }

    # transform all keys to lower case
    options = {key.lower():value for key, value in options.items()}

    # add missing keys to options and transform to namedtuple
    option_keys =('do_ecg','do_gsr','do_blocks','do_trials','silent')
    default_opts = dict.fromkeys(option_keys, False)
    default_opts.update(options)

    # convert to named tuple for easier access
    options = namedtuple('Options', default_opts.keys())(**default_opts)

    # if file already exists cancel everything
    if os.path.exists(path) :
        print path, 'file already exists'
        return

    # write column names to csv file
    head = 'subject,session,trial_id,condition,mean_gsr\n'
    with open(path,'w') as f :
        f.write(head)

    # bring subject and session in a form to easy iterate over
    
    sessions = [1,2]*len(subjects)
    subjects = itertools.chain(*zip(subjects,subjects))

    for subject, session in zip(subjects, sessions) :

        print 'Processing subject %s session %s' % (subject, session)

        subject = str(subject)
        session = str(session)

        # try to load data
        try:
            physio_data, trials, time_range = da.get_data(subject, session, options.only_success)
        except da.DataAccessError as e:
            print('Skip subject %s session %s: %s' % (subject, session, e))
            continue 

        time_scale = np.array(physio_data['time'])

        #print len(time_range), len(time_scale)

        if len(time_scale) == 0 :
            raise Exception('not physio data')

        results = dpp.process_data(physio_data, trials, subject, session, options)

        condition = trials[2]
        trial_id = trials[3]
        trails = trials[:-1]
        gsr_mean = results.mean_gsr_for_trials

        trials = zip(*trials)

        lines = [ ','.join([subject,session,str(tid),cond,str(gsr) + '\n']) for tid,cond,gsr in \
        zip(trial_id, condition, gsr_mean) ]

        with open(path,'a') as f :
            f.writelines(lines)


def save_raw_table():

    #subjects = [403, 416, 421, 424, 430, 433, 434, 437, 419, 420, 425, 426, 428, 429, 432, 436]
    
    #subjects = [314, 319,321,323,325,326,327,328,332,333]

    subjects = [312,314,315,317,320,322,
                329,330,332,403,416,419,
                420,421,424,425,426,428,
                430,432,433,436,437]

    path = da.config['PATH']['physio_path']
    version_major = 5
    version_minor = 0
    path = os.path.join(path, 'gsr_to_gamedata_table_v' + str(version_major) + '.' + str(version_minor)  + '.csv')

    options = {
        'do_gsr' : True,
        'do_trials' : True,
        'only_success' : False,
        'silent' : True,
        'overwrite' : False,
    }

    # transform all keys to lower case
    options = {key.lower():value for key, value in options.items()}

    # add missing keys to options and transform to namedtuple
    option_keys =('do_ecg','do_gsr','do_blocks','do_trials','only_success', 'silent','overwrite')
    default_opts = dict.fromkeys(option_keys, False)
    default_opts.update(options)

    # convert to named tuple for easier access
    options = namedtuple('Options', default_opts.keys())(**default_opts)

    # if file already exists cancel everything
    if not options.overwrite and os.path.exists(path):
        print path, 'file already exists'
        return

    # write column names to csv file
    head = 'subject,session,physio_time,raw_gsr,condition,trial_id,success\n'
    with open(path,'w') as f:
        f.write(head)

    # bring subject and session in a form to easy iterate over
    
    sessions = [1,2]*len(subjects)
    subjects = itertools.chain(*zip(subjects,subjects))

    for subject, session in zip(subjects, sessions) :

        print 'Processing subject %s session %s' % (subject, session)

        subject = str(subject)
        session = str(session)

        # skip 
        try:
            physio_data, trials, time_range = da.get_data(subject, session, options.only_success, options.silent)
        except da.DataAccessError as e:
            print('Skip subject %s session %s: %s' % (subject, session, e))
            continue

        time_scale = np.array(physio_data['time'])

        #print len(time_range), len(time_scale)

        if len(time_scale) == 0 :
            raise Exception('not physio data')

        results = dpp.process_data(physio_data, trials, subject, session, options)

        raw_gsr = physio_data['gsr']
        cond_for_physio = results.conditions_for_physio
        trial_for_physio = results.trial_ids_for_physio
        success_for_physio = results.success_for_physio

        lines = [ ','.join([subject, session, str(t), str(gsr), str(cond), str(tid), str(sfp)+ '\n']) for t,gsr,cond,tid,sfp in \
        zip(time_scale, raw_gsr, cond_for_physio, trial_for_physio, success_for_physio) ]

        with open(path,'a') as f :
            f.writelines(lines)


if __name__ == '__main__':
    save_raw_table()
