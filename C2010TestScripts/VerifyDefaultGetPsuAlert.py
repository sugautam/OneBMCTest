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

    UtilLogger.verboseLogger.info(\
        "VerifyDefaultGetPsuAlert.py: running Setup fxn")

    return True

# Function will test default values for
# Get Psu Alert
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetPsuAlert variables
    cmdName = 'GetPsuAlert'
    cmdNum = Config.cmdGetPsuAlert
    netFn = Config.netFnOem30

    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, [])

    # Verify response completion code
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default Completion Code correct: Success completion code.")
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default Completion Code incorrect. Completion Code: " + \
            str(respData))
        return False

    # Parse variable values from response
    psu1ThrottleNStatus = (int(respData[0], 16) & 64) >> 6 # PSU1_THROTTLE_N [6]
    rmThrottleEnNStatus = (int(respData[0], 16) & 16) >> 4 # RM_THROTTLE_EN_N [4]
    bmcForceNmThrottleNStatus = int(respData[0], 16) & 15 # BMC_FORCE_NM_THROTTLE_N [3:0]

    # Verify PSU1_THROTTLE_N status
    if psu1ThrottleNStatus == Config.defaultPsu1ThrottleNStatus:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for PSU1_THROTTLE_N status: " + \
            str(psu1ThrottleNStatus))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for PSU1_THROTTLE_N status. Expected: " + \
            str(Config.defaultPsu1ThrottleNStatus) + \
            " Actual: " + str(psu1ThrottleNStatus))
        cmdPassOrFail = False

    # Verify RM_THROTTLE_EN_N status
    if rmThrottleEnNStatus == Config.defaultRmThrottleEnNStatus:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for RM_THROTTLE_EN_N status: " + \
            str(rmThrottleEnNStatus))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for RM_THROTTLE_EN_N status. Expected: " + \
            str(Config.defaultRmThrottleEnNStatus) + \
            " Actual: " + str(rmThrottleEnNStatus))
        cmdPassOrFail = False

    # Verify BMC_FORCE_NM_THROTTLE_N status
    if bmcForceNmThrottleNStatus == Config.defaultBmcForceNmThrottleNStatus:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for BMC_FORCE_NM_THROTTLE_N status: " + \
            str(bmcForceNmThrottleNStatus))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for BMC_FORCE_NM_THROTTLE_N status. Expected: " + \
            str(Config.defaultBmcForceNmThrottleNStatus) + \
            " Actual: " + str(bmcForceNmThrottleNStatus))
        cmdPassOrFail = False

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info(\
        "VerifyDefaultGetPsuAlert.py: running Cleanup fxn")

    return True