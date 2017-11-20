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

    UtilLogger.verboseLogger.info("ConcurrentStressTest.py: running Setup fxn")

    return True

# Function will run concurrent stress test 
# for Ipmi over LAN+ and KCS
def Execute(interfaceParams):

    # Define Test variables
    testPassOrFail = True
    respData = []
    testName = 'ConcurrentStressTest'
    startTime = time.time()

    # total test time in seconds
    # total test time = 60 seconds/minute *
    #   60 minutes/hour * <totalTestTimeInHours>
    totalTestTime = startTime + 60 * 60 * \
        Config.concurrentStressTestTotalTime 
    
    try:
        if not interfaceParams:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.concurrentStressTestTotalTime ) + \
                "-hour concurrent stress test for KCS")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.concurrentStressTestTotalTime ) + \
                "-hour concurrent stress test for KCS")
        else:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.concurrentStressTestTotalTime) + \
                "-hour concurrent stress test for Ipmi over LAN+")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.concurrentStressTestTotalTime) + \
                "-hour concurrent stress test for Ipmi over LAN+")

        # Run test
        # Print Cycle # PASS/FAIL for every test cycle
        testCycle = 0
        cyclesPassed = 0
        cyclesFailed = 0
        while time.time() < totalTestTime:

            cyclePassOrFail = True

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
            cyclePassOrFail &= cmdPassOrFail

            # Soft power up blade
            cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
                interfaceParams, Config.netFnChassis,\
                Config.cmdChassisControl, [ '01' ])
            if cmdPassOrFail:
                # Sleep for 30 seconds
                time.sleep(30)
                UtilLogger.verboseLogger.info("ChassisControl.PowerUp" + \
                    ": Command passed: " + str(respData))
            else:
                UtilLogger.verboseLogger.error("ChassisControl.PowerUp" + \
                    ": Command failed. Completion Code: " + str(respData))
            cyclePassOrFail &= cmdPassOrFail

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
            cyclePassOrFail &= cmdPassOrFail

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
            cyclePassOrFail &= cmdPassOrFail

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
            cyclePassOrFail &= cmdPassOrFail

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
            cyclePassOrFail &= cmdPassOrFail

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
            cyclePassOrFail &= cmdPassOrFail

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
            cyclePassOrFail &= cmdPassOrFail
            
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
            cyclePassOrFail &= cmdPassOrFail

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
            cyclePassOrFail &= cmdPassOrFail

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
            cyclePassOrFail &= cpuPassOrFail

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
            cyclePassOrFail &= dimmPassOrFail

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
            cyclePassOrFail &= pciePassOrFail

            # Get Nic Info
            cyclePassOrFail &= IpmiUtil.VerifyGetNicInfo(interfaceParams)

            # Send Message: Get CPU and Memory Temperature
            sendMsgPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
                [ '00', '20', 'B8', '4B', '57', '01', '00', '03', \
                'FF', 'FF', 'FF', 'FF', '00', '00', '00', '00' ])
            if sendMsgPassOrFail:
                UtilLogger.verboseLogger.info(\
                    "Send Message (Get CPU and Memory Temperature)" + \
                    ": Command passed: " + str(respData))
            else:
                UtilLogger.verboseLogger.error(\
                    "Send Message (Get CPU and Memory Temerature)" + \
                    ": Command failed. Completion Code: " + str(respData))
            cyclePassOrFail &= sendMsgPassOrFail

            # Send Message: Set NM Power Draw Range to 200 W max
            sendMsgPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
                [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
                '00', '00', 'C8', '00' ])
            if sendMsgPassOrFail:
                UtilLogger.verboseLogger.info(\
                    "Send Message (Set NM Power Draw Range)" + \
                    ": Command passed: " + str(respData))
            else:
                UtilLogger.verboseLogger.error(\
                    "Send Message (Set NM Power Draw Range)" + \
                    ": Command failed. Completion Code: " + str(respData))
            cyclePassOrFail &= sendMsgPassOrFail

            # Send Message: Set Intel NM Parameter to enable Fast NM Limiting
            sendMsgPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
                [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
                '00', '00', '00', '00', '01', '00', '00', '00' ])
            if sendMsgPassOrFail:
                UtilLogger.verboseLogger.info(\
                    "Send Message (Set Intel NM Parameter)" + \
                    ": Command passed: " + str(respData))
            else:
                UtilLogger.verboseLogger.error(\
                    "Send Message (Set Intel NM Parameter)" + \
                    ": Command failed. Completion Code: " + str(respData))
            cyclePassOrFail &= sendMsgPassOrFail

            # Send Message: Set NM Power Draw Range to max
            sendMsgPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
                [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
                '00', '00', 'FF', '7F' ])
            if sendMsgPassOrFail:
                UtilLogger.verboseLogger.info(\
                    "Send Message (Set NM Power Draw Range)" + \
                    ": Command passed: " + str(respData))
            else:
                UtilLogger.verboseLogger.error(\
                    "Send Message (Set NM Power Draw Range)" + \
                    ": Command failed. Completion Code: " + str(respData))
            cyclePassOrFail &= sendMsgPassOrFail

            # Send Message: Set Intel NM Parameter to disable Fast NM Limiting
            sendMsgPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
                [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
                '00', '00', '00', '00', '00', '00', '00', '00' ])
            if sendMsgPassOrFail:
                UtilLogger.verboseLogger.info(\
                    "Send Message (Set Intel NM Parameter)" + \
                    ": Command passed: " + str(respData))
            else:
                UtilLogger.verboseLogger.error(\
                    "Send Message (Set Intel NM Parameter)" + \
                    ": Command failed. Completion Code: " + str(respData))
            cyclePassOrFail &= sendMsgPassOrFail

            # Verify test cycle
            if cyclePassOrFail:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " ConcurrentStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " ConcurrentStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                cyclesPassed += 1
            else:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " ConcurrentStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - startTime))) + \
                    " ConcurrentStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                cyclesFailed += 1
            UtilLogger.verboseLogger.info("")
            testCycle += 1
            testPassOrFail &= cyclePassOrFail

            # Sleep for 1 minute
            time.sleep(60)

        # Print Test Summary results
        endTime = time.time()
        if not interfaceParams:
            UtilLogger.consoleLogger.info("Kcs Stress Test Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
            UtilLogger.verboseLogger.info("Kcs Stress Test Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
        else:
            UtilLogger.consoleLogger.info("Ipmi over LAN+ Stress Test" + \
                " Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
            UtilLogger.verboseLogger.info("Ipmi over LAN+ Stress Test" + \
               " Summary - Cycles Passed: " + \
                str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
                " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
                " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
    except Exception, e:
        UtilLogger.verboseLogger.info("ConcurrentStressTest.py: exception occurred - " + \
            str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    # Detect and Remove BMC Hang
    return Helper.DetectAndRemoveBmcHang(interfaceParams)