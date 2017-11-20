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

# Define variables shared by
# functions
reservationId = []

# Setup Function
def Setup(interfaceParams):

    # Declare module-scope variables
    global reservationId

    # Define variables
    cmdPassOrFail = False
    respData = None

    # Define ReserveSel variables
    cmdName = 'ReserveSel'
    cmdNum = Config.cmdReserveSel
    netFn = Config.netFnStorage
        
    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, [])

    # Verify response
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed: " + str(respData))
        # Update reservationId variable with respData
        reservationId = respData

    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed. Completion Code: " + str(respData))

    return cmdPassOrFail

# Function will test completion code for Clear SEL
def Execute(interfaceParams):

    # Declare module-scope variables
    global reservationId

    # Define Test variables
    cmdPassOrFail = False
    respData = None

    # Define ClearSel variables
    cmdName = 'ClearSel'
    cmdNum = Config.cmdClearSel
    netFn = Config.netFnStorage

    # Define sample raw bytes for Clear Sel
    # Raw bytes defined as Initiate Erase
    rawBytesList = []
    for appendByte in reservationId:
        rawBytesList.append(appendByte)
    rawBytesList.append('43')
    rawBytesList.append('4C')
    rawBytesList.append('52')
    rawBytesList.append('AA')
    
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

    UtilLogger.verboseLogger.info("VerifyClearSel.py: running Cleanup fxn")

    return True