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

import os
import paramiko
import time
import Config
import UtilLogger
import Helper

fileName = os.path.basename(__file__)
transferedBytes = 0 
totalBytes = 0

# Add sshResponseLimit and ssgResponseSize argument for VerifyReadingExpanderEventLog.py
def sshExecuteCommand( execCmds, connectAddress=Config.bmcIpAddress, username=Config.bmcUser, password=Config.bmcPassword, port = Config.sshPort , expectedOutput = [], regExpPattern = None, ResponseLimit=Config.sshResponseLimit, ResponseSize=2024, timeSleep = 3 ):
    global  fileName
    # Initialize variables
    execPassOrFail = True
    execCmdOutputs = []
    sshPort = port    
    sentBytes = 0
    parsedCmdOutputs = []      

    try:
        # Initialize SSH Client 
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect( connectAddress, sshPort, username, password, None, None, Config.sshTimeout )
        
        # Solve the problem: No handlers could be found for logger "paramiko.transport"
        paramiko.util.log_to_file('paramiko.log')

        # Invoke Shell (default terminal: vt100)
        channel = ssh.invoke_shell()            
        # For each command in execCmds,
        # execute command -> wait for response (or timeout) ->
        # read output buffer -> append command output   
        #      
        for execCmd in execCmds:
            if( expectedOutput != [] ):
                if( execCmd == '\n' ):
                    sentBytes = channel.send(execCmd)
                    continue
                parsedCmdOutputs = []                
                startTime1 = time.time()
                while (time.time() - startTime1 <= ResponseLimit) and (parsedCmdOutputs != expectedOutput):
                    sentBytes = channel.send(execCmd)
                    startTime2 = time.time()
                    while (time.time() - startTime2 <= ResponseLimit) and ( not channel.recv_ready() ):
                        time.sleep(2)                    
                    if not channel.recv_ready():
                        execPassOrFail = False
                        UtilLogger.verboseLogger.error("Ssh.sshExecuteCommand: failed to execute commands " + str(execCmds) + " via Ssh due to timeout")
                        execCmdOutputs = []
                        return execPassOrFail, execCmdOutputs, parsedCmdOutputs
            
                    response = channel.recv(ResponseSize)[sentBytes:]
                    execCmdOutputs.append(response)
                    if(execCmdOutputs != None ):
                        parsedCmdOutputs = Helper.regExpParser(execCmdOutputs[-1], regExpPattern, expectedOutput )
            else:
                sentBytes = channel.send(execCmd)
                startTime = time.time()
                while (time.time() - startTime <= ResponseLimit) and ( not channel.recv_ready() ):
                    if (execCmd == '\n' ):
                        time.sleep(0.5)
                    else:
                        time.sleep(timeSleep)             # Timeout is increased to 5 seconds because of the disk usage commands take long time to respond.
                if not channel.recv_ready():
                    execPassOrFail = False
                    UtilLogger.verboseLogger.error("Ssh.sshExecuteCommand: failed to execute commands " + str(execCmds) + " via Ssh due to timeout")
                    execCmdOutputs = []
                    return execPassOrFail, execCmdOutputs, parsedCmdOutputs
                
                response = channel.recv(ResponseSize)[sentBytes:]
                execCmdOutputs.append(response)                

        # Close transport
        ssh.close()
    
    except Exception, e:
        UtilLogger.verboseLogger.error("Ssh.sshExecuteCommand: " + \
            " failed to execute commands " + str(execCmds) + \
            " via Ssh due to exception: " + \
            str(e))
        execPassOrFail = False
        
    return execPassOrFail, execCmdOutputs, parsedCmdOutputs

# Function initializes and returns SSH Client
# Outputs:
#   openPassOrFail (bool): initialize SSH succeeded (True) or failed (False)
#   ssh (object): ssh client (default value: None)
def sshInit(username=Config.bmcUser, password=Config.bmcPassword):

    # Intiialize variables
    openPassOrFail = True
    ssh = None

    try:
        # Initialize SSH Client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect( Config.bmcIpAddress, Config.sshPort, username, password, None, None, Config.sshTimeout )
        #ssh.connect( Config.bmcIpAddress, Config.sshPort, username, password )

    except Exception, e:

        UtilLogger.verboseLogger.error("Ssh.sshInit: " + \
            " failed to initialize SSH client " + \
            " due to exception: " + \
            str(e))
        openPassOrFail = False

    return openPassOrFail, ssh

# Function closes SSH Client
# Outputs:
#   closePassOrFail (bool): close SSH succeeded (True) or failed (False)
def sshClose(ssh):

    # Initialize variables
    closePassOrFail = True

    try:

        # Close SSH Client
        ssh.close()

    except Exception, e:

        UtilLogger.verboseLogger.error("Ssh.sshClose: " + \
            " failed to close SSH client " + \
            " due to exception: " + \
            str(e))
        closePassOrFail = False

    return closePassOrFail

def callBackFunc( trBytes, totBytes ):
    global transferedBytes, totalBytes

    transferedBytes = trBytes
    totalBytes = totBytes

def sftpPutFile(localFilePath, hostFilePath, username=Config.bmcUser, password=Config.bmcPassword):
    global transferedBytes, totalBytes
    # Initialize variables
    transferedBytes = 0
    totalBytes     = os.path.getsize(localFilePath)
    putPassOrFail = True

    try:
        # Open a transport
        transport = paramiko.Transport((Config.bmcIpAddress, Config.sshPort))

        # Authorize transport
        transport.connect(username=username, password=password)

        # Send file to host file path
        sftp = paramiko.SFTPClient.from_transport(transport)               
        sftp.put(localFilePath, hostFilePath, callback = callBackFunc )

        if(transferedBytes != totalBytes ):
            putPassOrFail = False
            UtilLogger.verboseLogger.error( "SFTP PUT failed. Transfered %d bytes from total of %d" %(transferedBytes, totalBytes) )
        
        UtilLogger.verboseLogger.info( "SFTP PUT succeed. Transfered %d bytes from total of %d" %(transferedBytes, totalBytes) )

        # Close transport
        sftp.close()
        transport.close()

    except Exception, e:

        UtilLogger.verboseLogger.error("Sftp.putFile: " + \
            " unable to put file via Sftp due to exception: " + \
            str(e))
        putPassOrFail = False

    return putPassOrFail

def sftpGetFile(hostFilePath, localFilePath, username=Config.bmcUser, password=Config.bmcPassword):

    # Initialize variables
    getPassOrFail = True

    try:

        # Open a transport
        transport = paramiko.Transport((Config.bmcIpAddress, Config.sshPort))

        # Authorize transport
        transport.connect(username=username, password=password)

        # Get file from host file path
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(hostFilePath, localFilePath)

        # Close transport
        sftp.close()
        transport.close()

    except Exception, e:

        UtilLogger.verboseLogger.error("Sftp.getFile: " + \
            " unable to get file via Sftp due to exception: " + \
            str(e))
        getPassOrFail = False

    return getPassOrFail

def sftpRemoveFile(hostFilePath, username=Config.bmcUser, password=Config.bmcPassword):

    # Initialize variables
    removePassOrFail = True

    try:

        # Open a transport
        transport = paramiko.Transport((Config.bmcIpAddress, Config.sshPort))

        # Authorize transport
        transport.connect(username=username, password=password)

        # Remove file at host file path
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.remove(hostFilePath)

        # Close transport
        sftp.close()
        transport.close()

    except Exception, e:

        UtilLogger.verboseLogger.error("Sftp.removeFile: " + \
            " unable to remove file via Sftp due to exception: " + \
            str(e))
        removePassOrFail = False

    return removePassOrFail
