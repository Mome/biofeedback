#! /bin/bash

title="Inlusio data download ..."
echo -e '\033]2;'$title'\007'

read -p "Enter username: " user

src="gate.ikw.uos.de:/net/store/nbp/inlusio_data/*"
dest=~/inlusio_data/

#echo "Copy from: " $src
#echo "Copy to: "$dest

rsync -avz $user@$src $dest

read -p "Press [Enter] key to close..."
