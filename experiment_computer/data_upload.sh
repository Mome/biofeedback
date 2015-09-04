#! /bin/bash

title="Inlusio data upload ..."
echo -e '\033]2;'$title'\007'

read -p "Enter username: " user

src=~/inlusio_data/*
dest="gate.ikw.uos.de:/net/store/nbp/inlusio_data"

#echo "Copy from: " $src
#echo "Copy to: "$dest

rsync -avz $src $user@$dest

read -p "Press [Enter] key to close..."
