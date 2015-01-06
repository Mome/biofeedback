
data_path = '~/inlusio_data'
metadata_path = '~/inlusio_data'
appdata_path = '~/inlusio_data'
netstore_path = "//samba.ikw.uos.de/dfs/store/nbp/inlusio_data"
data_delimiter = ','

default_coloumn_labels = ['relative_time','ecg','gsr']
default_raspi_port = 49152
default_sample_rate = '100Hz'
metadata_file_prefix = 'physio_meta'

win_port_id_1 = 'USB Serial Port (COM9)'
win_port_id_2 = 'FTDIBUS\\VID_0403+PID_6001+A900ABVGA\\0000'

linux_port_id_1 = 'Future Technology Devices International, Ltd FT232 USB-Serial (UART) IC '
linux_port_id_2 = 'USB VID:PID=0403:6001 SNR=A900abvG'


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
netstore_path = os.path.normpath(netstore_path)
netstore_path = os.path.expanduser(netstore_path)
del os
# ----------------------------------------------- #