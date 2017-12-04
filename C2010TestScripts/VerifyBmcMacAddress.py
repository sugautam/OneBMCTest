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

    UtilLogger.verboseLogger.info("VerifyBmcMacAddress.py: running Setup fxn")

    return True

# Function will test completion code for Get Device Id
def Execute(interfaceParams):

    # Define Test variables
    testPassOrFail = True
    respData = None

    # Define Master Write-Read Variables
    bmcMacEepromOffsetMsb = '18'
    bmcMacEepromOffsetLsb = '00'
    eepromBusId = '0D'
    eepromSlaveAddress = 'A8'
    bmcMacReadSize = '06'
    bmcEepromMacAddress = []
    bmcLanMacAddress = []
    lanChannel = '01'

    # Get BMC Mac Address via Master Write Read
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        Config.netFnApp, Config.cmdMasterWriteRead, \
        [ eepromBusId, eepromSlaveAddress, bmcMacReadSize,\
        bmcMacEepromOffsetMsb, bmcMacEepromOffsetLsb ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info("MasterWriteRead" + \
            ": Command passed: " + str(respData))
        bmcEepromMacAddress = respData
    else:
        UtilLogger.verboseLogger.error("MasterWriteRead" + \
            ": Command failed. Completion Code: " + str(respData))
    testPassOrFail &= cmdPassOrFail

    # Get BMC Mac Address via Get LAN Configuration Parameters
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        Config.netFnTransport, Config.cmdGetLanConfigurationParameters, \
        [ lanChannel, '05', '00', '00' ])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info("GetLanConfigurationParameters" + \
            ": Command passed: " + str(respData))
        bmcLanMacAddress = respData[1:] # Mac Address is bytes 1-6 of respData
    else:
        UtilLogger.verboseLogger.error("GetLanConfigurationParameters" + \
            ": Command failed. Completion Code: " + str(respData))
    testPassOrFail &= cmdPassOrFail

    # Compare BMC MAC Address in EEPROM with 
    #   BMC MAC Address via Get Lan Configuration Parameters
    if bmcEepromMacAddress and bmcLanMacAddress: # verify both are not empty
        if bmcEepromMacAddress == bmcLanMacAddress:
            UtilLogger.verboseLogger.info("VerifyBmcMacAddress" + \
                ": both MAC Addresses are the same. " + \
                "Bmc Mac Address in EEPROM: " + str(bmcEepromMacAddress) + \
                " Bmc Mac Address via Get Lan Configuration Parameters: " + \
                str(bmcLanMacAddress))
        else:
            UtilLogger.verboseLogger.error("VerifyBmcMacAddress" + \
                ": MAC Addresses do NOT match. " + \
                "Bmc Mac Address in EEPROM: " + str(bmcEepromMacAddress) + \
                " Bmc Mac Address via Get Lan Configuration Parameters: " + \
                str(bmcLanMacAddress))
            testPassOrFail = False
    else:
        UtilLogger.verboseLogger.info("VerifyBmcMacAddress" + \
            ": One of the MAC Addresses is empty. " + \
            "Bmc Mac Address in EEPROM: " + str(bmcEepromMacAddress) + \
            " Bmc Mac Address via Get Lan Configuration Parameters: " + \
            str(bmcLanMacAddress))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifyBmcMacAddress.py: running Cleanup fxn")

    return True