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
        "VerifyDefaultSetPowerRestorePolicy.py: running Setup fxn")

    return True

# Function will test default values for
# Set Power Restore Policy
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define SetPowerRestorePolicy variables
    cmdName = 'SetPowerRestorePolicy'
    cmdNum = Config.cmdSetPowerRestorePolicy
    netFn = Config.netFnChassis

    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, [ '03' ])

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
    powerRestorePolicySupport = int(respData[0], 16) & 7 # [2:0]

    # Verify power restore policy support
    if powerRestorePolicySupport == Config.defaultPowerRestorePolicySupport:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for Power Restore Policy Support: " + \
            str(powerRestorePolicySupport))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for Power Restore Policy Support. Expected: " + \
            str(Config.defaultPowerRestorePolicySupport) + \
            " Actual: " + str(powerRestorePolicySupport))
        cmdPassOrFail = False

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info(\
        "VerifyDefaultSetPowerRestorePolicy.py: running Cleanup fxn")

    return True