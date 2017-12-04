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

import os
import time
import Config
import Helper
import IpmiUtil
import UtilLogger
import FwFlash

previousFwVersion = []

# Prototype Setup Function
def Setup(interfaceParams):

    # Declare module-scope variables
    global previousFwVersion

    # Initialize variables
    setupPassOrFail = True
    processCmd = []

    # Flash Bmc Fw with previous version
    flashPassOrFail = FwFlash.YafuFlashBmcFw(\
        Config.bmcPrevBinFilePath,\
        Config.bmcIpAddress,\
        Config.bmcUser,\
        Config.bmcPassword)

    if flashPassOrFail:
        UtilLogger.verboseLogger.info("YafuFlashBmcFwUpdateTest: " + \
            "Bmc FW at path " + Config.bmcPrevBinFilePath + \
            " successfully flashed.")
        # Sleep
        UtilLogger.verboseLogger.info("YafuFlashBmcFwUpdateTest" + \
            ": Sleeping for " + str(Config.acPowerOnSleepInSeconds) + \
            " seconds..")
        time.sleep(Config.acPowerOnSleepInSeconds)
    else:
        UtilLogger.verboseLogger.info("YafuFlashBmcFwUpdateTest: " + \
            "Bmc FW at path " + Config.bmcPrevBinFilePath + \
            " failed FW flash.")
        return False

    # Get Device Id
    cmdName = 'GetDeviceId'
    cmdNum = Config.cmdGetDeviceId
    netFn = Config.netFnApp

    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, netFn, cmdNum, [])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": success completion code.")
        major, minor, aux = FwFlash.extractBmcFwGetDeviceId(respData)
        previousFwVersion = [ major, minor, aux ]
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": command failed. Completion Code: " + \
            str(respData))
        setupPassOrFail = False

    return setupPassOrFail

# Function will test BMC FW Update using
# Yafuflash for either KCS or IPMI over LAN+
def Execute(interfaceParams):

    # Declare module-scope variables
    global previousFwVersion

    # Define Test variables
    testPassOrFail = True
    flashedFwVersion = []

    # Flash BMC FW to next and verify
    # flashed FW newer than previous FW
    testPassOrFail &= FlashFwAndCompare(interfaceParams, \
        Config.bmcNextBinFilePath, 1)

    # Flash BMC FW to next again and verify
    # flashed FW same as previous FW
    testPassOrFail &= FlashFwAndCompare(interfaceParams, \
        Config.bmcNextBinFilePath, 0)

    # Flash BMC FW to prev and verify
    # flashed FW older than previous FW
    testPassOrFail &= FlashFwAndCompare(interfaceParams, \
        Config.bmcPrevBinFilePath, -1)

    # Flash BMC FW to prev again and verify
    # flashed FW same as previous FW
    testPassOrFail &= FlashFwAndCompare(interfaceParams, \
        Config.bmcPrevBinFilePath, 0)

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    # Initialize variables
    cleanupPassOrFail = True
    processCmd = []

    # Flash Bmc Fw with previous version
    flashPassOrFail = FwFlash.YafuFlashBmcFw(\
        Config.bmcNextBinFilePath,\
        Config.bmcIpAddress,\
        Config.bmcUser,\
        Config.bmcPassword)

    if flashPassOrFail:
        UtilLogger.verboseLogger.info("YafuFlashBmcFwUpdateTest: " + \
            "Bmc FW at path " + Config.bmcNextBinFilePath + \
            " successfully flashed.")
                # Sleep
        UtilLogger.verboseLogger.info("YafuFlashBmcFwUpdateTest" + \
            ": Sleeping for " + str(Config.acPowerOnSleepInSeconds) + \
            " seconds..")
        time.sleep(Config.acPowerOnSleepInSeconds)
    else:
        UtilLogger.verboseLogger.info("YafuFlashBmcFwUpdateTest: " + \
            "Bmc FW at path " + Config.bmcNextBinFilePath + \
            " failed FW flash.")
        cleanupPassOrFail = False

    # Detect and Remove BMC Hang
    cleanupPassOrFail &= Helper.DetectAndRemoveBmcHang(interfaceParams)

    return cleanupPassOrFail

def FlashFwAndCompare(interfaceParams, currentFwFilePath, expectedCompare):

    # Declare module-scope variables
    global previousFwVersion

    # Initialize variables
    testName = 'YafuFlashBmcFwUpdateTest'
    testPassOrFail = True
    flashedFwVersion = []

    # Initialize compare print statement
    comparePrint = ''
    if expectedCompare == 1:
        comparePrint = 'newer than'
    elif expectedCompare == 0:
        comparePrint = 'same as'
    elif expectedCompare == -1:
        comparePrint = 'older than'

    # Flash BMC FW to next again
    flashPassOrFail = FwFlash.YafuFlashBmcFw(\
        currentFwFilePath,\
        Config.bmcIpAddress,\
        Config.bmcUser,\
        Config.bmcPassword)

    # Verify flash successful
    if flashPassOrFail:
        UtilLogger.verboseLogger.info(testName + \
            ": BMC FW flash test passed.")
        # Sleep
        UtilLogger.verboseLogger.info(testName + \
            ": Sleeping for " + str(Config.acPowerOnSleepInSeconds) + \
            " seconds..")
        time.sleep(Config.acPowerOnSleepInSeconds)
    else:
        UtilLogger.verboseLogger.error(testName + \
            ": BMC FW flash test failed.")
        testPassOrFail = False

    # Get Device Id
    cmdName = 'GetDeviceId'
    cmdNum = Config.cmdGetDeviceId
    netFn = Config.netFnApp

    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, netFn, cmdNum, [])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": success completion code.")
        major, minor, aux = FwFlash.extractBmcFwGetDeviceId(respData)
        flashedFwVersion = [ major, minor, aux ]
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": command failed. Completion Code: " + \
            str(respData))
        testPassOrFail = False

    # Verify flashedFwVersion newer/older/same than previousFwVersion
    if testPassOrFail:
        compareFw = FwFlash.CompareBmcFwVersion(\
            flashedFwVersion[0], flashedFwVersion[1], flashedFwVersion[2],\
            previousFwVersion[0], previousFwVersion[1], previousFwVersion[2])
        if compareFw == expectedCompare:
            UtilLogger.verboseLogger.info("YafuFlashBmcFwUpdateTest: " + \
                " Bmc Fw (next) " + comparePrint + " previous version." + \
                " Current version: " + str(flashedFwVersion[0]) + '.' + \
                str(flashedFwVersion[1]) + '.' + \
                str(flashedFwVersion[2]) + \
                " Previous version: " + str(previousFwVersion[0]) + '.' + \
                str(previousFwVersion[1]) + '.' + \
                str(previousFwVersion[2]))
        else:
            UtilLogger.verboseLogger.info("YafuFlashBmcFwUpdateTest: " + \
                " Bmc Fw (next) NOT " + comparePrint + " previous version." + \
                " Current version: " + str(flashedFwVersion[0]) + '.' + \
                str(flashedFwVersion[1]) + '.' + \
                str(flashedFwVersion[2]) + \
                " Previous version: " + str(previousFwVersion[0]) + '.' + \
                str(previousFwVersion[1]) + '.' + \
                str(previousFwVersion[2]))
            testPassOrFail = False

    # Update previous version
    if testPassOrFail:
        previousFwVersion = flashedFwVersion

    return testPassOrFail