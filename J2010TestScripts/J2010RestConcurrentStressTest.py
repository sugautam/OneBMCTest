# OneBMCTest
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
threadLock = threading.Lock()
testPassOrFail = False
threads = []
threadsStats = [] # statistics for each REST thread
session = None

# Prototype Setup Function
def Setup(interfaceParams):
    
    # Declare module-scope variables
    global session, testPassOrFail
    return True

# Function will run single iteration of REST Concurrent Stress Test
def Execute(interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail
    global threads
    global threadsStats
    global session

    # Define Test variables
    testPassOrFail = True
    threadCount = Config.testThreadCount
    threadDuration = Config.testThreadDuration # in seconds
    UtilLogger.verboseLogger.info("J2010RestConcurrentStressTest.py: threadCount = %d" %(threadCount) )
    UtilLogger.verboseLogger.info("J2010RestConcurrentStressTest.py: threadDuration = %d" %(threadDuration) )

    try:
        # Check thread count is valid
        if threadCount < 1:
            threadCount = 1

        for threadIdx in range(0, threadCount):

            # Create new threads
            restThread = threading.Thread(name='restThread', target=runRestTest, args=(threadIdx, threadDuration, interfaceParams,))

            # Create thread statistics object and append to threadsStats
            restThreadStats = RestThreadStats(threadIdx)
            threadsStats.append(restThreadStats)

            # Add thread to threads list
            threads.append(restThread)

            # Start threads
            UtilLogger.verboseLogger.info("J2010RestConcurrentStressTest.py: starting " + "restThread with ID " + str(threadIdx + 1))
            restThread.start()

        # Wait for all threads to complete
        for testThread in threads:
            testThread.join()

        # Log Summary Statistics
        for threadStats in threadsStats:
            LogRestThreadStatistics(threadStats)

    except Exception, e:
        UtilLogger.verboseLogger.error("J2010RestConcurrentStressTest.py: " + \
            " Test failed with exception - " + str(e))
        testPassOrFail = False

    if( threadsStats == [] ):
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global testPassOrFail   
    return testPassOrFail
   
# Class holds statistics for instance of REST Thread ran
class RestThreadStats:

    # Initialize instance variables
    def __init__(self, idx):

        self.index = idx
        self.threadId = idx + 1
        self.threadPassOrFail = True
        self.commandsPassed = 0
        self.commandsFailed = 0
        self.threadDuration = None
        self.statDict = {'init' : 0}

        return

    # Update instance for a single command failure
    def UpdateFailureStats(self, command):

        # Update StatDict
        if command in self.statDict:
            self.statDict[command] += 1
        else:
            self.statDict[command] = 1

        # Update cmomandsFailed
        self.commandsFailed += 1

# Function will log thread statistics
def LogRestThreadStatistics(restThread):

    UtilLogger.verboseLogger.info("")

    # Log Summary
    UtilLogger.verboseLogger.info(\
        "REST THREAD " + str(restThread.threadId) + \
        " SUMMARY (J2010RestConcurrentStressTest) - " + \
        " Commands Run: " + str(restThread.commandsPassed + restThread.commandsFailed) + \
        " Commands Passed: " + str(restThread.commandsPassed) + \
        " Commands Failed: " + str(restThread.commandsFailed) + \
        " Rest Thread Duration: " + str(restThread.threadDuration))

    # Log tests that failed
    if restThread.commandsFailed > 0:
        UtilLogger.verboseLogger.info("===========================================")
        for failedTest, failedCount in restThread.statDict.iteritems():
            if failedTest is not 'init':
                UtilLogger.verboseLogger.info(failedTest + ": Failed " + \
                    str(failedCount) + " times")

    UtilLogger.verboseLogger.info("")

    return

# Function will run REST commands
def runRestTest(threadIdx, duration, interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail
    global threadsStats
    global session

    # Initialize variables
    threadPassOrFail = True
    threadStats = None
    UtilLogger.verboseLogger.info("Run REST Test in threads")
    # Get threadStats from threadsStats
    threadLock.acquire()
    threadStats = threadsStats[threadIdx]
    threadLock.release()
    
    # run REST test
    startTime = time.time()
    totalTestTime = startTime + duration

    port = str(Config.httpRedfishPort)
    headers = {'Content-Type':'application/json'}
    auth = (Config.bmcUser, Config.bmcPassword)
    userPasswd = "%s:%s" %(Config.bmcUser, Config.bmcPassword)
    encoded = "Basic %s" %(base64.b64encode(userPasswd))
    headers.update({"Authorization":encoded})  
    host = Config.bmcIpAddress
    timeout = 120

    try:
        while time.time() < totalTestTime:

            # Define request variables        
            getResource = 'redfish/v1/Chassis/System/MainBoard'

            # Send REST API and verify response
            cmdPassOrFail, response = RedFish.RestApiCall( session, host, getResource, "GET", auth, port, None, headers, timeout )
        
            if cmdPassOrFail:
                UtilLogger.verboseLogger.info("J2010RestConcurrentStressTest.Execute" + \
                    " (threadId " + str(threadStats.threadId) + "):" + \
                    " GET REST API for resource " + getResource + \
                    " passed with status code " + str(response.status_code) + \
                    " and response text: " + str(response.text))
                threadStats.commandsPassed += 1
            else:
                UtilLogger.verboseLogger.error("J2010RestConcurrentStressTest.Execute" + \
                    " (threadId " + str(threadStats.threadId) + "):" + \
                    " GET REST API for resource " + getResource + \
                    " failed with status code " + str(response.status_code) + \
                    " and response text: " + str(response.text))
                threadStats.UpdateFailureStats("get:" + getResource)
            threadStats.threadPassOrFail &= cmdPassOrFail

        if threadStats.threadPassOrFail:
            UtilLogger.verboseLogger.info("J2010RestConcurrentStressTest.runRestTest " + \
                "(thread ID " + str(threadStats.threadId) + "): " + \
                "runRestTest passed.")
        else:
            UtilLogger.verboseLogger.info("J2010RestConcurrentStressTest.runRestTest: " + \
                "(thread ID " + str(threadStats.threadId) + "): " + \
                "runRestTest failed.")

        # Calculate and update thread duration
        threadStats.threadDuration = datetime.timedelta(seconds=time.time() - startTime)

        # Update testPassOrFail and threadsStats
        threadLock.acquire()
        testPassOrFail &= threadStats.threadPassOrFail
        threadsStats[threadIdx] = threadStats
        threadLock.release()

    except Exception, e:
        UtilLogger.verboseLogger.info("J2010RestConcurrentStressTest.py: exception occurred - " + str(e))
        threadLock.acquire()
        testPassOrFail = False
        threadLock.release()

    return  testPassOrFail