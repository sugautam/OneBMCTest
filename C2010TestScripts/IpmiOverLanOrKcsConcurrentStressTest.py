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
import IpmiUtil
import Ssh
import UtilLogger

# Initialize global variables
threadLock = threading.Lock()
testPassOrFail = True
threads = []
threadsStats = [] # statistics for each ipmi thread

# Prototype Setup Function
def Setup(interfaceParams):

    # Get Sel entries
    processCmd = ['sel', '-u']
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)
    out, err = IpmiUtil.RunIpmiUtil(processCmd)
    if err:
        UtilLogger.verboseLogger.error("IpmiOverLanOrKcsConcurrentStressTest.py: " + \
            "setup SEL entries error: " + str(err))
        setupSuccess = False
    else:
        UtilLogger.verboseLogger.info("IpmiOverLanOrKcsConcurrentStressTest.py: " + \
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

# Function will run single iteration of Ipmi Over LAN+ Concurrent Stress Test
def Execute(interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail
    global threads
    global threadsStats

    # Define Test variables
    testPassOrFail = True
    threadCount = Config.ipmiOverLanConcurrentThreadCount
    threadDuration = Config.ipmiOverLanConcurrentThreadDuration # in seconds

    try:

        # Check thread count is valid
        if threadCount < 1:
            threadCount = 1

        for threadIdx in range(0, threadCount):

            # Create new threads
            ipmiThread = threading.Thread(name='ipmiThread', target=runIpmiTest, \
                args=(threadIdx, threadDuration, interfaceParams,))

            # Create thread statistics object and append to threadsStats
            ipmiThreadStats = IpmiThreadStats(threadIdx)
            threadsStats.append(ipmiThreadStats)

            # Add thread to threads list
            threads.append(ipmiThread)

            # Start threads
            UtilLogger.verboseLogger.info("IpmiOverLanOrKcsConcurrentStressTest.py: starting " + \
                "ipmiThread (Ipmi over LAN+) with ID " + str(threadIdx + 1))
            ipmiThread.start()

        # Wait for all threads to complete
        for testThread in threads:
            testThread.join()

        # Log Summary Statistics
        for threadStats in threadsStats:
            LogIpmiThreadStatistics(threadStats)

    except Exception, e:
        UtilLogger.verboseLogger.error("IpmiOverLanOrKcsConcurrentStressTest.py: " + \
            " Test failed with exception - " + str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    cleanupSuccess = False

    # Get Sel entries
    processCmd = ['sel', '-u']
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)
    out, err = IpmiUtil.RunIpmiUtil(processCmd)
    if err:
        UtilLogger.verboseLogger.error("IpmiOverLanOrKcsConcurrentStressTest.py: " + \
            "setup SEL entries error: " + str(err))
    else:
        UtilLogger.verboseLogger.info("IpmiOverLanOrKcsConcurrentStressTest.py: " + \
            "setup SEL entries: \n" + str(out))
        cleanupSuccess = True

    # Detect and Remove BMC Hang
    return Helper.DetectAndRemoveBmcHang(interfaceParams)

# Class holds statistics for instance of Ipmi Thread ran
class IpmiThreadStats:

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
def LogIpmiThreadStatistics(ipmiThread):

    UtilLogger.verboseLogger.info("")

    # Log Summary
    UtilLogger.verboseLogger.info(\
        "IPMI THREAD " + str(ipmiThread.threadId) + \
        " SUMMARY (IpmiOverLanOrKcsConcurrentStressTest) - " + \
        " Commands Run: " + str(ipmiThread.commandsPassed + ipmiThread.commandsFailed) + \
        " Commands Passed: " + str(ipmiThread.commandsPassed) + \
        " Commands Failed: " + str(ipmiThread.commandsFailed) + \
        " Ipmi Thread Duration: " + str(ipmiThread.threadDuration))

    # Log tests that failed
    if ipmiThread.commandsFailed > 0:
        UtilLogger.verboseLogger.info(\
            "===========================================")
        for failedTest, failedCount in ipmiThread.statDict.iteritems():
            if failedTest is not 'init':
                UtilLogger.verboseLogger.info(failedTest + ": Failed " + \
                    str(failedCount) + " times")

    UtilLogger.verboseLogger.info("")

    return

# Function will run Ipmi over LAN+ commands
def runIpmiTest(threadIdx, duration, interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail
    global threadsStats

    # Initialize variables
    threadPassOrFail = True
    threadStats = None

    # Get threadStats from threadsStats
    threadLock.acquire()
    threadStats = threadsStats[threadIdx]
    threadLock.release()
    

    # run Ipmi over LAN+ test
    startTime = time.time()
    totalTestTime = startTime + duration

    while time.time() < totalTestTime:

        # Get Device Id
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnApp,
            Config.cmdGetDeviceId, [])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetDeviceId" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed: " + str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error("GetDeviceId" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed. Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("GetDeviceId")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Get Sdr
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdGetSdr, [ '00', '00', '00', '00', '00', 'FF' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetSdr" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed: " + str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error("GetSdr" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed. Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("GetSdr")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Read Fru Data
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdReadFruData, [ '00', '00', '00', '08' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("ReadFruData" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed: " + str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error("ReadFruData" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed. Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("ReadFruData")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Get Power Reading
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnDcmi,\
            Config.cmdGetPowerReading, [ 'DC', '01', '01', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetPowerReading" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed: " + str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error("GetPowerReading" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed. Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("GetPowerReading")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Set Next Boot to BIOS Setup
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '18', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed for set next boot to Bios Setup: " + \
                str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed for set next boot to Bios Setup." + \
                " Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("SetSystemBootOptions.BiosSetup")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Set Next Boot to EFI
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '00', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed for set next boot to EFI: " + \
                str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed for set next boot to EFI." + \
                " Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("SetSystemBootOptions.EFI")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Set Next Boot to PXE
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '04', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed for set next boot to PXE: " + \
                str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed for set next boot to PXE." + \
                " Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("SetSystemBootOptions.PXE")
        threadStats.threadPassOrFail &= cmdPassOrFail
            
        # Set Next Boot to Hard Disk
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '08', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed for set next boot to Hard Disk: " + \
                str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed for set next boot to Hard Disk." + \
                " Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("SetSystemBootOptions.HDD")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Get Sel Entry
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdGetSelEntry, [ '00', '00', '00', '00', '00', 'FF' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetSelEntry" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed: " + str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error("GetSelEntry" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed. Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("GetSelEntry")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Get Processor Info
        cmdPassOrFail = True
        for idx in range(0, 2):
            # Set rawByte to cpu index
            cpuIdx = hex(idx).lstrip('0x')
            if idx == 0:
                cpuIdx = '0'
            # Send raw bytes via IpmiUtil
            cpuPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
                Config.netFnOem30, Config.cmdGetProcessorInfo, [ cpuIdx ])
            if cpuPassOrFail:
                UtilLogger.verboseLogger.info("GetProcessorInfo" + \
                    " (threadId " + str(threadStats.threadId) + ")" + \
                    ": Command passed for cpu 0x"\
                    + cpuIdx + ": " + str(respData))
                threadStats.commandsPassed += 1
            else:
                UtilLogger.verboseLogger.error("GetProcessorInfo" + \
                    " (threadId " + str(threadStats.threadId) + ")" + \
                    ": Command failed for cpu 0x" + cpuIdx + \
                    ". Completion Code: " + str(respData))
                threadStats.UpdateFailureStats("GetProcessorInfo")
            cmdPassOrFail &= cpuPassOrFail
        threadStats.threadPassOrFail &= cpuPassOrFail

        # Get Memory Info
        cmdPassOrFail = True
        for idx in range(0, 25):
            # Set rawByte to memory index
            dimmIdx = hex(idx).lstrip('0x')
            if idx == 0:
                dimmIdx = '0'
            dimmPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
                Config.netFnOem30, Config.cmdGetMemoryInfo, [ dimmIdx ])
            if dimmPassOrFail:
                UtilLogger.verboseLogger.info("GetMemoryInfo" + \
                    " (threadId " + str(threadStats.threadId) + ")" + \
                    ": Command passed for dimm 0x"\
                    + dimmIdx + ": " + str(respData))
                threadStats.commandsPassed += 1
            else:
                UtilLogger.verboseLogger.error("GetMemoryInfo" + \
                    " (threadId " + str(threadStats.threadId) + ")" + \
                    ": Command failed for dimm 0x" + dimmIdx + \
                    ". Completion Code: " + str(respData))
                threadStats.UpdateFailureStats("GetMemoryInfo")
            cmdPassOrFail &= dimmPassOrFail
        threadStats.threadPassOrFail &= dimmPassOrFail

        # Get Pcie Info
        for idx in range(0, 22):
            pcieIdx = hex(idx).lstrip('0x')
            if idx == 0:
                pcieIdx = '0'
            pciePassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
                Config.netFnOem30, Config.cmdGetPcieInfo, [ pcieIdx ])
            if pciePassOrFail:
                UtilLogger.verboseLogger.info("GetPcieInfo" + \
                    " (threadId " + str(threadStats.threadId) + ")" + \
                    ": Command passed for pcie 0x"\
                    + pcieIdx + ": " + str(respData))
                threadStats.commandsPassed += 1
            else:
                UtilLogger.verboseLogger.error("GetPcieInfo" + \
                    " (threadId " + str(threadStats.threadId) + ")" + \
                    ": Command failed for pcie 0x" + pcieIdx + \
                    ". Completion Code: " + str(respData))
                threadStats.UpdateFailureStats("GetPcieInfo")
            cmdPassOrFail &= pciePassOrFail
        threadStats.threadPassOrFail &= pciePassOrFail

        # Get Nic Info
        threadStats.threadPassOrFail &= IpmiUtil.VerifyGetNicInfo(interfaceParams)

        # Send Message: Get CPU and Memory Temperature
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', '4B', '57', '01', '00', '03', \
            'FF', 'FF', 'FF', 'FF', '00', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Get CPU and Memory Temperature)" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed: " + str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Get CPU and Memory Temerature)" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed. Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("Send Message (Get CPU and Memory Temperature)")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Send Message: Set NM Power Draw Range to 200 W max
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
            '00', '00', 'C8', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set NM Power Draw Range)" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed: " + str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set NM Power Draw Range)" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed. Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("Send Message (Set NM Power Draw Range)")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Send Message: Set Intel NM Parameter to enable Fast NM Limiting
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
            '00', '00', '00', '00', '01', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set Intel NM Parameter)" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed: " + str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set Intel NM Parameter)" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed. Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("Send Message (Set Intel NM Parameter)")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Send Message: Set NM Power Draw Range to max
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
            '00', '00', 'FF', '7F' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set NM Power Draw Range)" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed: " + str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set NM Power Draw Range)" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed. Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("Send Message (Set NM Power Draw Range)")
        threadStats.threadPassOrFail &= cmdPassOrFail

        # Send Message: Set Intel NM Parameter to disable Fast NM Limiting
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
            '00', '00', '00', '00', '00', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set Intel NM Parameter)" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command passed: " + str(respData))
            threadStats.commandsPassed += 1
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set Intel NM Parameter)" + \
                " (threadId " + str(threadStats.threadId) + ")" + \
                ": Command failed. Completion Code: " + str(respData))
            threadStats.UpdateFailureStats("Send Message (Set Intel NM Parameter)")
        threadStats.threadPassOrFail &= cmdPassOrFail

    if threadStats.threadPassOrFail:
        UtilLogger.verboseLogger.info("IpmiOverLanOrKcsConcurrentStressTest.runIpmiTest " + \
            "(thread ID " + str(threadStats.threadId) + "): " + \
            "runIpmiTest passed.")
    else:
        UtilLogger.verboseLogger.info("IpmiOverLanOrKcsConcurrentStressTest.runIpmiTest: " + \
            "(thread ID " + str(threadStats.threadId) + "): " + \
            "runIpmiTest failed.")

    # Calculate and update thread duration
    threadStats.threadDuration = datetime.timedelta(seconds=time.time() - startTime)

    # Update testPassOrFail and threadsStats
    threadLock.acquire()
    testPassOrFail &= threadStats.threadPassOrFail
    threadsStats[threadIdx] = threadStats
    threadLock.release()

    return