# PyTestUtil
#
# Copyright (c) Microsoft Corporation
#
# All rights reserved. 
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated documentation files (the ""Software""), 
# to deal in the Software without restriction, including without limitation the 
# rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice 
# shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import XmlParser
import Config
import RedFish
import UtilLogger
import Ssh
import os
import re

# Global variables
fileName = os.path.basename(__file__)
session = None
headers = None
auth = None
testPassOrFail = True

# Setup Function
def Setup(interfaceParams):
    global fileName, session, headers, auth, testPassOrFail
    
    UtilLogger.verboseLogger.info("%s: running Setup fxn" %(fileName))

    return True

# Function will test completion code for GPIO Registers
def Execute(interfaceParams):
    global testPassOrFail
    # The list of directories/folders to monitor for disk usage
    foldersToMonitor = Config.foldersToMonitor

    # Define Test variables
    testPassOrFail = True

    # Get Disk Usage for the specified directories
    for dir in foldersToMonitor:
        testPassOrFail &= GetFileSystemUsage(dir)

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global testPassOrFail, fileName
    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))

    return testPassOrFail

def GetFileSystemUsage(dir):
    global testPassOrFail
    # Define Test variables
    fs = None
    totalBlocks = None
    blocksUsed = None
    blocksAvailable = None
    percentInUse = None
    mountedOn = None
    dfOutput = []
    sshOutput = []
    threshold = Config.folderThresholdPercent       # In percent
    username = Config.bmcUser
    password = Config.bmcPassword

    execCmds = ['\n']                      
    execCmds.append("df -k %s\n" %(dir))
    
    try:
        # Get Filesystem usage
        expected = str(dir.split('/')[1])
        regexPattern = r"([\w+]+)"
        (execPassOrFail, sshOutputs, parsedCmdOutputs) = Ssh.sshExecuteCommand(execCmds, username, password, expectedOutput = expected, regExpPattern = regexPattern )
    
        if (not execPassOrFail):
            UtilLogger.verboseLogger.error( "%s: command = \"df -k %s\" failed to get file system usage on '%s'" %(fileName, dir, dir) )
            execPassOrFail &= False
            return(execPassOrFail)
        
        """
        Sample df response
        Filesystem     1K-blocks     Used Available Use% Mounted on
        /dev/sda1       94822236 87277364   2705156  97% /
        """
        
        # Parse dk response
        sshOutput = sshOutputs[-1]
        header = sshOutput.split('\r')[0].split()
        dfOutput = sshOutput.split('\r')[1].split()

        if  ( len(sshOutputs) >= 2 ):
            sshOutput = sshOutputs[1]
            header = sshOutput.split('\r')[0].split()
            dfOutput = sshOutput.split('\r')[1].split()

        if ( len(dfOutput) >= 6 ):
            fs = dfOutput[0]
            totalBlocks = dfOutput[1]
            blocksUsed = dfOutput[2]
            blocksAvailable = dfOutput[3]
            percentInUse = dfOutput[4].replace('%', '')
            mountedOn = dfOutput[5]
        else:
            UtilLogger.verboseLogger.error( "%s: failed to parse file system usage on '%s, len(sshOutputs) = %d'\n sshOutputs = %s" %(fileName, dir, len(sshOutputs), str(sshOutputs) ) )
            execPassOrFail = False
            return  (execPassOrFail)

        execCmds = ['\n']                  
        execCmds.append("du -s %s\n" %(dir))

        # Get Filesystem usage
        (execPassOrFail, sshOutputs, parsedCmdOutputs) = Ssh.sshExecuteCommand(execCmds, username, password, expectedOutput = expected, regExpPattern = regexPattern )

        if (not execPassOrFail):            
            UtilLogger.verboseLogger.error( "%s: command = \"du -s %s\" failed to get disk usage on '%s'" %(fileName, dir, dir) )
            execPassOrFail = False
            return  (execPassOrFail)

        """
        Sample du response

        999999 .
        """

        # Parse du response
        directory = None
        blocks = None        
        sshOutput = sshOutputs[-1]
        duOutput = sshOutput.split('\r')[0].split()
        
        if len(duOutput):
            blocks = duOutput[0]
            directory = duOutput[1]
        else:
            UtilLogger.verboseLogger.error("%s: failed to parse disk usage on '%s'. len(duOutput) = %d\n sshOutputs = %s" %(fileName, dir, len(duOutput), str(sshOutputs)))
            execPassOrFail &= False
            return(execPassOrFail)

        UtilLogger.verboseLogger.info("%s: FileSystem: %-20s  Mount: %-20s  InUse: %2d%%  Blocks: %s" %(fileName, fs, mountedOn, int(percentInUse), blocks))

        # Verify if the threshold has been exceeded
        if ( int(percentInUse) >= threshold) :
            UtilLogger.verboseLogger.error("%s: Directory '%s' disk usage of %s%% exceeds threshold of %s%%" %(fileName, directory, percentInUse, threshold))
            execPassOrFail = False

    except Exception, e:
        UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))
        testPassOrFail = False

    return(execPassOrFail)
