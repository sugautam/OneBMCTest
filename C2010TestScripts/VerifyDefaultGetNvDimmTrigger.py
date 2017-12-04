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
        "VerifyDefaultGetNvDimmTrigger.py: running Setup fxn")

    return True

# Function will test default values for
# Get NVDIMM_TRIGGER
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetNvDimmTrigger variables
    cmdName = 'GetNvDimmTrigger'
    cmdNum = Config.cmdGetNvDimmTrigger
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
    adrTriggerStatus = int(respData[0], 16) & 7 # bits [2:0]
    adrCompletePowerOffDelay = int(respData[1], 16)
    nvdimmPresentPowerOffDelay = int(respData[2], 16)

    # Verify ADR_TRIGGER status byte
    if adrTriggerStatus == Config.defaultGetNvDimmTriggerAdrTriggerStatus:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for ADR_TRIGGER Status: " + \
            str(adrTriggerStatus))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for ADR_TRIGGER Status. Expected: " + \
            str(Config.defaultGetNvDimmTriggerAdrTriggerStatus) + \
            " Actual: " + str(adrTriggerStatus))
        cmdPassOrFail = False

    # Verify ADR COMPLETE power-off delay
    if adrCompletePowerOffDelay == \
        Config.defaultGetNvDimmTriggerAdrCompletePowerOffDelay:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for ADR COMPLETE Power-Off Delay: " + \
            str(adrCompletePowerOffDelay))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for ADR COMPLETE Power-Off Delay. Expected: " + \
            str(Config.defaultGetNvDimmTriggerAdrCompletePowerOffDelay) + \
            " Actual: " + str(adrCompletePowerOffDelay))
        cmdPassOrFail = False

    # Verify NVDIMM present power-off delay
    if nvdimmPresentPowerOffDelay == \
        Config.defaultGetNvDimmTriggerNvDimmPresentPowerOffDelay:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for NVDIMM Present Power-Off Delay: " + \
            str(nvdimmPresentPowerOffDelay))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for NVDIMM Present Power-Off Delay. Expected: " + \
            str(Config.defaultGetNvDimmTriggerNvDimmPresentPowerOffDelay) + \
            " Actual: " + str(nvdimmPresentPowerOffDelay))
        cmdPassOrFail = False

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info(\
        "VerifyDefaultGetNvDimmTrigger.py: running Cleanup fxn")

    return True