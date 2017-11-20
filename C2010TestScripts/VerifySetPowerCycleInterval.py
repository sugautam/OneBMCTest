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

import Config
import IpmiUtil
import UtilLogger

# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifySetPowerCycleInterval.py: running Setup fxn")

    return True

# Function will test completion code for Set Power Cycle Interval
def Execute(interfaceParams):

    # Define Test variables
    testPassOrFail = False
    cmdPassOrFail = False
    respData = None

    # Define SetPowerCycleInterval variables
    cmdName = 'SetPowerCycleInterval'
    cmdNum = Config.cmdSetPowerCycleInterval
    netFn = Config.netFnChassis

    # Define sample raw bytes for Set Power Cycle Interval
    # Raw bytes defined as 10 seconds delay
    rawBytesList = \
        [ '0A' ]
        
    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for 10 second interval: " + str(respData))
        testPassOrFail = True
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed. Completion Code: " + str(respData))

    # Define sample raw bytes for Set Power Cycle Interval
    # Raw bytes defined as no delay (expected response: 0xCC)
    rawBytesList = \
        [ '00' ]
        
    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command failed with Success completion code and raw bytes: " + \
            str(respData) + \
            ". Expected 0xCC completion code for no delay power cycle interval.")
        testPassOrFail = False
    elif not cmdPassOrFail and respData == 'cc':
        UtilLogger.verboseLogger.info(cmdName + \
            ". Command passed for no delay power cycle interval. Completion code: " + \
            str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed. Completion Code: " + str(respData))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifySetPowerCycleInterval.py: running Cleanup fxn")

    return True