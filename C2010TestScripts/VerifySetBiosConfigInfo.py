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

    UtilLogger.verboseLogger.info("VerifySetBiosConfigInfo.py: running Setup fxn")

    return True

# Function will test completion code for Set Bios Config Info
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = False
    respData = None

    # Define SetBiosConfigInfo variables
    cmdName = 'SetBiosConfigInfo'
    cmdNum = Config.cmdSetBiosConfigInfo
    netFn = Config.netFnOem38

    # Define sample raw bytes for Set Bios Config Info 
    # (current: default BIOS config; and all available BIOS configs)
    rawBytesList = \
        [ '00', '00', 'bc', '66', '69', '00', '00', '00',\
        '00', '00', '00', '01', '00', '00', '00', '00',\
        '00', '18', 'b2', '66', '69', '00', '00', '00',\
        '00', '18', '00', '00', '03', '00', '00', '00',\
        '00', '00', '00', 'ff', 'ff', 'ff', 'ff', '00',\
        '40', '02', '06', '7f', '00', '00', '00', '00',\
        '03', '07', '7f', '00', '00', '00', '00', '03',\
        '08', '7f', '00', '00', '00', '00', '03', '09',\
        '46', '60', '09', '00', '40', '02', '0a', '7f',\
        '00', '00', '00', '00', '03', '0b', '46', '60',\
        '09', '00', '40', '02', '0c', '7f', '00', '00',\
        '00', '00', '03', '0d', '7f', '00', '00', '00',\
        '00', '03', '0e', '7f', '00', '00', '00', '00',\
        '03', '0f', '7f', '00', '00', '00', '00', '03',\
        '10', '7f', '00', '00', '00', '00', '03', '11',\
        '7f', '00', '00', '00', '00', '03', '12', '7f',\
        '00', '00', '00', '00', '03', '13', '7f', '00',\
        '00', '00', '00', '03', '14', '7f', '00', '00',\
        '00', '00', '03', '15', '7f', '00', '00', '00',\
        '00', '03', '16', '7f', '00', '00', '00', '00',\
        '03', '17', '7f', '00', '00', '00', '00', '03',\
        '18', '7f', '00', '00', '00', '00', '03', '00',\
        '00', '00', '00', '00', '00', '00', '00', '00',\
        '00', '00', '00', '00', '00', '00', '00', '00',\
        '00', '00', '00', '00', '00', '00', '00', '00' ]
        
    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed. Completion Code: " + str(respData))

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifySetBiosConfigInfo.py: running Cleanup fxn")

    return True