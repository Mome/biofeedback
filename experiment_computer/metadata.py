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
            with open(self.file_path) as f:
                d = yaml.load(open(self.file_path,'r'))
            self.subject_id = d['subject_id']
            self.comment = d['comment']
            self.records = d['records']
        else :
            self.subject_id = subject_id
            self.comment = ''
            self.records = []
            self.save()

    def get_dict(self):
        d = {}
        d['subject_id'] = self.subject_id
        d['comment'] = self.comment
        d['records'] = self.records
        return d

    def get_comment(self):
        return self.comment

    def set_comment(self,comment):
        self.comment = comment

    def add_record(self, number, file_name, session, start_time, source, sample_rate, column_labels, marker, comment):
        d = {}

        d['number'] = number
        d['file_name'] = file_name
        d['session'] = session
        d['start_time'] = start_time
        d['sample_rate'] = sample_rate
        d['comment'] = comment
        d['marker'] = marker
        d['source'] = source

        for i, label in enumerate(column_labels):
            d['column_' + str(i+1)] = label

        self.records.append(d)
        self.save()

    def get_next_record_number(self):
        if self.records == [] :
            next_number = 0
        else:
            next_number=max([r['number'] for r in self.records])+1
        return next_number

    def save(self):
        d = self.get_dict()
        yaml_code = yaml.dump(d,allow_unicode=True,default_flow_style=False)
        with open(self.file_path,'w') as f:
            f.write(yaml_code)

 
 