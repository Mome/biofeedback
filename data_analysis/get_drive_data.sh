# get sample data with
wget -r -np http://www.physionet.org/pn3/drivedb/

mv www.physionet.org/pn3/drivedb/ .
rm -R  www.physionet.org

# convert to readable data
rdsamp -r drivedb/drive01 > drivedb/drive01.txt
rdsamp -r drivedb/drive02 > drivedb/drive02.txt
rdsamp -r drivedb/drive03 > drivedb/drive03.txt
rdsamp -r drivedb/drive04 > drivedb/drive04.txt
rdsamp -r drivedb/drive05 > drivedb/drive05.txt
rdsamp -r drivedb/drive06 > drivedb/drive06.txt
rdsamp -r drivedb/drive07 > drivedb/drive07.txt
rdsamp -r drivedb/drive08 > drivedb/drive08.txt
rdsamp -r drivedb/drive09 > drivedb/drive09.txt
rdsamp -r drivedb/drive10 > drivedb/drive10.txt
rdsamp -r drivedb/drive11 > drivedb/drive11.txt
rdsamp -r drivedb/drive12 > drivedb/drive12.txt
rdsamp -r drivedb/drive13 > drivedb/drive13.txt
rdsamp -r drivedb/drive14 > drivedb/drive14.txt
rdsamp -r drivedb/drive15 > drivedb/drive15.txt
rdsamp -r drivedb/drive16 > drivedb/drive16.txt
rdsamp -r drivedb/drive17a > drivedb/drive17a.txt
rdsamp -r drivedb/drive17b > drivedb/drive17b.txt

# annotation reader (wouldn't work, due to missing atr file)
# rdann -r drivedb/drive01 -a atr > drive01.txt


# notes (transform .hea files)
wfdbdesc drivedb/drive01 > drivedb/note_drive01.txt
wfdbdesc drivedb/drive02 > drivedb/note_drive02.txt
wfdbdesc drivedb/drive03 > drivedb/note_drive03.txt
wfdbdesc drivedb/drive04 > drivedb/note_drive04.txt
wfdbdesc drivedb/drive05 > drivedb/note_drive05.txt
wfdbdesc drivedb/drive06 > drivedb/note_drive06.txt
wfdbdesc drivedb/drive07 > drivedb/note_drive07.txt
wfdbdesc drivedb/drive08 > drivedb/note_drive08.txt
wfdbdesc drivedb/drive09 > drivedb/note_drive09.txt
wfdbdesc drivedb/drive10 > drivedb/note_drive10.txt
wfdbdesc drivedb/drive11 > drivedb/note_drive11.txt
wfdbdesc drivedb/drive12 > drivedb/note_drive12.txt
wfdbdesc drivedb/drive13 > drivedb/note_drive13.txt
wfdbdesc drivedb/drive14 > drivedb/note_drive14.txt
wfdbdesc drivedb/drive15 > drivedb/note_drive15.txt
wfdbdesc drivedb/drive16 > drivedb/note_drive16.txt
wfdbdesc drivedb/drive17a > drivedb/note_drive17a.txt
wfdbdesc drivedb/drive17b > drivedb/note_drive17b.txt

#rm drivedb/*.dat
#rm drivedb/*.hea
#rm drivedb/index*
rm drivedb/SHA*
rm drivedb/MD5*


