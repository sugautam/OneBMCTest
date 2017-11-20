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
import time

import Config
import Helper
import IpmiUtil
import UtilLogger

# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info("BmcDcmiStressTest: running Setup fxn")

    return True

# Function will run BMC DCMI stress test 
# for Ipmi over LAN+ and KCS
def Execute(interfaceParams):

    # Define Test variables
    testPassOrFail = True
    respData = []
    testName = 'BmcDcmiStressTest'
    startTime = time.time()

    # total test time in seconds
    # total test time = 60 seconds/minute *
    #   60 minutes/hour * <totalTestTimeInHours>
    totalTestTime = startTime + 60 * 60 * \
        Config.bmcDcmiStressTestTotalTime
    
    try:
        if not interfaceParams:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.bmcMeStressTestTotalTime) + \
                "-hour BMC DCMI stress test for KCS " + \
                "with polling rate " + \
                str(Config.bmcDcmiStressTestPollTime) + " second(s)")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.bmcMeStressTestTotalTime) + \
                "-hour BMC DCMI stress test for KCS" + \
                "with polling rate " + \
                str(Config.bmcDcmiStressTestPollTime) + " second(s)")
        else:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.bmcMeStressTestTotalTime) + \
                "-hour BMC DCMI stress test for Ipmi over LAN+" + \
                "with polling rate " + \
                str(Config.bmcDcmiStressTestPollTime) + " second(s)")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.bmcMeStressTestTotalTime) + \
                "-hour BMC DCMI stress test for Ipmi over LAN+" + \
                "with polling rate " + \
                str(Config.bmcDcmiStressTestPollTime) + " second(s)")

        # Run test
        # Print Cycle # PASS/FAIL for every test cycle
        testCycle = 0
        cyclesPassed = 0
        cyclesFailed = 0
        while time.time() < totalTestTime:

            cyclePassOrFail = True
            rawBytesList = []

            # Get Power Limit
            cmdPassOrFail, respData = RetryCommand(\
                "Get Power Limit", interfaceParams, Config.netFnDcmi, \
                Config.cmdGetPowerLimit, [ 'DC', '00', '00' ])
            if not cmdPassOrFail and respData == '80':
                UtilLogger.verboseLogger.info("Get Power Limit:" + \
                    "Command passed. 0x80 completion code expected")
                cmdPassOrFail = True
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

            # Activate Power Limit
            cmdPassOrFail, respData = RetryCommand(\
                "Activate Power Limit", interfaceParams, Config.netFnDcmi, \
                Config.cmdActivatePowerLimit, [ 'DC', '01', '00', '00' ])
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

            # Get Power Limit
            cmdPassOrFail, respData = RetryCommand(\
                "Get Power Limit", interfaceParams, Config.netFnDcmi, \
                Config.cmdGetPowerLimit, [ 'DC', '00', '00' ])
            if cmdPassOrFail:
                if not (respData[4:6] == [ 'f4', '01' ]):
                    UtilLogger.verboseLogger.error("Get Power Limit:" + \
                        " command failed. Expected response[4:6] with " + \
                        " 500 W. Actual: " + str(int(respData[5]+respData[4], 16)))
                    cmdPassOrFail = False
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

            # De-activate Power Limit
            cmdPassOrFail, respData = RetryCommand(\
                "De-activate Power Limit", interfaceParams, Config.netFnDcmi, \
                Config.cmdActivatePowerLimit, [ 'DC', '00', '00', '00' ])
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

            # Set Power Limit (300 W)
            cmdPassOrFail, respData = RetryCommand(\
                "Set Power Limit (300 W)", interfaceParams, Config.netFnDcmi, \
                Config.cmdSetPowerLimit, \
                [ 'DC', '00', '00', '00', '00', '2C', '01', '70', \
                '17', '00', '00', '00', '00', '01', '00' ])
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

            # Get Power Limit
            cmdPassOrFail, respData = RetryCommand(\
                "Get Power Limit", interfaceParams, Config.netFnDcmi, \
                Config.cmdGetPowerLimit, [ 'DC', '00', '00' ])
            if not cmdPassOrFail and respData == '80':
                UtilLogger.verboseLogger.info("Get Power Limit:" + \
                    "Command passed. 0x80 completion code expected")
                cmdPassOrFail = True
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

            # Activate Power Limit
            cmdPassOrFail, respData = RetryCommand(\
                "Activate Power Limit", interfaceParams, Config.netFnDcmi, \
                Config.cmdActivatePowerLimit, [ 'DC', '01', '00', '00' ])
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

            # Get Power Limit
            cmdPassOrFail, respData = RetryCommand(\
                "Get Power Limit", interfaceParams, Config.netFnDcmi, \
                Config.cmdGetPowerLimit, [ 'DC', '00', '00' ])
            if cmdPassOrFail:
                if not (respData[4:6] == [ '2c', '01' ]):
                    UtilLogger.verboseLogger.error("Get Power Limit:" + \
                        " command failed. Expected response[4:6] with " + \
                        " 300 W. Actual: " + str(int(respData[5]+respData[4], 16)))
                    cmdPassOrFail = False
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

            # De-activate Power Limit
            cmdPassOrFail, respData = RetryCommand(\
                "De-activate Power Limit", interfaceParams, Config.netFnDcmi, \
                Config.cmdActivatePowerLimit, [ 'DC', '00', '00', '00' ])
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

            # Get Power Limit
            cmdPassOrFail, respData = RetryCommand(\
                "Get Power Limit", interfaceParams, Config.netFnDcmi, \
                Config.cmdGetPowerLimit, [ 'DC', '00', '00' ])
            if not cmdPassOrFail and respData == '80':
                UtilLogger.verboseLogger.info("Get Power Limit:" + \
                    "Command passed. 0x80 completion code expected")
                cmdPassOrFail = True
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

            # Set Power Limit (500 W)
            cmdPassOrFail, respData = RetryCommand(\
                "Set Power Limit (500 W)", interfaceParams, Config.netFnDcmi, \
                Config.cmdSetPowerLimit, \
                [ 'DC', '00', '00', '00', '00', 'F4', '01', '70', \
                '17', '00', '00', '00', '00', '01', '00' ])
            cyclePassOrFail &= cmdPassOrFail

            time.sleep(Config.bmcDcmiStressTestPollTime)

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
            UtilLogger.consoleLogger.info("BMC DCMI Stress Test via KCS Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
            UtilLogger.verboseLogger.info("BMC DCMI Stress Test via KCS Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
        else:
            UtilLogger.consoleLogger.info("Bmc DCMI Stress Test via Ipmi over LAN+" + \
                " Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
            UtilLogger.verboseLogger.info("Bmc DCMI Stress Test via Ipmi over LAN+" + \
               " Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
    except Exception, e:
        UtilLogger.verboseLogger.info("BmcDcmiStressTest: exception occurred - " + \
            str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    # Detect and Remove BMC Hang
    return Helper.DetectAndRemoveBmcHang(interfaceParams)

# Function will retry the BMC-ME command
# as defined in rawBytesList for 5 times
def RetryCommand(cmdName, interfaceParams, netfn, cmdNum, rawBytesList):

    # Retry max of 5 times
    retryMax = 5

    # Loop and check for either 
    # Success completion code or
    # Node Busy (0xC0)
    retryCount = 0
    cmdPassOrFail = False
    respData = []
    for retryCount in range(0, retryMax):

        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
            netfn, cmdNum, rawBytesList)
        if cmdPassOrFail and respData != 'c0':
            break
        elif not cmdPassOrFail:
            break
    
    # Verify results
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(\
            cmdName + \
            ": Command passed: " + str(respData) + \
            ". Retry count: " + str(retryCount))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed. Completion Code: " + \
            str(respData) + ". Retry count: " + \
            str(retryCount))

    return cmdPassOrFail, respData