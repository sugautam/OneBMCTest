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

    UtilLogger.verboseLogger.info("VerifyGetSessionChallenge.py: running Setup fxn")

    return True

# Function will test completion code for Get Session Challenge
def Execute(interfaceParams):

    # Check if running in KCS
    # if so, exit test
    if interfaceParams:
        UtilLogger.verboseLogger.info("VerifyGetSessionChallenge" + \
            ": currently running commands KCS. Will not execute.")
        return True

    # Define Test variables
    cmdPassOrFail = False
    respData = None

    # Define GetSessionChallenge variables
    cmdName = 'GetSessionChallenge'
    cmdNum = Config.cmdGetSessionChallenge
    netFn = Config.netFnApp

    # Define sample raw bytes for Get Session Challenge
    # Raw bytes defined as 'admin' user name with MD5 authentication type
    rawBytesList = \
        [ '02', '61', '64', '6d', '69', '6e', '00', '00',\
        '00', '00', '00', '00', '00', '00', '00', '00',\
        '00' ]
        
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

    UtilLogger.verboseLogger.info("VerifyGetSessionChallenge.py: running Cleanup fxn")

    return True