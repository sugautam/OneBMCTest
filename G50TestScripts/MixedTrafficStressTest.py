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

import datetime
import os
import threading
import time

import Config
import Helper
import RedFish
import Ssh
import UtilLogger
import base64


# Initialize global variables
fileName = os.path.basename(__file__)
threadLock = threading.Lock()
testPassOrFail = True
session = None
mixedTrafficfileName = None
theHostPath = None
localFilePath = None

# Setup Function
def Setup(interfaceParams):
    global fileName, mixedTrafficfileName, theHostPath, localFilePath
    
    mixedTrafficfileName = 'MixedTrafficStressTest.txt'
    theHostPath = Config.G50MixedTrafficStressHostFilePath + mixedTrafficfileName 
    localFilePath = os.getcwd() + "\\G50TestScripts\\" + mixedTrafficfileName
    
    return True

# Function will run single iteration of Mixed-Traffic Stress Test
def Execute(interfaceParams):
    global fileName, mixedTrafficfileName, theHostPath, localFilePath 
    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail
    global session

    # Define Test variables
    testPassOrFail = True
    threadDuration = Config.mixedTrafficStressTestThreadDuration # in seconds
    threads = []

    # Test will not be conducted for KCS interface
    if not interfaceParams:
        UtilLogger.verboseLogger.info("MixedTrafficStressTest.py: Currently using KCS interface. Will not run test.")
        return True

    # Test will not be conducted if local file does not exist
    if not os.path.isfile(localFilePath):
        UtilLogger.verboseLogger.error(fileName + ": file at local path " + localFilePath + " does not exist. Will not run test." )
        return False

    try:

        # Create new threads
        restThread = threading.Thread(name='restThread', target=runRestTest, args=(threadDuration, interfaceParams,))
        sftpThread = threading.Thread(name='sftpThread', target=runSftpTest, args=(threadDuration,))

        # Start threads
        UtilLogger.verboseLogger.info("MixedTrafficStressTest.py: starting restThread (REST) and sftpThread (SFTP)")
        restThread.start()
        sftpThread.start()

        # Add threads to thread list
        threads.append(restThread)
        threads.append(sftpThread)

        # Wait for all threads to complete
        for testThread in threads:
            testThread.join()

    except Exception, e:
        UtilLogger.verboseLogger.error("MixedTrafficStressTest.py: " + \
            " Test failed with exception - " + str(e))
        testPassOrFail = False

    return testPassOrFail

# Cleanup Function
def Cleanup(interfaceParams): 
    global testPassOrFail    
    return testPassOrFail

# Function will run REST commands
def runRestTest(duration, interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail
    global session
    
    # Initialize variables
    threadPassOrFail = True
    
    # run REST test
    startTime = time.time()
    totalTestTime = startTime + duration

    while time.time() < totalTestTime:

        # Define Test variables
        cmdPassOrFail = False
        response = None

        # Define request variables
            # Define request variables
    port = str(Config.httpRedfishPort)
    headers = {'Content-Type':'application/json'}
    auth = (Config.bmcUser, Config.bmcPassword)
    userPasswd = "%s:%s" %(Config.bmcUser, Config.bmcPassword)
    encoded = "Basic %s" %(base64.b64encode(userPasswd))
    headers.update({"Authorization":encoded})    
    host = Config.bmcIpAddress    
    
    try:
        # Send REST API and verify response
        getResource = 'redfish/v1/Chassis/System'
        cmdPassOrFail, response = RedFish.RestApiCall( session, host, getResource, "GET", auth, port, None, headers )
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("MixedTrafficStressTest.Execute:" + \
                " GET REST API for resource " + getResource + \
                " passed with status code " + str(response.status_code) + \
                " and response text: " + str(response.text))
        else:
            UtilLogger.verboseLogger.error("MixedTrafficStressTest.Execute:" + \
                " GET REST API for resource " + getResource + \
                " failed with status code " + str(response.status_code) + \
                " and response text: " + str(response.text))
        threadPassOrFail &= cmdPassOrFail

        if threadPassOrFail:
            UtilLogger.verboseLogger.info("MixedTrafficStressTest.runRestTest: runRestTest passed.")
        else:
            UtilLogger.verboseLogger.info("MixedTrafficStressTest.runRestTest: runRestTest failed.")

        # Update testPassOrFail
        threadLock.acquire()
        testPassOrFail &= threadPassOrFail
        threadLock.release()
    except Exception, e:
            UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))
            threadLock.acquire()
            testPassOrFail = False
            threadLock.release()
    return

def runSftpTest(duration):
    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail
    
    # Initialize variables
    threadPassOrFail = True

    # run Sftp test
    startTime = time.time()
    totalTestTime = startTime + duration

    try:
        while time.time() < totalTestTime:
            # Put file in target (host) file path
            sftpPassOrFail = Ssh.sftpPutFile( localFilePath, theHostPath, Config.bmcUser, Config.bmcPassword )
            if sftpPassOrFail:
                UtilLogger.verboseLogger.info("MixedTrafficStressTest.runSftpTest: successfully put file via Sftp.")
            else:
                UtilLogger.verboseLogger.error("MixedTrafficStressTest.runSftpTest: failed to put file via Sftp. Local path: " + localFilePath + ":  Host path: " + theHostPath )
            threadPassOrFail &= sftpPassOrFail

            # Remove file from target (host) file path
            sftpPassOrFail = Ssh.sftpRemoveFile( theHostPath, Config.bmcUser, Config.bmcPassword )
            if sftpPassOrFail:
                UtilLogger.verboseLogger.info("MixedTrafficStressTest.runSftpTest: successfully removed file via Sftp.")
            else:
                UtilLogger.verboseLogger.error("MixedTrafficStressTest.runSftpTest: failed to remove file via Sftp. Host path: " + Config.G50MixedTrafficStressHostFilePath )
            threadPassOrFail &= sftpPassOrFail

            # Sleep for 100 milliseconds
            time.sleep(0.1)

        if threadPassOrFail:
            UtilLogger.verboseLogger.info("MixedTrafficStressTest.runSftpTest: runSftpTest passed.")
        else:
            UtilLogger.verboseLogger.info("MixedTrafficStressTest.runSftpTest: runSftpTest failed.")            

        # Update testPassOrFail
        threadLock.acquire()
        testPassOrFail &= threadPassOrFail
        threadLock.release()
    except Exception, e:
            UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))            
            threadLock.acquire()
            testPassOrFail = False
            threadLock.release()
    return
