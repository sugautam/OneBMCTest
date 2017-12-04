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

    UtilLogger.verboseLogger.info("AddSelClearSelStressTest.py: running Setup fxn")

    return True

# Function will run stress test over Ipmi over LAN+ or KCS
# for adding and clearing SELs in BMC Flash
def Execute(interfaceParams):

    # Define Test variables
    testPassOrFail = True
    respData = []
    testName = 'AddSelClearSelStressTest'
    startTime = time.time()

    # total test time in seconds
    # total test time = 60 seconds/minute *
    #   60 minutes/hour * <totalTestTimeInHours>
    totalTestTime = startTime + 60 * 60 * \
        Config.addSelClearSelStressTestTotalTime
    
    try:
        if not interfaceParams:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.addSelClearSelStressTestTotalTime) + \
                "-hour Add Sel Clear Sel stress test for KCS")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.addSelClearSelStressTestTotalTime) + \
                "-hour Add Sel Clear Sel stress test for KCS")
        else:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.addSelClearSelStressTestTotalTime) + \
                "-hour Add Sel Clear Sel stress test for Ipmi over LAN+")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.addSelClearSelStressTestTotalTime) + \
                "-hour Add Sel Clear Sel stress test for Ipmi over LAN+")

        # Run test
        # Print Cycle # PASS/FAIL for every test cycle
        testCycle = 0
        cyclesPassed = 0
        cyclesFailed = 0
        while time.time() < totalTestTime:

            cyclePassOrFail = True

            # Add Sel Entries
            for selIdx in range(0, Config.addSelClearSelStressTestEntriesLimit):
                cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
                    interfaceParams, Config.netFnStorage,\
                    Config.cmdAddSelEntry,\
                        ['00', '00', '00', '00', '00', '00', '00', '00', \
                        '00', '00', '00', '00', '00', '00', '00', '00' ])
                if cmdPassOrFail:
                    UtilLogger.verboseLogger.info("AddSelEntry" + \
                        ": Command passed: " + str(respData) + \
                        ". Sel Entry: " + str(selIdx + 1))
                else:
                    UtilLogger.verboseLogger.error("AddSelEntry" + \
                        ": Command failed. Completion Code: " + str(respData) + \
                        ". Sel Entry: " + str(selIdx + 1))
                cyclePassOrFail &= cmdPassOrFail

            # Reserve Sel
            reservationId = []
            cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
                interfaceParams, Config.netFnStorage,\
                Config.cmdReserveSel, [])
            if cmdPassOrFail:
                UtilLogger.verboseLogger.info("ReserveSel" + \
                    ": Command passed: " + str(respData))
                reservationId = respData
            else:
                UtilLogger.verboseLogger.error("ReserveSel" + \
                    ": Command failed. Completion Code: " + \
                    str(respData))
            cyclePassOrFail &= cmdPassOrFail 

            # Define sample raw bytes for Clear Sel
            # Raw bytes defined as Initiate Erase
            rawBytesList = []
            for appendByte in reservationId:
                rawBytesList.append(appendByte)
            rawBytesList.append('43')
            rawBytesList.append('4C')
            rawBytesList.append('52')
            rawBytesList.append('AA')

            # Clear Sel
            cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
                interfaceParams, Config.netFnStorage,\
                Config.cmdClearSel,\
                rawBytesList)
            if cmdPassOrFail:
                UtilLogger.verboseLogger.info("ClearSel" + \
                    ": Command passed: " + str(respData))
            else:
                UtilLogger.verboseLogger.error("ClearSel" + \
                    ": Command failed. Completion Code: " + \
                    str(respData))

            # Verify test cycle
            if cyclePassOrFail:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " AddSelClearSelStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " AddSelClearSelStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                cyclesPassed += 1
            else:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " AddSelClearSelStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " AddSelClearSelStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                cyclesFailed += 1
            UtilLogger.verboseLogger.info("")
            testCycle += 1
            testPassOrFail &= cyclePassOrFail

        # Print Test Summary results
        endTime = time.time()
        if not interfaceParams:
            UtilLogger.consoleLogger.info(\
                "Add Sel Clear Sel over Kcs Stress Test Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
            UtilLogger.verboseLogger.info(\
                "Add Sel Clear Sel over Kcs Stress Test Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
        else:
            UtilLogger.consoleLogger.info(\
                "Add Sel Clear Sel over Ipmi over LAN+ Stress Test" + \
                " Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
            UtilLogger.verboseLogger.info(\
                "Add Sel Clear Sel over Ipmi over LAN+ Stress Test" + \
               " Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
    except Exception, e:
        UtilLogger.verboseLogger.info("AddSelClearSelStressTest.py: exception occurred - " + \
            str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    # Detect and Remove BMC Hang
    return Helper.DetectAndRemoveBmcHang(interfaceParams)