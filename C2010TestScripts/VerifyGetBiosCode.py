﻿# OneBMCTest
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

    UtilLogger.verboseLogger.info("VerifyGetBiosCode.py: running Setup fxn")

    return True

# Function will test completion code for Get Bios Code
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetBiosCode variables
    cmdName = 'GetBiosCode'
    cmdNum = Config.cmdGetBiosCode
    netFn = Config.netFnOem32

    # Define sample raw bytes for 
    # Current (0x00) BIOS POST code
    rawBytesList = [ '00' ]

    # Send raw bytes via IpmiUtil
    biosPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if biosPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for current BIOS Code: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for current BIOS Code."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= biosPassOrFail

    # Define sample raw bytes for 
    # Previous (0x01) BIOS POST code
    rawBytesList = [ '01' ]

    # Send raw bytes via IpmiUtil
    biosPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if biosPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for previous BIOS Code: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for previous BIOS Code."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= biosPassOrFail

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifyGetBiosCode.py: running Cleanup fxn")

    return True