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

    UtilLogger.verboseLogger.info("VerifyGetProcessorInfo.py: running Setup fxn")

    return True

# Function will test completion code for Get Processor Info
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetProcessorInfo variables
    cmdName = 'GetProcessorInfo'
    cmdNum = Config.cmdGetProcessorInfo
    netFn = Config.netFnOem30

    # Define sample raw bytes (2 CPUs in Mt Olympus)
    for idx in range(0, 2):

        # Set rawByte to cpu index
        cpuIdx = hex(idx).lstrip('0x')
        if idx == 0:
            cpuIdx = '0'
        rawBytesList = [ cpuIdx ]

        # Send raw bytes via IpmiUtil
        cpuPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
            netFn, cmdNum, rawBytesList)

        # Verify response
        if cpuPassOrFail:
            UtilLogger.verboseLogger.info(cmdName + \
                ": Command passed for cpu 0x"\
                + cpuIdx + ": " + str(respData))
        else:
            UtilLogger.verboseLogger.error(cmdName + \
                ": Command failed for cpu 0x" + cpuIdx + \
                ". Completion Code: " + str(respData))

        cmdPassOrFail &= cpuPassOrFail

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifyGetProcessorInfo.py: running Cleanup fxn")

    return True