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
import time
import Config
import IpmiUtil
import UtilLogger
import re

# Function will calculate 2's complement integer (signed)
# using input hex string and number of bits
def calc2sComplementHexString2Int(hexInput, bitCount):

    # Initialize local variables
    twosComplement = None

    # Check if MSB is positive (0) or negative (1)
    if ((int(hexInput, 16) >> (bitCount - 1)) & 1):
        twosComplement = -1 * ((~int(hexInput, 16) + 1) & (2**bitCount-1))
    else:
        twosComplement = int(hexInput, 16) & (2**bitCount-1)

    return twosComplement

# Function will check if BMC is hung 
# If BMC is determined to be hung/failing,
# test configuration will be reset
def DetectAndRemoveBmcHang(interfaceParams):
    # Initialize variables
    detectAndRemovePassOrFail = False

    UtilLogger.verboseLogger.info("DetectAndRemoveBmcHang: " + \
        "Checking if BMC is hung by calling Get Device Id (retry count: " + \
        str(Config.bmcHangRetryCount) + ")")

    # Check if BMC is hung by trying to Get Device Id
    # BMC currently determined to be hung/failing if
    # BMC does not provide response after
    # the number of retries provided by BMC
    for retryCount in range(0, Config.bmcHangRetryCount):

        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams,\
            Config.netFnApp, Config.cmdGetDeviceId, [])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetDeviceId: " + \
                "Command passed (retry count: " + \
                str(retryCount) + "): " + str(respData))
            detectAndRemovePassOrFail = True
            break
        else:
            if not respData:
                UtilLogger.verboseLogger.error("GetDeviceId: " + \
                    "Command failed (retry count: " + \
                    str(retryCount) + "). No response: " + str(respData))
            else:
                UtilLogger.verboseLogger.info("GetDeviceId: " + \
                    "Command failed (retry count: " + \
                    str(retryCount) + "). Completion Code: " + str(respData))
                detectAndRemovePassOrFail = True
                break

    if not detectAndRemovePassOrFail: # BMC determined to be hung/failing

        UtilLogger.verboseLogger.info("DetectAndRemoveBmcHang: " + \
            "BMC determined to be hung or failing. Resetting the " + \
            "test configuration.")

        # Reset test config (ie AC Power Cycle blade)
        try:
            import AcPowerIpSwitch
            detectAndRemovePassOrFail = AcPowerIpSwitch.AcPowerCycleBlade(interfaceParams)
        except Exception, e:
            UtilLogger.verboseLogger.error("DetectAndRemoveBmcHang: " + \
                "unable to AC Power Cycle blade due to exception - " + \
                str(e))

        # Check if AC Power Cycle fixed BMC hang by getting and clearing SELs
        UtilLogger.verboseLogger.info("DetectAndRemoveBmcHang: " + \
        "Checking if BMC hang is fixed by getting and clearing SELs.")

        # Get Sel entries
        processCmd = ['sel', '-u']
        for interfaceParam in interfaceParams:
            processCmd.append(interfaceParam)
        out, err = IpmiUtil.RunIpmiUtil(processCmd)
        if err:
            UtilLogger.verboseLogger.error("DetectAndRemoveBmcHang: " + \
                "SEL entries error: " + str(err))
            return False
        else:
            UtilLogger.verboseLogger.info("DetectAndRemoveBmcHang.py: " + \
                "SEL entries: \n" + str(out))
            detectAndRemovePassorFail = True

        # Reserve Sel
        reservationId = []
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdReserveSel, [])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("ReserveSel" + \
                ": Command passed: " + str(respData))
            reservationId = respData
        else:
            UtilLogger.verboseLogger.error("ReserveSel" + \
                ": Command failed. Completion Code: " + \
                str(respData))
        detectAndRemovePassorFail &= cmdPassOrFail 

        # Define sample raw bytes for Clear Sel
        # Raw bytes defined as Initiate Erase
        rawBytesList = []
        for appendByte in reservationId:
            rawBytesList.append(appendByte)
        rawBytesList.append('43')
        rawBytesList.append('4C')
        rawBytesList.append('52')
        rawBytesList.append('AA')

        # Clear Sel
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdClearSel,\
            rawBytesList)
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("ClearSel" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("ClearSel" + \
                ": Command failed. Completion Code: " + \
                str(respData))
        detectAndRemovePassorFail &= cmdPassOrFail

    return detectAndRemovePassOrFail

def PingAndCheckResponse( responseTimeLimit, ipAddress, startTime=None ):

    # Initialize variables
    pingPassOrFail = False
    pingStartTime = None
    pingDuration = -1

    # Define start time
    if startTime is None:
        pingStartTime = time.time()
    else:
        pingStartTime = startTime

    UtilLogger.verboseLogger.info("PingAndCheckResponse: " + \
        "pinging with " + str(ipAddress) + \
        " and checking time taken for successful ping.")

    try:
        # Determine correct ping command based on OS
        processCmd = []
        if Config.currentOs == Config.osNameWindows:
            processCmd = [ 'ping', '-n', '1', str(ipAddress) ]
        else:
            processCmd = [ 'ping', '-c', '1', str(ipAddress) ]

        while time.time() - pingStartTime <= responseTimeLimit and not pingPassOrFail:

            # Run IpmiUtil and get stdout and stderr
            process = Popen(processCmd, stdout=PIPE, stderr=PIPE)
            out, err = process.communicate()

            # Print additional output to verbose log
            # if debugEn is True
            if Config.debugEn:
                UtilLogger.verboseLogger.info("PingAndCheckResponse: Command run: " + \
                    str(processCmd))
                UtilLogger.verboseLogger.info("PingAndCheckResponse: Command output: " + \
                    str(out))

            if err:
                if Config.debugEn:
                    UtilLogger.verboseLogger.info("PingAndCheckResponse: error for ping: " + \
                        str(err))
            else:
                for line in out.split("\n"):
                    if ("bytes from " + ipAddress) in line or \
                    ("Reply from " + ipAddress) in line:
                        pingDuration = time.time() - pingStartTime
                        UtilLogger.verboseLogger.info("PingAndCheckResponse: " + \
                            "received reply from " + ipAddress + " after " + \
                            str(pingDuration) + " seconds.")
                        pingPassOrFail = True
                        break

    except Exception, e:
        if Config.debugEn:
            UtilLogger.verboseLogger.error("PingAndCheckResponse: " + \
                "exception occurred: " + str(e))

    if not pingPassOrFail:
        UtilLogger.verboseLogger.error("PingAndCheckResponse: " + \
            "ping test for " + ipAddress + \
            " failed after " + str(responseTimeLimit) + " seconds " + \
            "response limit.")

    return pingPassOrFail, pingDuration

def GetDeviceIdAndCheckResponse(responseTimeLimit, interfaceParams, startTime=None):

    # Initialize variables
    getPassOrFail = False
    getStartTime = None
    getDuration = -1

    # Define start time
    if startTime is None:
        getStartTime = time.time()
    else:
        getStartTime = startTime

    UtilLogger.verboseLogger.info("GetDeviceIdAndCheckResponse: " + \
        "polling with Get Device Id" + \
        " and checking time taken for successful ping.")

    try:

        # Poll BMC using Get Device Id
        while time.time() - getStartTime <= responseTimeLimit and not getPassOrFail:

            # Get Device Id
            getPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
                Config.netFnApp, Config.cmdGetDeviceId, [])
            if getPassOrFail:
                getDuration = time.time() - getStartTime
                UtilLogger.verboseLogger.info("GetDeviceIdAndCheckResponse:" + \
                    " command passed. Duration until response: " + str(getDuration) + \
                    " seconds. Response: " + str(respData))
            else:
                if Config.debugEn:
                    UtilLogger.verboseLogger.error("GetDeviceIdAndCheckResponse:" + \
                        " command failed. Completion Code: " + str(respData))

    except Exception, e:
        if Config.debugEn:
            UtilLogger.verboseLogger.error("GetDeviceIdAndCheckResponse:" + \
                " exception occurred: " + str(e))

    if not getPassOrFail:
        UtilLogger.verboseLogger.error("GetDeviceIdAndCheckResponse:" + \
            " Get Device ID polling test failed after " + \
            str(responseTimeLimit) + " seconds response limit.")

    return getPassOrFail, getDuration

def LogFwDecompressionResults(fwDecompList):

    # Get number of FwDecomp in list >= 0
    fwDecompPosCnt = 0
    for fwDecomp in fwDecompList:
        if fwDecomp >= 0:
            fwDecompPosCnt += 1

    # Determine decompression time max, minimum and average
    fwDecompAvg = 0
    fwDecompMax = 0
    fwDecompMin = -1
    for fwDecomp in fwDecompList:
            
        # Determine max decompression time
        if fwDecomp > fwDecompMax:
            fwDecompMax = fwDecomp

        # Determine minimum decompression time
        if fwDecomp < fwDecompMin or fwDecompMin == -1:
            fwDecompMin = fwDecomp

        # Determine average decompression time
        # Note: using cyclesPassed to determine # of 
        # fw decompression times >= 0 seconds
        if fwDecompPosCnt > 0: # Check to avoid divide-by-zero
            fwDecompAvg += fwDecomp/fwDecompPosCnt

    # Print Fw Decompression Time Summary
    UtilLogger.verboseLogger.info(\
        "FW Decompression Time Summary: " + \
        "Average FwDecomp: " + str(fwDecompAvg) + " seconds " + \
        "Maximum FwDecomp: " + str(fwDecompMax) + " seconds " + \
        "Minimum FwDecomp: " + str(fwDecompMin) + " seconds ")
    UtilLogger.verboseLogger.info("")

    return

# Function will get chassis status
# and determine how long it takes for blade to get expected chassis status
# Inputs:
#   startTime (time.time() object): pre-determined start time
#   expectedStatus (int): expect chassis statue to be either OFF (0) or ON (1)
# Output:
#   statusPassOrFail (bool): if expected get chassis status received, return True, else False
def CheckForChassisStatus(interfaceParams, expectedStatus, startTime = None):

    # Define constants
    currPowerStateIdx = 0

    # Initialize variables
    getStatusStartTime = None
    getStatusDuration = Config.getChassisStatusLimitInSeconds
    statusPassOrFail = False
    expectedStatusResp = [ 'off', 'on' ]

    # Define start time
    if startTime is None:
        getStatusStartTime = time.time()
    else:
        getStatusStartTime = startTime

    # Get Chassis Status
    while ((time.time() - getStatusStartTime) \
        <= Config.getChassisStatusLimitInSeconds) and \
        not statusPassOrFail:
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
            Config.netFnChassis, Config.cmdGetChassisStatus, [])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetChassisStatus: " + \
                "command passed. Response: " + str(respData))
            actualStatus = int(respData[currPowerStateIdx], 16) & 1
            if actualStatus == expectedStatus:
                UtilLogger.verboseLogger.info("Helper.CheckForChassisStatus: " + \
                    "status check passed. Received get chassis status: " + \
                    expectedStatusResp[expectedStatus])
                statusPassOrFail = True
                getStatusDuration = time.time() - getStatusStartTime
            else:
                if Config.debugEn:
                    UtilLogger.verboseLogger.error("Helper.CheckForChassisStatus: " + \
                        "status check failed. Expected: " + \
                        expectedStatusResp[expectedStatus] + \
                        ". Actual: " + \
                        expectedStatusResp[actualStatus])
        else:
            UtilLogger.verboseLogger.error("GetChassisStatus: " + \
                "command failed. Completion Code: " + str(respData))

    if statusPassOrFail:
        UtilLogger.verboseLogger.info("Helper.CheckForChassisStatus: " + \
            "test passed. Able to get expected chassis status " + \
            expectedStatusResp[expectedStatus] + " after " + \
            str(getStatusDuration) + " seconds.")
    else:
        UtilLogger.verboseLogger.error("Helper.CheckForChassisStatus: " + \
            "test failed. Unable to get expected chassis status " + \
            expectedStatusResp[expectedStatus] + " after " + \
            str(Config.getChassisStatusLimitInSeconds) + " seconds.")

    return statusPassOrFail

# Function will SSH to BMC and check for any character 
#   until bootToBiosStartScreenLimitInSeconds
def SshBootToBiosStartScreenTest(startTime = None, username = None, password = None ):

    # Initialize variables
    bootToBiosStartTime = None
    bootToBiosEndTime = -1
    testPassOrFail = True

    # Define start time
    if startTime is None:
        bootToBiosStartTime = time.time()
    else:
        bootToBiosStartTime = startTime

    try:
        # Import Ssh Module
        import Ssh

        # Initialize SSH Client
        sshPassOrFail, ssh = Ssh.sshInit( username, password )
        if sshPassOrFail:
            UtilLogger.verboseLogger.info("SshBootToBiosStartScreenTest: " + \
                "successfully created SSH Client.")
        else:
            UtilLogger.verboseLogger.error("SshBootToBiosStartScreenTest: " + \
                "failed to create SSH Client.")
            return False

        # SSH Client Init successful
        # Check for any character via SSH until max limit
        #   bootToBiosStartScreenLimitInSeconds
        # Invoke Shell (default terminal: vt100)
        channel = ssh.invoke_shell()

        # Verify successful SSH connection with BMC
        sentBytes = channel.send('\n')
        time.sleep(Config.sshResponseLimit) # wait <sshResponseLimit> seconds
        sshOut = channel.recv(2024)[sentBytes:]
        if Config.debugEn:
            UtilLogger.verboseLogger.info("SshBootToBiosStartScreenTest: " + \
                "ssh output: " + str(sshOut))

        # Check for Bios start screen via SSH
        bootToBiosPassOrFail = False
        UtilLogger.verboseLogger.info("SshBootToBiosStartScreenTest: " + \
            "checking for Bios start screen.")
        while (time.time() - bootToBiosStartTime) <= \
            int(Config.bootToBiosStartScreenLimitInSeconds):
          
            # Verify successful SSH connection with BMC
            sentBytes = channel.send('\n')
            time.sleep(5) # wait 5 seconds
            sshOut = channel.recv(2024)[sentBytes:]
            if Config.debugEn:
                UtilLogger.verboseLogger.info("SshBootToBiosStartScreenTest: " + \
                    "channel out: " + str(sshOut))
            for line in sshOut.split('\n'):
                if "American Megatrends" in line or \
                    "Flex" in line or \
                    "SAC" in line:
                    bootToBiosEndTime = int(time.time() - bootToBiosStartTime)
                    UtilLogger.verboseLogger.info("SshBootToBiosStartScreenTest: " + \
                        "Blade booted to BIOS, with the following output: " + \
                        str(sshOut) + " and after " + str(bootToBiosEndTime) + \
                        " seconds.")
                    bootToBiosPassOrFail = True
                    break
            if bootToBiosPassOrFail:
                break

        testPassOrFail &= bootToBiosPassOrFail

        # Verify bootToBiosPassOrFail is false
        if not bootToBiosPassOrFail:
            UtilLogger.verboseLogger.info("SshBootToBiosStartScreenTest: " + \
                "unable to detect boot to BIOS start screen after " + \
                str(Config.bootToBiosStartScreenLimitInSeconds) + \
                " seconds.")

        # Close SSH Session
        closePassOrFail = Ssh.sshClose(ssh)
        if closePassOrFail:
            UtilLogger.verboseLogger.info("SshBootToBiosStartScreenTest: " + \
                "successfully closed SSH session.")
        else:
            UtilLogger.verboseLogger.error("SshBootToBiosStartScreenTest: " + \
                "failed to close SSH session.")

        if testPassOrFail:
            UtilLogger.verboseLogger.info("SshBootToBiosStartScreenTest: " + \
                "test to detect BIOS Start Screen via SSH passed.")
        else:
            UtilLogger.verboseLogger.info("SshBootToBiosStartScreenTest: " + \
                "test to detect BIOS Start Screen via SSH failed.")

    except Exception, e:
        UtilLogger.verboseLogger.error("SshBootToBiosStartScreenTest: " + \
            "exception occurred: " + str(e))
        testPassOrFail = False

    return testPassOrFail


# Function will SSH to BMC BMC and check for any character 
#   until bootToBMCStartScreenLimitInSeconds
def SshBootToBMCStartScreenTest(startTime = None, username = None, password = None, ptrn = None ):

    # Initialize variables
    bootToBMCStartTime = None
    bootToBMCEndTime = -1
    testPassOrFail = True

    # Define start time
    if startTime is None:
        bootToBMCStartTime = time.time()
    else:
        bootToBMCStartTime = startTime

    try:
        # Import Ssh Module
        import Ssh

        # Initialize SSH Client
        sshPassOrFail, ssh = Ssh.sshInit( username, password )
        if sshPassOrFail:
            UtilLogger.verboseLogger.info("SshBootToBMCStartScreenTest: " + \
                "successfully created SSH Client.")
        else:
            UtilLogger.verboseLogger.error("SshBootToBMCStartScreenTest: " + \
                "failed to create SSH Client.")
            return False

        # SSH Client Init successful
        # Check for any character via SSH until max limit
        #   bootToBMCStartScreenLimitInSeconds
        # Invoke Shell (default terminal: vt100)
        channel = ssh.invoke_shell()

        # Verify successful SSH connection with BMC
        sentBytes = channel.send('\n')
        time.sleep(Config.sshResponseLimit) # wait <sshResponseLimit> seconds
        sshOut = channel.recv(2024)[sentBytes:]
        if Config.debugEn:
            UtilLogger.verboseLogger.info("SshBootToBMCStartScreenTest: " + \
                "ssh output: " + str(sshOut))

        # Check for BMC start screen via SSH
        bootToBMCPassOrFail = False
        UtilLogger.verboseLogger.info("SshBootToBMCStartScreenTest: " + \
            "checking for BMC start screen.")
        while (time.time() - bootToBMCStartTime) <= int(Config.bootToBMCStartScreenLimitInSeconds):          
            outputStr = None
            # Verify successful SSH connection with BMC
            sentBytes = channel.send('\n')
            time.sleep(5) # wait 5 seconds
            sshOut = channel.recv(2024)[sentBytes:]
            
            if Config.debugEn:
                UtilLogger.verboseLogger.info("SshBootToBMCStartScreenTest: channel out: " + str(sshOut))            
            
            if( ptrn != None ):
                outputStr = regExpParser( sshOut, ptrn, ptrn )

            if( outputStr == ptrn ):
                UtilLogger.verboseLogger.info("SshBootToBMCStartScreenTest: " + \
                        "BMC booted to login on console, with the following output: " + \
                        str(sshOut) + " and after " + str(bootToBMCEndTime) + \
                        " seconds.")
                bootToBMCPassOrFail = True
                break

        testPassOrFail &= bootToBMCPassOrFail

        # Verify bootToBiosPassOrFail is false
        if not bootToBMCPassOrFail:
            UtilLogger.verboseLogger.info("SshBootToBMCStartScreenTest: " + \
                "unable to detect boot to BMC start screen after " + \
                str(Config.bootToBMCStartScreenLimitInSeconds) + \
                " seconds.")

        # Close SSH Session
        closePassOrFail = Ssh.sshClose(ssh)
        if closePassOrFail:
            UtilLogger.verboseLogger.info("SshBootToBMCStartScreenTest: " + \
                "successfully closed SSH session.")
        else:
            UtilLogger.verboseLogger.error("SshBootToBMCStartScreenTest: " + \
                "failed to close SSH session.")

        if testPassOrFail:
            UtilLogger.verboseLogger.info("SshBootToBMCStartScreenTest: " + \
                "test to detect BMC Start Screen via SSH passed.")
        else:
            UtilLogger.verboseLogger.info("SshBootToBMCStartScreenTest: " + \
                "test to detect BMC Start Screen via SSH failed.")

    except Exception, e:
        UtilLogger.verboseLogger.error("SshBootToBMCStartScreenTest: " + \
            "exception occurred: " + str(e))
        testPassOrFail = False

    return testPassOrFail


def regExpParser(inputParameter, pattern, theSubstring):
    output = None
    regex = re.compile(pattern)
    matches = regex.findall(inputParameter)

    if not matches:
        return None

    for s in matches:
        if (s == theSubstring):
            output = s

    return output
