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

    setupSuccess = False

    # Get Sel entries
    processCmd = ['sel', '-u']
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)
    out, err = IpmiUtil.RunIpmiUtil(processCmd)
    if err:
        UtilLogger.verboseLogger.error("DcPowerCycleStressTest.py: " + \
            "setup SEL entries error: " + str(err))
    else:
        UtilLogger.verboseLogger.info("DcPowerCycleStressTest.py: " + \
            "setup SEL entries: \n" + str(out))
        setupSuccess = True

    return setupSuccess

# Function will run stress test over Ipmi over LAN+ or KCS
# for DC Power Cycling BMC
def Execute(interfaceParams):

    # Define Test variables
    testPassOrFail = True
    respData = []
    testName = 'DcPowerCycleStressTest'
    startTime = time.time()

    # total test time in seconds
    # total test time = 60 seconds/minute *
    #   60 minutes/hour * <totalTestTimeInHours>
    totalTestTime = startTime + 60 * 60 * \
        Config.dcPowerCycleStressTestTotalTime
    
    try:
        if not interfaceParams:
            UtilLogger.consoleLogger.info(\
                "Currently running in-band in server blade. Will not execute test.")
            UtilLogger.verboseLogger.info(\
                "Currently running in-band in server blade. Will not execute test.")
            return True
        else:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.dcPowerCycleStressTestTotalTime) + \
                "-hour DC Power Up/Down Status stress test for Ipmi over LAN+")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.dcPowerCycleStressTestTotalTime) + \
                "-hour DC Power Up/Down Status stress test for Ipmi over LAN+")

        # Run test
        # Print Cycle # PASS/FAIL for every test cycle
        testCycle = 0
        cyclesPassed = 0
        cyclesFailed = 0
        while time.time() < totalTestTime:

            cyclePassOrFail = True
            cycleStartTime = time.time()

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
            
            # Define ChassisControl variables
            cmdName = 'ChassisControl'
            cmdNum = Config.cmdChassisControl
            netFn = Config.netFnChassis

            # Define sample raw byte for 
            # power down (0x00)
            rawBytesList = [ '00' ]

            # Send raw bytes via IpmiUtil
            chassisCtrlPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
                netFn, cmdNum, rawBytesList)

            # Verify response
            if chassisCtrlPassOrFail:
                UtilLogger.verboseLogger.info(cmdName + \
                    ": Command passed for power down: "\
                    + str(respData))
            else:
                UtilLogger.verboseLogger.error(cmdName + \
                    ": Command failed for power down."\
                    + " Completion Code: " + str(respData))

            cyclePassOrFail &= chassisCtrlPassOrFail

            # Define sample raw byte for 
            # power up (0x01)
            rawBytesList = [ '01' ]

            # Send raw bytes via IpmiUtil
            chassisCtrlPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
                netFn, cmdNum, rawBytesList)

            # Verify response
            if chassisCtrlPassOrFail:
                UtilLogger.verboseLogger.info(cmdName + \
                    ": Command passed for power up: "\
                    + str(respData))
            else:
                UtilLogger.verboseLogger.error(cmdName + \
                    ": Command failed for power up."\
                    + " Completion Code: " + str(respData))

            cyclePassOrFail &= chassisCtrlPassOrFail

            # Check for Chassis Status Off
            cyclePassOrFail &= Helper.CheckForChassisStatus(interfaceParams, 0)

            # Check for Chassis Status ON
            cyclePassOrFail &= Helper.CheckForChassisStatus(interfaceParams, 1)

            # Connect to BMC via SSH and test to see if 
            #   boot to BIOS Start screen can be detected
            cyclePassOrFail &= Helper.SshBootToBiosStartScreenTest(cycleStartTime)

            # Get and verify Sel entries
            selPassOrFail, unexpectedSels = IpmiUtil.VerifySelAgainstXmlList(interfaceParams, \
                Config.dcPowerCycleStressTestExpectedSelsXmlFilePath)
            if selPassOrFail:
                UtilLogger.verboseLogger.info("DcPowerCycleStressTest.py: " + \
                    "required/optional SELs in " + \
                    Config.dcPowerCycleStressTestExpectedSelsXmlFilePath + \
                    " match actual SEL output.")
            else:
                UtilLogger.verboseLogger.error("DcPowerCycleStressTest.py: " + \
                    " actual SELs failed to match expected SELs in " + \
                    Config.dcPowerCycleStressTestExpectedSelsXmlFilePath + \
                    ". Unexpected SEL entries: " + "\n" + \
                    "\n".join(\
                    unexpectedSels if unexpectedSels is not None else [ 'Empty' ]) + "\n")
            cyclePassOrFail &= selPassOrFail

            # Get and verify sensor entries
            sensorPassOrFail = IpmiUtil.VerifyThresholdSensors(interfaceParams, \
                Config.sensorListXmlFile)
            if sensorPassOrFail:
                UtilLogger.verboseLogger.info("DcPowerCycleStressTest.py: " + \
                    "actual sensor values are within expected margins defined in " + \
                    Config.sensorListXmlFile)
            else:
                UtilLogger.verboseLogger.error("DcPowerCycleStressTest.py: " + \
                    "actual sensor values fail to be within expected margins defined in " + \
                    Config.sensorListXmlFile)
            cyclePassOrFail &= sensorPassOrFail

            # Verify test cycle
            if cyclePassOrFail:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " DcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " DcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                cyclesPassed += 1
            else:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " DcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " DcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                cyclesFailed += 1
            UtilLogger.verboseLogger.info("")
            testCycle += 1
            testPassOrFail &= cyclePassOrFail

        # Print Test Summary results
        endTime = time.time()
        UtilLogger.consoleLogger.info(\
            "DC Power Cycle over Ipmi over LAN+ Stress Test" + \
            " Summary - Cycles Passed: " + \
            str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
            " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
            " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
        UtilLogger.verboseLogger.info(\
            "DC Power Cycle over Ipmi over LAN+ Stress Test" + \
            " Summary - Cycles Passed: " + \
            str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
            " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
            " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
    except Exception, e:
        UtilLogger.verboseLogger.info("DcPowerCycleStressTest.py: exception occurred - " + \
            str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    # Detect and Remove BMC Hang if it occurs
    return Helper.DetectAndRemoveBmcHang(interfaceParams)