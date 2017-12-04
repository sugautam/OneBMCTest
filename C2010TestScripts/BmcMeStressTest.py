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
import time

import Config
import Helper
import IpmiUtil
import UtilLogger

# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info("BmcMeStressTest.py: running Setup fxn")

    return True

# Function will run 12-hour Bmc-Me stress test 
# for Ipmi over LAN+ and KCS
def Execute(interfaceParams):

    # Define Test variables
    testPassOrFail = True
    respData = []
    testName = 'BmcMeStressTest'
    startTime = time.time()

    # total test time in seconds
    # total test time = 60 seconds/minute *
    #   60 minutes/hour * <totalTestTimeInHours>
    totalTestTime = startTime + 60 * 60 * \
        Config.bmcMeStressTestTotalTime
    
    try:
        if not interfaceParams:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.bmcMeStressTestTotalTime) + \
                "-hour Bmc-Me stress test for KCS")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.bmcMeStressTestTotalTime) + \
                "-hour Bmc-Me stress test for KCS")
        else:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.bmcMeStressTestTotalTime) + \
                "-hour Bmc-Me stress test for Ipmi over LAN+")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.bmcMeStressTestTotalTime) + \
                "-hour Bmc-Me stress test for Ipmi over LAN+")

        # Run test
        # Print Cycle # PASS/FAIL for every test cycle
        testCycle = 0
        cyclesPassed = 0
        cyclesFailed = 0
        while time.time() < totalTestTime:

            cyclePassOrFail = True
            rawBytesList = []

            # Send Message: Get CPU and Memory Temperature
            cyclePassOrFail &= RetryCommand(\
                "Send Message (Get CPU and Memory Temperature)",\
                interfaceParams,\
                [ '00', '20', 'B8', '4B', '57', '01', '00', '03', \
                'FF', 'FF', 'FF', 'FF', '00', '00', '00', '00' ])

            # Send Message: Set NM Power Draw Range to 200 W max
            cyclePassOrFail &= RetryCommand(\
                "Send Message (Set NM Power Draw Range)",\
                interfaceParams,\
                [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
                '00', '00', 'C8', '00' ])

            # Send Message: Set Intel NM Parameter to enable Fast NM Limiting
            cyclePassOrFail &= RetryCommand(\
                "Send Message (Set Intel NM Parameter)",\
                interfaceParams,\
                [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
                '00', '00', '00', '00', '01', '00', '00', '00' ])

            # Send Message: Set NM Power Draw Range to max
            cyclePassOrFail &= RetryCommand(\
                "Send Message (Set NM Power Draw Range)",\
                interfaceParams,\
                [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
                '00', '00', 'FF', '7F' ])

            # Send Message: Set Intel NM Parameter to disable Fast NM Limiting
            cyclePassOrFail &= RetryCommand(\
                "Send Message (Set Intel NM Parameter)",\
                interfaceParams,\
                [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
                '00', '00', '00', '00', '00', '00', '00', '00' ])

            # Verify test cycle
            if cyclePassOrFail:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " BmcMeStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " BmcMeStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                cyclesPassed += 1
            else:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " BmcMeStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " BmcMeStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                cyclesFailed += 1
            UtilLogger.verboseLogger.info("")
            testCycle += 1
            testPassOrFail &= cyclePassOrFail

        # Print Test Summary results
        endTime = time.time()
        if not interfaceParams:
            UtilLogger.consoleLogger.info("Bmc-ME via Kcs Stress Test Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
            UtilLogger.verboseLogger.info("Bmc-ME via Kcs Stress Test Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
        else:
            UtilLogger.consoleLogger.info("Bmc-ME via Ipmi over LAN+ Stress Test" + \
                " Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
            UtilLogger.verboseLogger.info("Bmc-ME via Ipmi over LAN+ Stress Test" + \
               " Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
    except Exception, e:
        UtilLogger.verboseLogger.info("BmcMeStressTest.py: exception occurred - " + \
            str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    # Detect and Remove BMC Hang
    return Helper.DetectAndRemoveBmcHang(interfaceParams)

# Function will retry the BMC-ME command
# as defined in rawBytesList for 5 times
def RetryCommand(cmdName, interfaceParams, rawBytesList):

    # Retry max of 5 times
    retryMax = 5

    # Loop and check for either 
    # Success completion code or
    # Node Busy (0xC0)
    retryCount = 0
    sendMsgPassOrFail = False
    respData = []
    for retryCount in range(0, retryMax):

        sendMsgPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            rawBytesList)
        if sendMsgPassOrFail:
            break
        elif respData != 'c0':
            break
    
    # Verify results
    if sendMsgPassOrFail:
        UtilLogger.verboseLogger.info(\
            cmdName + \
            ": Command passed: " + str(respData) + \
            ". Retry count: " + str(retryCount))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed. Completion Code: " + \
            str(respData) + ". Retry count: " + \
            str(retryCount))

    return sendMsgPassOrFail