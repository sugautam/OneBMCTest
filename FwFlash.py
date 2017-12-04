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

from subprocess import Popen, PIPE

import os

import Config
import UtilLogger

# Function runs input command
# on specified Fw Flash and returns response
def RunFwFlash(fwFlashFilePath, *args):
    
    # Initialize varaibles for RunFwFlash
    returnOut = ''
    err = ''
    fwFlashAbsFilePath = os.path.abspath(fwFlashFilePath)

    try:

        # Create parameter list to run on shell
        processCmd = [ fwFlashAbsFilePath ]
        for arg in args:
            for param in arg:
                processCmd.append(param)

        # Print additional output to verbose log
        # if debugEn is True
        if Config.debugEn:
            commandRun = ""
            for arg in args:
                for param in arg:
                    commandRun += " " + str(param)
            UtilLogger.verboseLogger.info("RunFwFlash: Command run by " + \
                "Fw Flash program " + str(fwFlashAbsFilePath) + ": " + \
                commandRun)

        # Run Fw Flash and get stdout and stderr
        process = Popen(processCmd, stdout=PIPE, stderr=PIPE,\
            cwd=os.path.dirname(fwFlashAbsFilePath))

        # Print additional output to verbose log
        # if debugEn is True
        if Config.debugEn:
            UtilLogger.verboseLogger.info("RunFwFlash: Command output by Fw " + \
                "Flash program " + fwFlashAbsFilePath + ": ")

        # Periodically poll the process to obtain
        # stdout and stderr
        while True:
            out = process.stdout.readline()
            returnOut += out
            if out == '' and process.poll() is not None:
                break
            if out and Config.debugEn:
                UtilLogger.verboseLogger.info(out)

        # Get Stderr
        err = process.stderr.read()

        # Check return code
        returnCode = process.poll()
        if int(returnCode) != 0:
            err = "Error return code: " + str(returnCode) + \
                " Error output: " + err

    except KeyboardInterrupt:
        UtilLogger.verboseLogger.error("RunFwFlash: " + \
            "keyboard interrupt exception occurred ")
        if returnOut and Config.debugEn:
            UtilLogger.verboseLogger.info("RunFwFlash: stdout prior to exception: " + \
                str(returnOut))
        raise
    except Exception, e:
        UtilLogger.verboseLogger.error("RunFwFlash: exception occurred for " + \
            "Fw Flash program " + str(fwFlashAbsFilePath) + ": " + str(e))
        if returnOut and Config.debugEn:
            UtilLogger.verboseLogger.info("RunFwFlash: stdout prior to exception: " + \
                str(returnOut))

    return returnOut, err

# Function will flash BMC FW
# using YafuFlash via KCS or Ipmi over LAN+
def YafuFlashBmcFw(fwBinPath, ip, user, pwd):

    flashPassOrFail = False
    processCmd = []
    fwBinAbsPath = os.path.abspath(fwBinPath)

    # Determine if running KCS or IPMI over LAN+
    # and contruct command line accordingly
    if not ip: # Kcs
        processCmd.append(Config.yafuFlashKcsSwitch)
        processCmd.append(Config.yafuFlashForceFlashSwitch)
        processCmd.append(Config.yafuFlashNetfnSwitch)
        processCmd.append(Config.yafuFlashNetfnBmcValue)
        processCmd.append(Config.yafuFlashChipSelectSwitch)
        processCmd.append(Config.yafuFlashChipSelectDefaultValue)
        processCmd.append(fwBinAbsPath)
    else: # Ipmi over LAN+
        processCmd.append(Config.yafuFlashLanSwitch)
        processCmd.append(Config.yafuFlashForceFlashSwitch)
        processCmd.append(Config.yafuFlashNetfnSwitch)
        processCmd.append(Config.yafuFlashNetfnBmcValue)
        processCmd.append(Config.yafuFlashChipSelectSwitch)
        processCmd.append(Config.yafuFlashChipSelectDefaultValue)
        processCmd.append(Config.yafuFlashIpAddressSwitch)
        processCmd.append(ip)
        processCmd.append(Config.yafuFlashUserSwitch)
        processCmd.append(user)
        processCmd.append(Config.yafuFlashPasswordSwitch)
        processCmd.append(pwd)
        processCmd.append(fwBinAbsPath)

    UtilLogger.verboseLogger.info("YafuFlashBmcFw: Flashing BMC FW with " + \
        "binary at filepath " + fwBinAbsPath)

    # Set the yafuFlashFilePath based on current OS
    yafuFlashFilePath = ''
    if Config.currentOs == Config.osNameWindows: # Windows
        yafuFlashFilePath = Config.yafuFlashFilePath
    elif Config.currentOs == Config.osNameLinux: # Linux
        yafuFlashFilePath = Config.yafuFlashLinuxFilePath

    # Process command using RunFwFlash
    out, err = RunFwFlash(yafuFlashFilePath, processCmd)
    if err:
        UtilLogger.verboseLogger.error("Received error for RunFwFlash: " + err)
    else:
        UtilLogger.verboseLogger.info("Successfully flashed BMC FW with filepath: " + \
            fwBinAbsPath)
        flashPassOrFail = True

    return flashPassOrFail

# Function will flash BMC Fw
# using SocFlsah via KCS
def SocFlashBmcFw(fwBinPath, chipSelect):

    flashPassOrFail = False
    processCmd = []

    # Make sure utility running in KCS
    if Config.bmcIpAddress:
        UtilLogger.verboseLogger.info("SocFlashBmcFw: " + \
            "not running in KCS. Will not Flash Bmc Fw.")
        return flashPassOrFail

    # Contruct command line for KCS
    processCmd.append(Config.socFlashOptionSwitch + \
        Config.socFlashOptionValue)
    processCmd.append(Config.socFlashCSSwitch + \
        str(chipSelect))
    processCmd.append(Config.socFlashFlashTypeSwitch + \
        Config.socFlashFlashTypeBmcValue)
    processCmd.append(Config.socFlashLpcPortSwitch + \
        Config.socFlashLpcPortValue)
    processCmd.append(Config.socFlashBinPathSwitch + \
        fwBinPath)

    UtilLogger.verboseLogger.info("SocFlashBmcFw: Flashing BMC FW with " + \
        "binary at filepath " + fwBinPath)

    # Process command using RunFwFlash
    out, err = RunFwFlash(Config.socFlashFilePath, processCmd)
    if err:
        UtilLogger.verboseLogger.error("SocFlashBmcFw: " + \
            "received error for RunFwFlash - " + err)
    else:
        UtilLogger.verboseLogger.info("SocFlashBmcFw: " + \
            "successfully flashed BMC FW with filepath - " + \
            fwBinPath)
        flashPassOrFail = True

    return flashPassOrFail

# Function will flash CPLD FW
# using YafuFlash via KCS or Ipmi over Lan+
def YafuFlashCpldFw(fwBinPath, ip, user, pwd):

    flashPassOrFail = False
    processCmd = []
    fwBinAbsPath = os.path.abspath(fwBinPath)

    # Determine if running KCS or IPMI over LAN+
    # and contruct command line accordingly
    if not ip: # Kcs
        processCmd.append(Config.yafuFlashKcsSwitch)
        processCmd.append(Config.yafuFlashForceFlashSwitch)
        processCmd.append(Config.yafuFlashNetfnSwitch)
        processCmd.append(Config.yafuFlashNetfnCpldValue)
        processCmd.append(Config.yafuFlashPeripheralSwitch)
        processCmd.append(Config.yafuFlashPeripheralCpldValue)
        processCmd.append(fwBinAbsPath)
    else: # Ipmi over LAN+
        processCmd.append(Config.yafuFlashLanSwitch)
        processCmd.append(Config.yafuFlashForceFlashSwitch)
        processCmd.append(Config.yafuFlashNetfnSwitch)
        processCmd.append(Config.yafuFlashNetfnCpldValue)
        processCmd.append(Config.yafuFlashPeripheralSwitch)
        processCmd.append(Config.yafuFlashPeripheralCpldValue)
        processCmd.append(Config.yafuFlashIpAddressSwitch)
        processCmd.append(ip)
        processCmd.append(Config.yafuFlashUserSwitch)
        processCmd.append(user)
        processCmd.append(Config.yafuFlashPasswordSwitch)
        processCmd.append(pwd)
        processCmd.append(fwBinAbsPath)

    UtilLogger.verboseLogger.info("YafuFlashBmcFw: Flashing CPLD FW with " + \
        "binary at filepath " + fwBinAbsPath)

    # Process command using RunFwFlash
    out, err = RunFwFlash(Config.yafuFlashFilePath, processCmd)
    if err:
        UtilLogger.verboseLogger.error("Received error for RunFwFlash: " + err)
    else:
        UtilLogger.verboseLogger.info("Successfully flash CPLD FW with filepath: " + \
            fwBinAbsPath)
        flashPassOrFail = True

    return flashPassOrFail

# Function will compare Bmc Fw version
# and state which is newer
# Inputs (all type int): 
#   maj1: Bmc Fw major value of first input
#   min1: Bmc Fw minor value of first input
#   aux1: Bmc Fw aux value of first input
#   maj2: Bmc Fw major value of second input
#   min2: Bmc Fw minor value of second input
#   aux2: Bmc Fw aux value of second input
# Output:
#   compareOut:
#       1: first input is newer (greater) than second input
#       0: first and second input are equal
#      -1: first input is older (less) than second input
def CompareBmcFwVersion(maj1, min1, aux1,\
    maj2, min2, aux2):

    # initialize variables
    compareOut = 0

    # check if both are equal
    if maj1 == maj2 and \
        min1 == min2 and \
        aux1 == aux2:
        compareOut = 0
    # check if maj1 is newer than maj2
    elif maj1 > maj2 or \
        (maj1 == maj2 and min1 > min2) or \
        (maj1 == maj2 and min1 == min2 and \
        aux1 > aux2):
        compareOut = 1
    # otherwise, input 1 < input2
    else:
        compareOut = -1

    return compareOut

# Function will extract Bmc Fw version
# from GetDeviceId response
def extractBmcFwGetDeviceId(respData):

    # Initialize variables
    majIndex = 2
    minIndex = 3
    auxIndex = 11

    # Return maj, min, aux
    maj = int(respData[majIndex], 16)
    min = int(respData[minIndex], 16)
    aux = int(respData[auxIndex], 16)

    return maj, min, aux