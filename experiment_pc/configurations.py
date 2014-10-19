
data_path = '~/inlusio_data/records'
metadata_path = '~/inlusio_data/metadata'
data_delimiter = ','


# ---------------- RESOLVE PATHS ---------------- #
import os                                         #
data_path = os.path.expanduser(data_path)         #
if not data_path.endswith('/') :                  #
	data_path += '/'                              #
metadata_path = os.path.expanduser(metadata_path) #
if not metadata_path.endswith('/') :              #
	metadata_path += '/'                          #
del os                                            #
# ----------------------------------------------- #

#TODO path management for WINDOWS