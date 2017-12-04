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

import time

import Config
import IpmiUtil
import UtilLogger

# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifyChassisControl.py: running Setup fxn")

    return True

# Function will test completion code for Chassis Control
def Execute(interfaceParams):

    # Test will not be conducted for KCS interface
    if not interfaceParams:
        UtilLogger.verboseLogger.error(\
            "VerifyChassisControl.py: Currently using KCS interface. " + \
            "Will not run test.")
        return True

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define ChassisControl variables
    cmdName = 'ChassisControl'
    cmdNum = Config.cmdChassisControl
    netFn = Config.netFnChassis

    # Define sample raw byte for 
    # power down (0x00)
    rawBytesList = [ '00' ]

    # Send raw bytes via IpmiUtil
    chassisCtrlPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if chassisCtrlPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for power down: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for power down."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= chassisCtrlPassOrFail

    # Define sample raw byte for 
    # power up (0x01)
    rawBytesList = [ '01' ]

    # Send raw bytes via IpmiUtil
    chassisCtrlPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if chassisCtrlPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for power up: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for power up."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= chassisCtrlPassOrFail

    # Define sample raw byte for 
    # power cycle (0x02)
    rawBytesList = [ '02' ]

    # Send raw bytes via IpmiUtil
    chassisCtrlPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if chassisCtrlPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for power cycle: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for power cycle."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= chassisCtrlPassOrFail

    # Define sample raw byte for 
    # hard reset (0x03)
    rawBytesList = [ '03' ]

    # Send raw bytes via IpmiUtil
    chassisCtrlPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if chassisCtrlPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for hard reset: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for hard reset."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= chassisCtrlPassOrFail

    # Define sample raw byte for 
    # diagnostic interrupt (0x04)
    rawBytesList = [ '04' ]

    # Send raw bytes via IpmiUtil
    chassisCtrlPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if chassisCtrlPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for diagnostic interrupt: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for diagnostic interrupt."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= chassisCtrlPassOrFail

    # Define sample raw byte for 
    # soft-shutdown (0x05)
    rawBytesList = [ '05' ]

    # Send raw bytes via IpmiUtil
    chassisCtrlPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify response
    if chassisCtrlPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for soft-shutdown: "\
            + str(respData))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed for soft-shutdown."\
            + " Completion Code: " + str(respData))

    cmdPassOrFail &= chassisCtrlPassOrFail

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifyChassisControl.py: running Cleanup fxn")

    return True