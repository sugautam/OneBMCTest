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
        "VerifyDefaultGetBiosConfig.py: running Setup fxn")

    return True

# Function will test default values for
# Get Bios Config
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetBiosConfig variables
    cmdName = 'GetBiosConfig'
    cmdNum = Config.cmdGetBiosConfig
    netFn = Config.netFnOem38

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
    currentBiosConfiguration = int(respData[0], 16)
    chosenBiosConfiguration = int(respData[1], 16)

    # Verify current Bios configuration
    if currentBiosConfiguration == Config.defaultCurrentBiosConfiguration:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for Current BIOS Configuration: " + \
            str(currentBiosConfiguration))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for Current BIOS Configuration. Expected: " + \
            str(Config.defaultCurrentBiosConfiguration) + \
            " Actual: " + str(currentBiosConfiguration))
        cmdPassOrFail = False

    # Verify chosen Bios configuration
    if chosenBiosConfiguration == Config.defaultChosenBiosConfiguration:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for Chosen BIOS Configuration: " + \
            str(chosenBiosConfiguration))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for Chosen BIOS Configuration. Expected: " + \
            str(Config.defaultChosenBiosConfiguration) + \
            " Actual: " + str(chosenBiosConfiguration))
        cmdPassOrFail = False

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info(\
        "VerifyDefaultGetBiosConfig.py: running Cleanup fxn")

    return True