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
import time

import AcPowerIpSwitch
import Config
import Helper
import IpmiUtil
import UtilLogger

# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info(\
        "FirmwareDecompressionTest.py: running Setup fxn")

    return True

# Function will run Firmware Decompression Test
def Execute(interfaceParams):

    # Define Test variables
    testPassOrFail = True
    respData = []
    testName = 'FirmwareDecompressionTest'
    actualFwDecompressionTime = None
    
    try:
        if not interfaceParams:
            UtilLogger.consoleLogger.info(\
                "Currently running in-band in server blade. Will not execute test.")
            UtilLogger.verboseLogger.info(\
                "Currently running in-band in server blade. Will not execute test.")
            return True

        # Power Down Server Blade
        powerPassOrFail, response = AcPowerIpSwitch.SetPowerOnOff(\
            Config.acPowerIpSwitchOutlet, 0)
        if powerPassOrFail:
            UtilLogger.verboseLogger.info(testName + \
                ": Server blade powered down.")
        else:
            UtilLogger.verboseLogger.error(testName + \
                ": Failed to power down server blade.")
        testPassOrFail &= powerPassOrFail

        # Sleep
        UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: " + \
            "Sleeping for " + str(Config.acPowerOffSleepInSeconds) + " seconds.")
        time.sleep(Config.acPowerOffSleepInSeconds)

        # Power Up Server Blade
        powerPassOrFail, response = AcPowerIpSwitch.SetPowerOnOff(\
            Config.acPowerIpSwitchOutlet, 1)
        if powerPassOrFail:
            UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: " + \
                "Server blade powered up.")
        else:
            UtilLogger.verboseLogger.error("AcPowerCycleStressTest.py: " + \
                "Failed to power up server blade.")
        testPassOrFail &= powerPassOrFail

        # Ping BMC until it responds
        pingPassOrFail, actualFwDecompressionTime = Helper.PingAndCheckResponse(\
            Config.fwDecompressionTestLimit, Config.bmcIpAddress)
        testPassOrFail &= pingPassOrFail

        # Poll BMC until it responds
        getPassOrFail, actualFwDecompressionTime = Helper.GetDeviceIdAndCheckResponse(\
            Config.fwDecompressionTestLimit, interfaceParams, actualFwDecompressionTime)
        testPassOrFail &= getPassOrFail

        # Check if measured FW Decompression Time within expected value
        if actualFwDecompressionTime == -1:
            UtilLogger.verboseLogger.error(testName + \
                ": test failed since BMC FW did not decompress" + \
                " before test limit of " + str(Config.fwDecompressionTestLimit) + \
                " seconds.")
            testPassOrFail = False
        else:
            if actualFwDecompressionTime <= float(Config.bmcFwDecompressionInSeconds):
                UtilLogger.verboseLogger.info(testName + \
                    ": test passed. Actual Bmc Fw Decompression Time: " + \
                    str(actualFwDecompressionTime) + " seconds." + \
                    " Expected Bmc Fw Decompression Time: " + \
                    str(Config.bmcFwDecompressionInSeconds) + \
                    " seconds.")
            else:
                UtilLogger.verboseLogger.error(testName + \
                    ": test failed. Actual Bmc Fw Decompression Time: " + \
                    str(actualFwDecompressionTime) + " seconds." + \
                    " Expected Bmc Fw Decompression Time: " + \
                    str(Config.bmcFwDecompressionInSeconds) + \
                    " seconds.")
                testPassOrFail = False

    except Exception, e:
        UtilLogger.verboseLogger.info("FirmwareDecompressionTest.py: exception occurred - " + \
            str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    # Detect and Remove BMC Hang
    return Helper.DetectAndRemoveBmcHang(interfaceParams)