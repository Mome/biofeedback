from __future__ import division

from sys import argv, exit
import itertools

from pylab import *

import data_access as da
import signal_classes as signal
import data_preprocessing as dpp

def save_table(path) :

    if os.path.exists(path + '/physio_results.csv') :
        print path + '/physio_results.csv', 'file already exists'
        return

    head = 'subject,session,trial_id,condition,mean_hr,mean_hrv,mean_gsr\n'

    with open(path + '/physio_results.csv','w') as f :
        f.write(head)

    subjects = repeat(da.subjects,2)
    sessions = [1,2]*len(da.subjects)

    for subject, session in zip(subjects, sessions) :

        # remove later after fixing
        if subject == 323 and session == 1 :
            continue

        print 'processing', subject, session

        subject = str(subject)
        session = str(session)

        physio_data, trials = da.get_data(subject, session)
        time_scale = array(physio_data['time'])

        if len(time_scale) == 0 :
            raise Exception('not physio data')

        ecg_signal = signal.EcgSignal( time_scale, physio_data['ecg'] )
        ecg_signal.remove_nans()
        ecg_signal.detect_beats()
        #ecg_signal._detect_compressions()
        ecg_signal.fill_gaps()
        ecg_signal.beat_intervalls_by_gaps()
        ecg_signal.remove_small_intervalls()

        gsr_signal = signal.GsrSignal( time_scale, physio_data['gsr'] )
        gsr_signal.remove_nans()
        gsr_signal.remove_invalid_values()

        """
        plot(ecg_signal.time_scale, ecg_signal.signal)
        scatter(ecg_signal.beats, 2.5*ones(len(ecg_signal.beats)))
        plot(gsr_signal.time_scale, gsr_signal.signal)"""

        condition = trials[2]
        trial_id = trials[3]
        trails = trials[:-1] 

        #blocks = dpp.join_trails_to_blocks(*trails)

        trials = zip(*trials)

        mean_hr_for_trials = ecg_signal.mean_value_for_blocks(trials,'hr')
        mean_hrv_for_trials = ecg_signal.mean_value_for_blocks(trials,'hrv')
        gsr_mean = gsr_signal.mean_gsr_for_blocks(trials)

        """figure()
        plot(mean_ecg_for_trials)
        plot(gsr_mean)
        show()"""

        # convert to bpm
        mean_hr_for_trials = mean_hr_for_trials*60

        subject_number = [subject]*len(trial_id)
        session_number = [session]*len(trial_id)

        lines = [ ','.join([subject,session,str(i),c,str(hr),str(hrv),str(gsr) + '\n']) for i,c,hr,hrv,gsr in \
        zip(trial_id, condition, mean_hr_for_trials,mean_hrv_for_trials, gsr_mean) ]

        with open(path + '/physio_results.csv','a') as f :
            f.writelines(lines)


if argv[1] == 'save' :

    import os
    directory = os.path.expanduser('~/inlusio_plots')
    if not os.path.exists(directory) :
        print('mkdir', directory)
        os.mkdir(directory)

    #subject_folders = os.listdir(da.PHYSIO_PATH)
    #subject_numbers = [folder.split('_')[-1] for folder in subject_folders]
    #subject_numbers.sort()

    save_table(directory)

else :
    subject = argv[1]
    session = argv[2]
    save_table(subject, sesison, '.')


"""
physio_start = time_scale[0]

convert time scales to minues
time_scale /= 60
mts = min(time_scale)
time_scale = time_scale-mts
"""
