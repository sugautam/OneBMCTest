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
import random
import threading
import time

import AcPowerIpSwitch
import Config
import Helper
import IpmiUtil
import Psu
import Ssh
import UtilLogger

# Initialize global variables
threadLock = threading.Lock()
testPassOrFail = True
bootInProgress = False

# Prototype Setup Function
def Setup(interfaceParams):

    # Get Sel entries
    processCmd = ['sel', '-u']
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)
    out, err = IpmiUtil.RunIpmiUtil(processCmd)
    if err:
        UtilLogger.verboseLogger.error("AcCycleAddSelClearSelStressTest: " + \
            "setup SEL entries error: " + str(err))
        setupSuccess = False
    else:
        UtilLogger.verboseLogger.info("AcCycleAddSelClearSelStressTest: " + \
            "setup SEL entries: \n" + str(out))

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
    
    return True

# Function will run AC Cycle Add SEL Clear SEL Stress Test
def Execute(interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail

    # Define Test variables
    testPassOrFail = True
    threadDuration = Config.acCycleAddSelClearSelStressTestTotalTime # in seconds
    threads = []

    # Test will not be conducted for KCS interface
    if not interfaceParams:
        UtilLogger.verboseLogger.info(\
            "AcCycleAddSelClearSelStressTest: Currently using KCS interface. " + \
            "Will not run test.")
        return True

    try:

        # Create new threads
        addSelClearSelThread = threading.Thread(name='runAddSelClearSelTest', \
            target=runAddSelClearSelTest, \
            args=(threadDuration, interfaceParams,))
        acCycleThread = threading.Thread(name='runAcCycleTest', target=runAcCycleTest, \
            args=(threadDuration,interfaceParams,))

        # Start threads
        UtilLogger.verboseLogger.info("AcCycleAddSelClearSelStressTest: starting " + \
            "ipmiThread (Ipmi over LAN+) and sftpThread (SFTP)")
        addSelClearSelThread.start()
        acCycleThread.start()

        # Add threads to thread list
        threads.append(addSelClearSelThread)
        threads.append(acCycleThread)

        # Wait for all threads to complete
        for testThread in threads:
            testThread.join()

    except Exception, e:
        UtilLogger.verboseLogger.error("AcCycleAddSelClearSelStressTest: " + \
            " Test failed with exception - " + str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    cleanupSuccess = False

    # Enable PSU battery
    cleanupSuccess = Psu.EnableDisablePsuBattery(interfaceParams, True)

    # Get Sel entries
    processCmd = ['sel', '-u']
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)
    out, err = IpmiUtil.RunIpmiUtil(processCmd)
    if err:
        UtilLogger.verboseLogger.error("AcCycleAddSelClearSelStressTest: " + \
            "setup SEL entries error: " + str(err))
    else:
        UtilLogger.verboseLogger.info("AcCycleAddSelClearSelStressTest: " + \
            "setup SEL entries: \n" + str(out))
        cleanupSuccess = True

    # Detect and Remove BMC Hang
    return Helper.DetectAndRemoveBmcHang(interfaceParams)

# Function will run Ipmi over LAN+ commands
def runAddSelClearSelTest(duration, interfaceParams):

    # Declare Module-Scope variables
    global bootInProgress
    global threadLock
    global testPassOrFail

    # Initialize variables
    threadPassOrFail = True
    
    # run Ipmi over LAN+ test
    startTime = time.time()
    totalTestTime = startTime + duration*60*60 # in seconds

    while time.time() < totalTestTime:

        cyclePassOrFail = True

        # Initial record ID returned for Add Sel Entry after Clear SEL
        expectedRecordId = 2 

        # Add Sel Entries (assume SELs were cleared by runAcCycle thread)
        for selIdx in range(0, Config.addSelClearSelStressTestEntriesLimit):
            cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
                interfaceParams, Config.netFnStorage,\
                Config.cmdAddSelEntry,\
                    ['00', '00', '00', '00', '00', '00', '00', '00', \
                    '00', '00', '00', '00', '00', '00', '00', '00' ])
            if cmdPassOrFail:
                if int(respData[1]+respData[0], 16) == expectedRecordId:
                    UtilLogger.verboseLogger.info("AddSelEntry" + \
                        ": Command passed: " + str(respData) + \
                        ". Sel entry matches expected Record Id. " + \
                        "Sel Entry: " + str(expectedRecordId))
                else:
                    UtilLogger.verboseLogger.error("AddSelEntry" + \
                        ": Command response: " + str(respData) + \
                        " failed to get expected Sel record ID." + \
                        " Expected Sel Entry: " + str(expectedRecordId) + \
                        " Actual Sel Entry: " + str(int(respData[1]+respData[0], 16)))
                    cmdPassOrFail = False
                expectedRecordId += 1
            else:
                UtilLogger.verboseLogger.error("AddSelEntry" + \
                    ": Command failed. Completion Code: " + str(respData) + \
                    ". Sel Entry: " + str(expectedRecordId))
            if expectedRecordId == Config.maxNumberOfSels:
                expectedRecordId = 1 # Sel Record ID resets to 1 after SEL rollover
            cyclePassOrFail &= cmdPassOrFail

            # Check for AC cycling process
            bootTimeoutStartTime = time.time()
            threadLock.acquire()
            checkBootInProgress = bootInProgress
            threadLock.release()
            while checkBootInProgress and ((time.time() - bootTimeoutStartTime) < \
                Config.acCycleAddSelClearSelStressTestBootProcessTimeout):
                threadLock.acquire()
                checkBootInProgress = bootInProgress
                threadLock.release()
                expectedRecordId = 2
                time.sleep(0.1)

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

        threadPassOrFail &= cyclePassOrFail

    if threadPassOrFail:
        UtilLogger.verboseLogger.info(\
            "AcCycleAddSelClearSelStressTest.runAddSelClearSelTest: " + \
            "runAddSelClearSelTest passed.")
    else:
        UtilLogger.verboseLogger.info(\
            "AcCycleAddSelClearSelStressTest.runAddSelClearSelTest: " + \
            "runAddSelClearSelTest failed.")

    # Update testPassOrFail
    threadLock.acquire()
    testPassOrFail &= threadPassOrFail
    threadLock.release()

    return

def runAcCycleTest(duration, interfaceParams):

    # Declare Module-Scope variables
    global bootInProgress
    global threadLock
    global testPassOrFail

    # Initialize variables
    threadPassOrFail = True

    # run Sftp test
    startTime = time.time()
    totalTestTime = startTime + duration*60*60

    while time.time() < totalTestTime:

        cyclePassOrFail = True

        # generate random number in range to sleep
        randSleep = random.randint(\
            Config.acCycleAddSelClearSelStressTestRandRange[0], \
            Config.acCycleAddSelClearSelStressTestRandRange[1])
        UtilLogger.verboseLogger.info(\
            "AcCycleAddSelClearSelStressTest.runAcCycleTest: " + \
            "sleeping for " + str(randSleep) + " seconds..")
        time.sleep(randSleep)

        # Indicate that blade boot-up process in progress
        threadLock.acquire()
        bootInProgress = True
        threadLock.release()

        # Disable PSU battery
        cyclePassOrFail &= Psu.EnableDisablePsuBattery(interfaceParams, False)

        # Power Down Server Blade
        powerPassOrFail, response = AcPowerIpSwitch.SetPowerOnOff(\
            Config.acPowerIpSwitchOutlet, 0)
        if powerPassOrFail:
            UtilLogger.verboseLogger.info(\
                "AcCycleAddSelClearSelStressTest.runAcCycleTest: " + \
                "Server blade powered down.")
        else:
            UtilLogger.verboseLogger.error(\
                "AcCycleAddSelClearSelStressTest.runAcCycleTest: " + \
                "Failed to power down server blade.")
        cyclePassOrFail &= powerPassOrFail

        # Sleep
        UtilLogger.verboseLogger.info(\
            "AcCycleAddSelClearSelStressTest.runAcCycleTest: " + \
            "Sleeping for " + str(Config.acPowerOffSleepInSeconds) + " seconds.")
        time.sleep(Config.acPowerOffSleepInSeconds)

        # Power Up Server Blade
        powerPassOrFail, response = AcPowerIpSwitch.SetPowerOnOff(\
            Config.acPowerIpSwitchOutlet, 1)
        if powerPassOrFail:
            UtilLogger.verboseLogger.info(\
                "AcCycleAddSelClearSelStressTest.runAcCycleTest: " + \
                "Server blade powered up.")
        else:
            UtilLogger.verboseLogger.error(\
                "AcCycleAddSelClearSelStressTest.runAcCycleTest: " + \
                "Failed to power up server blade.")
        cyclePassOrFail &= powerPassOrFail

        # Check for ping
        # Ping BMC until it responds
        pingPassOrFail, decompEndTime = Helper.PingAndCheckResponse(\
            Config.acPowerOnSleepInSeconds, Config.bmcIpAddress)
        cyclePassOrFail &= pingPassOrFail

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
        cyclePassOrFail &= cmdPassOrFail

        # Indicate that blade boot-up process in progress
        threadLock.acquire()
        bootInProgress = False
        threadLock.release()

        threadPassOrFail &= cyclePassOrFail

    if threadPassOrFail:
        UtilLogger.verboseLogger.info(\
            "AcCycleAddSelClearSelStressTest.runAcCycleTest: " + \
            "runSftpTest passed.")
    else:
        UtilLogger.verboseLogger.info(\
            "AcCycleAddSelClearSelStressTest.runAcCycleTest: " + \
            "runSftpTest failed.")

    # Update testPassOrFail
    threadLock.acquire()
    testPassOrFail &= threadPassOrFail
    threadLock.release()

    return