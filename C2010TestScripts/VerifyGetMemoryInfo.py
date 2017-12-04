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

    UtilLogger.verboseLogger.info("VerifyGetMemoryInfo.py: running Setup fxn")

    return True

# Function will test completion code for Get Memory Info
# NOTE: memory index range should go in a config file
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetMemoryInfo variables
    cmdName = 'GetMemoryInfo'
    cmdNum = Config.cmdGetMemoryInfo
    netFn = Config.netFnOem30

    # Define sample raw bytes (24 dimm slots in Mt Olympus)
    for idx in range(0, 25):

        # Set rawByte to memory index
        dimmIdx = hex(idx).lstrip('0x')
        if idx == 0:
            dimmIdx = '0'
        rawBytesList = [ dimmIdx ]

        # Send raw bytes via IpmiUtil
        dimmPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
            netFn, cmdNum, rawBytesList)

        # Verify response
        if dimmPassOrFail:
            UtilLogger.verboseLogger.info(cmdName + \
                ": Command passed for dimm 0x"\
                + dimmIdx + ": " + str(respData))
        else:
            UtilLogger.verboseLogger.error(cmdName + \
                ": Command failed for dimm 0x" + dimmIdx + \
                ". Completion Code: " + str(respData))

        cmdPassOrFail &= dimmPassOrFail

    return cmdPassOrFail 

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifyGetMemoryInfo.py: running Cleanup fxn")

    return True