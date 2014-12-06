
data_path = '~/inlusio_data'
metadata_path = '~/inlusio_data'
appdata_path = '~/inlusio_data'
data_delimiter = ','

default_coloumn_labels = ['relative_time','ecg','gsr']
default_raspi_port = 49152
default_sample_rate = '100Hz'
metadata_file_prefix = 'physio_meta'




# ---------------- RESOLVE PATHS ---------------- #
import os
data_path = os.path.expanduser(data_path)
data_path = os.path.normpath(data_path)
metadata_path = os.path.expanduser(metadata_path)
metadata_path = os.path.normpath(metadata_path)
appdata_path = os.path.expanduser(appdata_path)
appdata_path = os.path.normpath(appdata_path)
module_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.normpath(module_path)
del os
# ----------------------------------------------- #