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

import Config
import IpmiUtil
import UtilLogger

# Prototype Setup Function
def Setup(interfaceParams):

    # Send raw bytes for Send Message (Activate Power Limit - Activate)
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnDcmi, Config.cmdActivatePowerLimit, \
        [ 'DC', '01', '00', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info('Send Message (Activate Power Limit - Activate)' + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.info('Send Message (Activate Power Limit - Activate)' + \
            ": Command failed. Completion Code: " + str(respData))

    return cmdPassOrFail

# Function will test default values for
# Get Power Limit
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetPowerLimit variables
    cmdName = 'GetPowerLimit'
    cmdNum = Config.cmdGetPowerLimit
    netFn = Config.netFnDcmi

    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, [ 'dc', '00', '00' ])

    # Verify response completion code
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Completion Code correct: Success completion code.")
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Default Completion Code incorrect. Completion Code: " + \
            str(respData))
        return False

    # Parse variable values from response
    exceptionAction = int(respData[3], 16)
    powerLimit = int(respData[5] + respData[4], 16)
    correctionTime = int(respData[9] + respData[8] + \
        respData[7] + respData[6], 16)
    samplingPeriod = int(respData[13] + respData[12], 16)

    # Verify exception action
    if exceptionAction == Config.defaultPowerLimitExceptionAction:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default value correct for Exception Action: " + \
            str(exceptionAction))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Default Value incorrect for Exception Action. Expected: " + \
            str(Config.defaultPowerLimitExceptionAction) + \
            " Actual: " + str(exceptionAction))
        cmdPassOrFail = False

    # Verify power limit
    if powerLimit == Config.defaultPowerLimit:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Value correct for Power Limit: " + \
           str(powerLimit))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Default Value incorrect for Power Limit. Expected: " + \
            str(Config.defaultPowerLimit) + \
            " Actual: " + str(powerLimit))
        cmdPassOrFail = False

    # Verify correction time
    if correctionTime == Config.defaultPowerLimitCorrectionTime:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Value correct for Correction Time: " + \
            str(correctionTime))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Default Value incorrect for Correction Time. Expected: " + \
            str(Config.defaultPowerLimitCorrectionTime) + \
            " Actual: " + str(correctionTime))
        cmdPassOrFail = False

    # Verify sampling period
    if samplingPeriod == Config.defaultPowerLimitSamplingPeriod:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Value correct for Sampling Period: " + \
            str(samplingPeriod))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Default Value incorrect for for Sampling Period. Expected: " + \
            str(Config.defaultPowerLimitSamplingPeriod) + \
            " Actual: " + str(samplingPeriod))
        cmdPassOrFail = False

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    # Send raw bytes for Send Message (Activate Power Limit - De-Activate)
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnDcmi, Config.cmdActivatePowerLimit, \
        [ 'DC', '00', '00', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info('Send Message (Activate Power Limit - De-Activate)' + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.info('Send Message (Activate Power Limit - De-Activate)' + \
            ": Command failed. Completion Code: " + str(respData))

    return cmdPassOrFail