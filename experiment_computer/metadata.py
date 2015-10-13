import configurations as conf
import os
import yaml

class Subject:

    def __init__(self,subject_id):
    
        path = conf.metadata_path + os.sep + 'subject_' + str(subject_id)

        if not os.path.exists(path) :
            os.makedirs(path)

        self.file_path = path + os.sep + conf.metadata_file_prefix + '_' + str(subject_id) + '.yml'

        if os.path.exists(self.file_path) :
            with open(self.file_path, 'r') as f:
                d = yaml.load(f)
            self.subject_id = d['subject_id']
            self.records = d['records']
        else :
            self.subject_id = subject_id
            self.records = []
            self.save()

    def get_dict(self):
        d = {}
        d['subject_id'] = self.subject_id
        d['records'] = self.records
        return d

    def add_record(self, number, file_name, session, start_time, source, sample_rate, column_labels):
        d = {}

        d['number'] = number
        d['file_name'] = file_name
        d['session'] = session
        d['start_time'] = start_time
        d['sample_rate'] = sample_rate
        d['source'] = source

        for i, label in enumerate(column_labels):
            d['column_' + str(i+1)] = label

        self.records.append(d)
        self.save()

    def get_next_record_number(self, session):

        valid_numbers = [r['number'] for r in self.records if r['session']==session]
        print valid_numbers

        if len(valid_numbers) == 0:
            next_number = 0
        else :
            next_number = max(valid_numbers)+1

        return next_number

    def save(self):
        d = self.get_dict()
        yaml_code = yaml.dump(d,allow_unicode=True,default_flow_style=False)
        with open(self.file_path,'w') as f:
            f.write(yaml_code)

 
 