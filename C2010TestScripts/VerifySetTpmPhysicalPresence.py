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

    UtilLogger.verboseLogger.info("VerifySetTpmPhysicalPresence.py: running Setup fxn")

    return True

# Function will test completion code for Set TPM Physical Presence
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define SetTpmPhysicalPresence variables
    cmdName = 'SetTpmPhysicalPresence'
    cmdNum = Config.cmdSetTpmPhysicalPresence
    netFn = Config.netFnOem38

    # Define sample raw byte for 
    # TPM Physical Presence to 
    # not asserted (0x00 == flag is false)
    rawBytesList = [ '00' ]

    # Send raw bytes via IpmiUtil
    tpmPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if tpmPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for Physical Presence not asserted: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for Physical Presence not asserted."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= tpmPassOrFail

    # Define sample raw byte for 
    # TPM Physical Presence to 
    # asserted (0x01 == flag is true)
    rawBytesList = [ '01' ]

    # Send raw bytes via IpmiUtil
    tpmPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if tpmPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for Physical Presence asserted: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for Physical Presence asserted."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= tpmPassOrFail

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifySetTpmPhysicalPresence.py: running Cleanup fxn")

    return True