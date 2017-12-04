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

    UtilLogger.verboseLogger.info("VerifyGetFirmwareVersion.py: running Setup fxn")

    return True

# Function will test completion code for Get Firmware Version
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetFirmwareVersion variables
    cmdName = 'GetFirmwareVersion'
    cmdNum = Config.cmdGetFirmwareVersion
    netFn = Config.netFnOem38

    # Define sample raw byte for 
    # BIOS version (0x00)
    rawBytesList = [ '00' ]

    # Send raw bytes via IpmiUtil
    fwPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if fwPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for BIOS version: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for BIOS version."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= fwPassOrFail

    # Define sample raw byte for 
    # CPLD version (0x01)
    rawBytesList = [ '01' ]

    # Send raw bytes via IpmiUtil
    fwPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if fwPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for CPLD version: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for CPLD version."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= fwPassOrFail

    # Define sample raw byte for 
    # BMC version (0x02)
    rawBytesList = [ '02' ]

    # Send raw bytes via IpmiUtil
    fwPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if fwPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for BMC version: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for BMC version."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= fwPassOrFail

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifyGetFirmwareVersion.py: running Cleanup fxn")

    return True