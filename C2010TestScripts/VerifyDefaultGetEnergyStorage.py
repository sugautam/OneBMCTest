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

    UtilLogger.verboseLogger.info(\
        "VerifyDefaultGetEnergyStorage.py: running Setup fxn")

    return True

# Function will test default values for
# Get Energy Storage
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetEnergyStorage variables
    cmdName = 'GetEnergyStorage'
    cmdNum = Config.cmdGetEnergyStorage
    netFn = Config.netFnOem30

    # Send raw bytes via IpmiUtil
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
        netFn, cmdNum, [])

    # Verify response completion code
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default Completion Code correct: Success completion code.")
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default Completion Code incorrect. Completion Code: " + \
            str(respData))
        return False

    # Parse variable values from response
    presence = int(respData[0], 16) & 1 # bit [0]
    energyState = (int(respData[0], 16) & 28) >> 2 # bits [4:2]
    scalingFactor = int(respData[2], 16)
    backupEnergyBlade = int(respData[4] + respData[3], 16)
    backupEnergyNvdimm = int(respData[5], 16)
    rollingCounter = int(respData[7] + respData[6], 16)

    # Verify presence
    if presence == Config.defaultGetEnergyStoragePresence:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for Presence: " + \
            str(presence))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for Presence Action. Expected: " + \
            str(Config.defaultGetEnergyStoragePresence) + \
            " Actual: " + str(presence))
        cmdPassOrFail = False

    # Verify energy state
    if energyState == Config.defaultGetEnergyStorageEnergyState:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for Energy State: " + \
            str(energyState))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for Energy State. Expected: " + \
            str(Config.defaultGetEnergyStorageEnergyState) + \
            " Actual: " + str(energyState))
        cmdPassOrFail = False 

    # Verify scaling factor
    if scalingFactor == Config.defaultGetEnergyStorageScalingFactor:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for Scaling Factor: " + \
            str(scalingFactor))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for Scaling Factor. Expected: " + \
            str(Config.defaultGetEnergyStorageScalingFactor) + \
            " Actual: " + str(scalingFactor))
        cmdPassOrFail = False

    # Verify backup energy for blade
    if backupEnergyBlade == Config.defaultGetEnergyStorageBackupEnergyBlade:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for Backup Energy for Blade: " + \
            str(backupEnergyBlade))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for Backup Energy for Blade. Expected: " + \
            str(Config.defaultGetEnergyStorageBackupEnergyBlade) + \
            " Actual: " + str(backupEnergyBlade))
        cmdPassOrFail = False

    # Verify backup energy for nvdimm
    if backupEnergyNvdimm == Config.defaultGetEnergyStorageBackupEnergyNvdimm:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for Backup Energy for NvDimm: " + \
            str(backupEnergyNvdimm))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for Backup Energy for NvDimm. Expected: " + \
            str(Config.defaultGetEnergyStorageBackupEnergyNvdimm) + \
            " Actual: " + str(backupEnergyNvdimm))
        cmdPassOrFail = False

    # Verify rolling counter
    if rollingCounter == Config.defaultGetEnergyStorageRollingCounter:
        UtilLogger.verboseLogger.info(cmdName + \
            ": default value correct for Rolling Counter: " + \
            str(rollingCounter))
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": default value incorrect for Rolling Counter. Expected: " + \
            str(Config.defaultGetEnergyStorageRollingCounter) + \
            " Actual: " + str(rollingCounter))
        cmdPassOrFail = False

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info(\
        "VerifyDefaultGetEnergyStorage.py: running Cleanup fxn")

    return True