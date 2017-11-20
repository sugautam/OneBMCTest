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

import time

import Config
import Helper
import IpmiUtil
import UtilLogger

# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info("BmcMeCompletionCodeSmokeTest.py: running Setup fxn")

    return True

# Function will test completion code for BMC ME Smoke Test
def Execute(interfaceParams):

    # Define Test variables
    testName = 'BmcMeCompletionCodeSmokeTest'
    testPassOrFail = True
    respData = None

    # Send raw bytes for Send Message 
    # (Get Device ID)
    testPassOrFail &= RetryCommand(\
        'Send Message (Get Device ID)', interfaceParams, \
        [ '00', '20', '18', '01' ])

    # Send raw bytes for Send Message 
    # (Send Raw PECI - 
    # RdPkgConfig(): read DDR DIMM Digital Thermal Reading (CLTT) for channel 0)
    testPassOrFail &= RetryCommand(\
        'Send Message (Send Raw PECI - RdPkgConfig(): read DDR DIMM Digital ' + \
        'Thermal Reading (CLTT))', interfaceParams, \
        [ '00', '20', 'B8', '40', '57', '01', '00', '30', '05', '05', \
        'A1', '00', '0E', '00', '00' ])

    # Send raw bytes for Send Message 
    # (Send Raw PMBUS command - READ_PIN: read input power)
    testPassOrFail &= RetryCommand(\
        'Send Message (Send Raw PMBUS command - READ_PIN: read input power)', \
        interfaceParams, \
        [ '00', '20', 'B8', 'D9', '57', '01', '00', '16', '02', '22', \
        '00', '00', '00', '00', '01', '02', '97' ])

    # Send raw bytes for Send Message (Set Power Limit to 500 W)
    testPassOrFail &= RetryCommand(\
        'Send Message (Set Power Limit to 500 W)', interfaceParams, \
        [ '00', '20', 'B0', '04', 'DC', '00', '00', '00', '00', 'F4', \
        '01', '70', '17', '00', '00', '00', '00', '80', '01' ])

    # Send raw bytes for Send Message (Activate Power Limit - Activate)
    testPassOrFail &= RetryCommand(\
        'Send Message (Activate Power Limit - Activate)', interfaceParams, \
        [ '00', '20', 'B0', '05', 'DC', '01', '00', '00' ])

    # Send raw bytes for Send Message (Get Power Limit)
    testPassOrFail &= RetryCommand(\
        'Send Message (Get Power Limit)', interfaceParams, \
        [ '00', '20', 'B0', '03', 'DC', '00', '00' ])

    # Send raw bytes for Send Message (Activate Power Limit - De-Activate)
    testPassOrFail &= RetryCommand(\
        'Send Message (Activate Power Limit - De-Activate)', interfaceParams, \
        [ '00', '20', 'B0', '05', 'DC', '00', '00', '00' ])

    # Send raw bytes for Send Message (Get Power Reading)
    testPassOrFail &= RetryCommand(\
        'Send Message (Get Power Reading)', interfaceParams, \
        [ '00', '20', 'B0', '02', 'DC', '01', '00', '00' ])

    # Send raw bytes for Send Message (Get Sensor Reading - CPU0 Tjmax)
    testPassOrFail &= RetryCommand(\
        'Send Message (Get Sensor Reading - CPU0 Tjmax)', interfaceParams, \
        [ '00', '20', '10', '2D', '30' ])

    # Send raw bytes for Send Message (Get Sensor Reading - CPU1 Tjmax)
    testPassOrFail &= RetryCommand(\
        'Send Message (Get Sensor Reading - CPU1 Tjmax)', interfaceParams, \
        [ '00', '20', '10', '2D', '31' ])

    # Send raw bytes for Send Message (Get Sensor Reading - CPU0 Thermal Status)
    testPassOrFail &= RetryCommand(\
        'Send Message (Get Sensor Reading - CPU0 Thermal Status)', interfaceParams, \
        [ '00', '20', '10', '2D', '1C' ])

    # Send raw bytes for Send Message (Get Sensor Reading - CPU1 Thermal Status)
    testPassOrFail &= RetryCommand(\
        'Send Message (Get Sensor Reading - CPU1 Thermal Status)', interfaceParams, \
        [ '00', '20', '10', '2D', '1D' ])

    # Send raw bytes for Send Message 
    # (Force Intel ME Recovery - Restart using Recovery Firmware)
    cmdPassOrFail = RetryCommand(\
        'Send Message (Force Intel ME Recovery - ' + \
        'Restart using Recovery Firmware)', interfaceParams, \
        [ '00', '20', 'B8', 'DF', '57', '01', '00', '01' ])
    testPassOrFail &= cmdPassOrFail

    # Sleep to allow for ME reset
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info("BmcMeCompletionCodeSmokeTest: " + \
            "ME restarting. Sleeping for " + \
            str(Config.meResetSleepInSeconds) + \
            " seconds..")
        time.sleep(Config.meResetSleepInSeconds)

    # Send raw bytes for Send Message 
    # (Force Intel ME Recovery - Restore Factory Default Variable values)
    cmdPassOrFail = RetryCommand(\
        'Send Message (Force Intel ME Recovery - ' + \
        'Restore Factory Default Variable values and Restart Intel ME FW)', \
        interfaceParams, \
        [ '00', '20', 'B8', 'DF', '57', '01', '00', '02' ])
    testPassOrFail &= cmdPassOrFail

    # Sleep to allow for ME reset
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info("BmcMeCompletionCodeSmokeTest: " + \
            "ME restarting. Sleeping for " + \
            str(Config.meResetSleepInSeconds) + \
            " seconds..")
        time.sleep(Config.meResetSleepInSeconds)

    # Send raw bytes for Send Message 
    # (ME Cold Reset)
    cmdPassOrFail = RetryCommand(\
        'Send Message (ME Cold Reset)', interfaceParams, \
        [ '00', '20', '18', '02' ])
    testPassOrFail &= cmdPassOrFail

    # Sleep to allow for ME Cold Reset
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info("BmcMeCompletionCodeSmokeTest: " + \
            "ME cold resetting. Sleeping for " + \
            str(Config.meResetSleepInSeconds) + \
            " seconds..")
        time.sleep(Config.meResetSleepInSeconds)

    # Send raw bytes for Send Message 
    # (Send Raw PECI - RdPkgConfig(): read package identifier for CPUID Info)
    testPassOrFail &= RetryCommand(\
        'Send Message (Send Raw PECI - RdPkgConfig(): read package ' + \
        'identifier for CPUID Info)', interfaceParams, \
        [ '00', '20', 'b8', '40', '57', '01', '00', '70', \
        '05', '05', 'a1', '00', '00', '00', '00' ])

    # Send Message: Get CPU and Memory Temperature
    testPassOrFail &= RetryCommand(\
        "Send Message (Get CPU and Memory Temperature)",\
        interfaceParams,\
        [ '00', '20', 'B8', '4B', '57', '01', '00', '03', \
        'FF', 'FF', 'FF', 'FF', '00', '00', '00', '00' ])

    # Send Message: Set NM Power Draw Range to 200 W max
    testPassOrFail &= RetryCommand(\
        "Send Message (Set NM Power Draw Range)",\
        interfaceParams,\
        [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
        '00', '00', 'C8', '00' ])

    # Send Message: Set Intel NM Parameter to enable Fast NM Limiting
    testPassOrFail &= RetryCommand(\
        "Send Message (Set Intel NM Parameter)",\
        interfaceParams,\
        [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
        '00', '00', '00', '00', '01', '00', '00', '00' ])

    # Send Message: Set NM Power Draw Range to max
    testPassOrFail &= RetryCommand(\
        "Send Message (Set NM Power Draw Range)",\
        interfaceParams,\
        [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
        '00', '00', 'FF', '7F' ])

    # Send Message: Set Intel NM Parameter to disable Fast NM Limiting
    testPassOrFail &= RetryCommand(\
        "Send Message (Set Intel NM Parameter)",\
        interfaceParams,\
        [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
        '00', '00', '00', '00', '00', '00', '00', '00' ])

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
