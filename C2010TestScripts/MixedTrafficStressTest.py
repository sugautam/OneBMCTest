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
import IpmiUtil
import Ssh
import UtilLogger

# Initialize global variables
threadLock = threading.Lock()
testPassOrFail = True

# Prototype Setup Function
def Setup(interfaceParams):

    # Get Sel entries
    processCmd = ['sel', '-u']
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)
    out, err = IpmiUtil.RunIpmiUtil(processCmd)
    if err:
        UtilLogger.verboseLogger.error("MixedTrafficStressTest.py: " + \
            "setup SEL entries error: " + str(err))
        setupSuccess = False
    else:
        UtilLogger.verboseLogger.info("MixedTrafficStressTest.py: " + \
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

# Function will run single iteration of Mixed-Traffic Stress Test
def Execute(interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail

    # Define Test variables
    testPassOrFail = True
    threadDuration = Config.mixedTrafficStressTestThreadDuration # in seconds
    threads = []

    # Test will not be conducted for KCS interface
    if not interfaceParams:
        UtilLogger.verboseLogger.info(\
            "MixedTrafficStressTest.py: Currently using KCS interface. " + \
            "Will not run test.")
        return True

    # Test will not be conducted if local file does not exist
    if not os.path.isfile(Config.mixedTrafficStressLocalFilePath):
        UtilLogger.verboseLogger.error("MixedTrafficStressTest.py: " + \
            "file at local path " + Config.mixedTrafficStressLocalFilePath + \
            " does not exist. Will not run test.")
        return False

    try:

        # Create new threads
        ipmiThread = threading.Thread(name='ipmiThread', target=runIpmiTest, \
            args=(threadDuration, interfaceParams,))
        sftpThread = threading.Thread(name='sftpThread', target=runSftpTest, \
            args=(threadDuration,))

        # Start threads
        UtilLogger.verboseLogger.info("MixedTrafficStressTest.py: starting " + \
            "ipmiThread (Ipmi over LAN+) and sftpThread (SFTP)")
        ipmiThread.start()
        sftpThread.start()

        # Add threads to thread list
        threads.append(ipmiThread)
        threads.append(sftpThread)

        # Wait for all threads to complete
        for testThread in threads:
            testThread.join()

    except Exception, e:
        UtilLogger.verboseLogger.error("MixedTrafficStressTest.py: " + \
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
        UtilLogger.verboseLogger.error("MixedTrafficStressTest.py: " + \
            "setup SEL entries error: " + str(err))
    else:
        UtilLogger.verboseLogger.info("MixedTrafficStressTest.py: " + \
            "setup SEL entries: \n" + str(out))
        cleanupSuccess = True

    # Detect and Remove BMC Hang
    return Helper.DetectAndRemoveBmcHang(interfaceParams)

# Function will run Ipmi over LAN+ commands
def runIpmiTest(duration, interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail

    # Initialize variables
    threadPassOrFail = True
    
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
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("GetDeviceId" + \
                ": Command failed. Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Get Sdr
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdGetSdr, [ '00', '00', '00', '00', '00', 'FF' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetSdr" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("GetSdr" + \
                ": Command failed. Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Read Fru Data
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdReadFruData, [ '00', '00', '00', '08' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("ReadFruData" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("ReadFruData" + \
                ": Command failed. Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Get Power Reading
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnDcmi,\
            Config.cmdGetPowerReading, [ 'DC', '01', '01', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetPowerReading" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("GetPowerReading" + \
                ": Command failed. Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Set Next Boot to BIOS Setup
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '18', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                ": Command passed for set next boot to Bios Setup: " + \
                str(respData))
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                ": Command failed for set next boot to Bios Setup." + \
                " Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Set Next Boot to EFI
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '00', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                ": Command passed for set next boot to EFI: " + \
                str(respData))
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                ": Command failed for set next boot to EFI." + \
                " Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Set Next Boot to PXE
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '04', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                ": Command passed for set next boot to PXE: " + \
                str(respData))
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                ": Command failed for set next boot to PXE." + \
                " Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail
            
        # Set Next Boot to Hard Disk
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '08', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                ": Command passed for set next boot to Hard Disk: " + \
                str(respData))
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                ": Command failed for set next boot to Hard Disk." + \
                " Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Get Sel Entry
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdGetSelEntry, [ '00', '00', '00', '00', '00', 'FF' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetSelEntry" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("GetSelEntry" + \
                ": Command failed. Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

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
                    ": Command passed for cpu 0x"\
                    + cpuIdx + ": " + str(respData))
            else:
                UtilLogger.verboseLogger.error("GetProcessorInfo" + \
                    ": Command failed for cpu 0x" + cpuIdx + \
                    ". Completion Code: " + str(respData))
            cmdPassOrFail &= cpuPassOrFail
        threadPassOrFail &= cpuPassOrFail

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
                    ": Command passed for dimm 0x"\
                    + dimmIdx + ": " + str(respData))
            else:
                UtilLogger.verboseLogger.error("GetMemoryInfo" + \
                    ": Command failed for dimm 0x" + dimmIdx + \
                    ". Completion Code: " + str(respData))
            cmdPassOrFail &= dimmPassOrFail
        threadPassOrFail &= dimmPassOrFail

        # Get Pcie Info
        for idx in range(0, 22):
            pcieIdx = hex(idx).lstrip('0x')
            if idx == 0:
                pcieIdx = '0'
            pciePassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
                Config.netFnOem30, Config.cmdGetPcieInfo, [ pcieIdx ])
            if pciePassOrFail:
                UtilLogger.verboseLogger.info("GetPcieInfo" + \
                    ": Command passed for pcie 0x"\
                    + pcieIdx + ": " + str(respData))
            else:
                UtilLogger.verboseLogger.error("GetPcieInfo" + \
                    ": Command failed for pcie 0x" + pcieIdx + \
                    ". Completion Code: " + str(respData))
            cmdPassOrFail &= pciePassOrFail
        threadPassOrFail &= pciePassOrFail

        # Get Nic Info
        threadPassOrFail &= IpmiUtil.VerifyGetNicInfo(interfaceParams)

        # Send Message: Get CPU and Memory Temperature
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', '4B', '57', '01', '00', '03', \
            'FF', 'FF', 'FF', 'FF', '00', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Get CPU and Memory Temperature)" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Get CPU and Memory Temerature)" + \
                ": Command failed. Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Send Message: Set NM Power Draw Range to 200 W max
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
            '00', '00', 'C8', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set NM Power Draw Range)" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set NM Power Draw Range)" + \
                ": Command failed. Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Send Message: Set Intel NM Parameter to enable Fast NM Limiting
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
            '00', '00', '00', '00', '01', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set Intel NM Parameter)" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set Intel NM Parameter)" + \
                ": Command failed. Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Send Message: Set NM Power Draw Range to max
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
            '00', '00', 'FF', '7F' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set NM Power Draw Range)" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set NM Power Draw Range)" + \
                ": Command failed. Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

        # Send Message: Set Intel NM Parameter to disable Fast NM Limiting
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
            '00', '00', '00', '00', '00', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set Intel NM Parameter)" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set Intel NM Parameter)" + \
                ": Command failed. Completion Code: " + str(respData))
        threadPassOrFail &= cmdPassOrFail

    if threadPassOrFail:
        UtilLogger.verboseLogger.info("MixedTrafficStressTest.runIpmiTest: " + \
            "runIpmiTest passed.")
    else:
        UtilLogger.verboseLogger.info("MixedTrafficStressTest.runIpmiTest: " + \
            "runIpmiTest failed.")

    # Update testPassOrFail
    threadLock.acquire()
    testPassOrFail &= threadPassOrFail
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

    while time.time() < totalTestTime:

        # Put file in target (host) file path
        sftpPassOrFail = Ssh.sftpPutFile(Config.mixedTrafficStressLocalFilePath, \
            Config.mixedTrafficStressHostFilePath)
        if sftpPassOrFail:
            UtilLogger.verboseLogger.info("MixedTrafficStressTest.runSftpTest: " + \
                "successfully put file via Sftp.")
        else:
            UtilLogger.verboseLogger.error("MixedTrafficStressTest.runSftpTest: " + \
                "failed to put file via Sftp. Local path: " + \
                Config.mixedTrafficStressLocalFilePath + " Host path: " + \
                Config.mixedTrafficStressHostFilePath)
        threadPassOrFail &= sftpPassOrFail

        # Remove file from target (host) file path
        sftpPassOrFail = Ssh.sftpRemoveFile(Config.mixedTrafficStressHostFilePath)
        if sftpPassOrFail:
            UtilLogger.verboseLogger.info("MixedTrafficStressTest.runSftpTest: " + \
                "successfully removed file via Sftp.")
        else:
            UtilLogger.verboseLogger.error("MixedTrafficStressTest.runSftpTest: " + \
                "failed to remove file via Sftp. Host path: " + \
                Config.mixedTrafficStressHostFilePath)
        threadPassOrFail &= sftpPassOrFail

        # Sleep for 100 milliseconds
        time.sleep(0.1)

    if threadPassOrFail:
        UtilLogger.verboseLogger.info("MixedTrafficStressTest.runSftpTest: " + \
            "runSftpTest passed.")
    else:
        UtilLogger.verboseLogger.info("MixedTrafficStressTest.runSftpTest: " + \
            "runSftpTest failed.")

    # Update testPassOrFail
    threadLock.acquire()
    testPassOrFail &= threadPassOrFail
    threadLock.release()

    return