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

    UtilLogger.verboseLogger.info(\
        "VerifyDefaultGetDefaultPowerLimit.py: running Setup fxn")

    return True

# Function will test default values for
# Get Default Power Limit
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = False
    respData = None

    # Define GetDefaultPowerLimit variables
    cmdName = 'GetDefaultPowerLimit'
    cmdNum = Config.cmdGetDefaultPowerLimit
    netFn = Config.netFnOem30

    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, [])

    # Verify response completion code
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Value correct: Success completion code.")
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Default Completion Code incorrect. Completion Code: " + \
            str(respData))
        return False

    # Verify default power limit
    if int(respData[1] + respData[0], 16) == Config.defaultDefaultPowerLimit:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Value correct for default power limit: " + \
           str(int(respData[1] + respData[0], 16)))
    else:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Value incorrect for Default Power Limit. Expected: " + \
            str(Config.defaultDefaultPowerLimit) + \
            " Actual: " + str(int(respData[1] + respData[0])))
        cmdPassOrFail = False

    # Verify Delay Interval
    if int(respData[3] + respData[2], 16) == Config.defaultDelayInterval:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Value correct for delay interval: " + \
            str(int(respData[3] + respData[2], 16)))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Default Value incorrect for delay interval. Expected: " + \
            str(Config.defaultDelayInterval) + \
            " Actual: " + str(int(respData[3] + respData[2], 16)))
        cmdPassOrFail = False

    # Verify Bmc Action
    if int(respData[4], 16) == Config.defaultBmcAction:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Value correct for Bmc Action: " + \
            str(int(respData[4], 16)))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Default Value incorrect for for Bmc Action. Expected: " + \
            str(Config.defaultBmcAction) + \
            " Actual: " + str(int(respData[4], 16)))
        cmdPassOrFail = False

    # Verify Auto Remove Dpc Delay
    if int(respData[5], 16) == Config.defaultAutoRemoveDpcDelay:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Value correct for Auto Remove Dpc Delay: " + \
            str(int(respData[5], 16)))
    else:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Default Value incorrect for Auto Remove Dpc Delay. Expected: " + \
            str(Config.defaultAutoRemoveDpcDelay) + \
            " Actual: " + str(int(respData[5], 16)))
        cmdPassOrFail = False

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info(\
        "VerifyDefaultGetDefaultPowerLimit.py: running Cleanup fxn")

    return True