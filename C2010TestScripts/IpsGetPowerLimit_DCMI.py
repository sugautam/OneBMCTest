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

import time

import Config
import IpmiUtil
import UtilLogger

# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info('Setup: running Setup fxn')

    return True

# Function will test default values for
# Get Power Limit
def Execute(interfaceParams):

    # Define Test variables
    testPassOrFail = True
    respData = None

    # Test 1: 
    # Set Power Limit (500 W) ->
    # Activate Power Limit (activate) ->
    # Get Power Limit ->
    # Activate Power Limit (de-activate)

    # Send raw bytes for Set Power Limit (500 W)
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnDcmi, Config.cmdSetPowerLimit, \
        [ 'DC', '00', '00', '00', '00', 'F4', '01', '00', \
        '00', '00', '00', '00', '00', '01', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info('Set Power Limit (500 W)' + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.info('Set Power Limit (500 W)' + \
            ": Command failed. Completion Code: " + str(respData))
    testPassOrFail &= cmdPassOrFail

    # Send raw bytes for Activate Power Limit - Activate
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnDcmi, Config.cmdActivatePowerLimit, \
        [ 'DC', '01', '00', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info('Activate Power Limit - Activate' + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.info('Activate Power Limit - Activate' + \
            ": Command failed. Completion Code: " + str(respData))
    testPassOrFail &= cmdPassOrFail

    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnDcmi, Config.cmdGetPowerLimit, \
        [ 'DC', '00', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info('Get Power Limit' + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.info('Get Power Limit' + \
            ": Command failed. Completion Code: " + str(respData))
    testPassOrFail &= cmdPassOrFail

    # Send raw bytes for Send Message (Activate Power Limit - De-Activate)
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnDcmi, Config.cmdActivatePowerLimit, \
        [ 'DC', '00', '00', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info('Activate Power Limit - De-Activate' + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.info('Activate Power Limit - De-Activate' + \
            ": Command failed. Completion Code: " + str(respData))
    testPassOrFail &= cmdPassOrFail

    # Sleep for 5 seconds before startings Test 2
    UtilLogger.verboseLogger.info('Sleeping for 5 seconds...')
    time.sleep(5)

    # Test 2: 
    # Set Power Limit (500 W) ->
    # Activate Power Limit (activate) ->
    # Sleep for 500 ms
    # Get Power Limit ->
    # Activate Power Limit (de-activate)

    # Send raw bytes for Set Power Limit (500 W)
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnDcmi, Config.cmdSetPowerLimit, \
        [ 'DC', '00', '00', '00', '00', 'F4', '01', '00', \
        '00', '00', '00', '00', '00', '01', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info('Set Power Limit (500 W)' + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.info('Set Power Limit (500 W)' + \
            ": Command failed. Completion Code: " + str(respData))
    testPassOrFail &= cmdPassOrFail

    # Send raw bytes for Send Message (Activate Power Limit - Activate)
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnDcmi, Config.cmdActivatePowerLimit, \
        [ 'DC', '01', '00', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info('Activate Power Limit - Activate' + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.info('Activate Power Limit - Activate' + \
            ": Command failed. Completion Code: " + str(respData))
    testPassOrFail &= cmdPassOrFail

    # Sleep for 500 ms
    UtilLogger.verboseLogger.info('Sleeping for 500 ms...')
    time.sleep(0.5)

    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnDcmi, Config.cmdGetPowerLimit, \
        [ 'DC', '00', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info('Get Power Limit' + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.info('Get Power Limit' + \
            ": Command failed. Completion Code: " + str(respData))
    testPassOrFail &= cmdPassOrFail

    # Send raw bytes for Send Message (Activate Power Limit - De-Activate)
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnDcmi, Config.cmdActivatePowerLimit, \
        [ 'DC', '00', '00', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info('Activate Power Limit - De-Activate' + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.info('Activate Power Limit - De-Activate' + \
            ": Command failed. Completion Code: " + str(respData))
    testPassOrFail &= cmdPassOrFail

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info('Cleanup: running Cleanup fxn')

    return True
