import configurations as conf
import os
import yaml

class Subject:

	def __init__(self,subject_id):
		file_path = conf.meta_data_path + os.ep + str(subject_id) + '.yml'
		if os.path.exists(file_path) :
			self.f = open(file_path,'wr')
			d = yaml.load(self.f)
			self.subject_id = d['']
		else :
			self.f = open(file_path,'wr')
			self.subject_id = subject_id
			self.comment = ''
			self.records = []
			self.save()

	def get_dict():
		d = {}
		d['subject_id'] = self.subject_id
		d['comment'] = self.comment
		d['records'] = self.records
		return d

	def get_comment(self):
		return self.comment

	def set_comment(self,comment):
		self.comment = comment

	def add_record(self, file_name, session, start_time, sample_rate, column_labels, marker, comment):
		d = {}
		d['file_name'] = file_name
		d['session'] = session
		d['start_time'] = start_time
		d['sample_rate'] = sample_rate
		d['comment'] = comment
		d['marker'] = marker

		for i, label in enumerate(column_labels):
			d['column_' + str(i+1)] = label

		self.records.append(d)

	def save(self):
		d = get_dict()
		yaml_code = yaml.dump(d,allow_unicode=True,default_flow_style=False)
		self.f.write(yaml_code)


	def __del__(self):
		self.f.close()
