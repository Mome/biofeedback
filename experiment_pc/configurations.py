
data_path = '~/inlusio_data/records'
metadata_path = '~/inlusio_data/metadata'
appdata_path = '~/biofeedback'
data_delimiter = ','


# ---------------- RESOLVE PATHS ---------------- #
import os
data_path = os.path.expanduser(data_path)
data_path = os.path.normpath(data_path)
metadata_path = os.path.expanduser(metadata_path)
metadata_path = os.path.normpath(metadata_path)
appdata_path = os.path.expanduser(appdata_path)
appdata_path = os.path.normpath(appdata_path)
del os
# ----------------------------------------------- #