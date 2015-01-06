import getpass
import os
import platform
import string
import subprocess
import sys

import configurations as conf

class WinHdMapper :

    def __init__(self, drive='Z', netstore_path=None):


        if netstore_path == None :
            netstore_path = conf.netstore_path

        self.drive = drive
        self.path = netstore_path

    #Small function to check the availability of network resource.
    def isAvailable(self):
        winCMD = 'IF EXIST ' + self.path + ' echo YES'
        cmdOutPut = subprocess.Popen(winCMD, stdout=subprocess.PIPE, shell=True).communicate()
        return string.find(str(cmdOutPut), 'YES',)

    #Small function to check if the mention location is a directory
    def isDirectory(self):
        winCMD = 'dir ' + self.path + ' | FIND ".."'
        cmdOutPut = subprocess.Popen(winCMD, stdout=subprocess.PIPE, shell=True).communicate()
        return string.find(str(cmdOutPut), 'DIR',)

    def mapNetworkDrive(self, user, password):

        #Check for drive availability
        if isAvailable(self.drive) > -1:
            print 'Drive letter is already in use'
            return -1

        #Check for network resource availability
        #if isAvailable(networkPath) == -1:
        #   print "Path not accessible: ", networkPath
        #   #Network path is not reachable
        #   return -1

        #Prepare 'NET USE' commands
        winCMD1 = 'NET USE ' + self.drive + ' ' + self.path
        winCMD2 = winCMD1 + ' ' + password + ' /User ' + user

        print "winCMD1 = ", winCMD1
        print "winCMD2 = ", winCMD2
        #Execute 'NET USE' command with authentication
        winCMD = winCMD2
        cmdOutPut = subprocess.Popen(winCMD, stdout=subprocess.PIPE, shell=True).communicate()
        print "Executed: ", winCMD
        if string.find(str(cmdOutPut), 'successfully',) == -1:
            print winCMD, " FAILED"
            winCMD = winCMD1
            #Execute 'NET USE' command without authentication, incase session already open
            cmdOutPut = subprocess.Popen(winCMD, stdout=subprocess.PIPE, shell=True).communicate()
            print "Executed: ", winCMD
            if string.find(str(cmdOutPut), 'successfully',) == -1:
                print winCMD, " FAILED"
                return -1
            #Mapped on second try
            return 1
        #Mapped with first try
        return 1

    def unmapNetworkDrive(drive):

        #Check if the drive is in use
        if isAvailable(drive) == -1:
            #Drive is not in use
            return -1

        #Prepare 'NET USE' command
        winCMD = 'net use ' + drive + ' /DELETE'
        cmdOutPut = subprocess.Popen(winCMD, stdout=subprocess.PIPE, shell=True).communicate()
        if string.find(str(cmdOutPut), 'successfully',) == -1:
            #Could not UN-MAP, this might be a physical drive
            return -1
        #UN-MAP successful
        return 1

def download_data():

    if sys.platform.startswith('linux') :
        subprocess.call(['xterm','-e','bash','data_download.sh'])
    elif sys.platform.startswith('win') :
        raise NotImplementedError()
    else :
        raise OSError('Platform ' + sys.platform + ' not supported')

def upload_data():
    if sys.platform.startswith('linux') :
        subprocess.call(['xterm','-e','bash','data_upload.sh'])
    elif sys.platform.startswith('win') :
        raise NotImplementedError()
    else :
        raise OSError('Platform ' + sys.platform + ' not supported')

if __name__=='__main__':
    #user = raw_input('User: ')
    #password = getpass.getpass('Passord: ')
    #mapper = WinHdMapper()
    #mapNetworkDrive(user, password)
    upload_data()