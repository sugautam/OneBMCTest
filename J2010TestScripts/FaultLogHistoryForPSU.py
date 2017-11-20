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
import os
import re
import Config
import RedFish
import UtilLogger
import AcPowerIpSwitch
import Ssh
import zipfile
import shutil

# Global variables
fileName = os.path.splitext(os.path.basename(__file__))[0]
testPassOrFail = True

# Setup Function
def Setup(interfaceParams):
    global fileName
    UtilLogger.verboseLogger.info("%s: running Setup fxn" %(fileName))

    return True

def Execute(interfaceParams):
    global testPassOrFail

    # BMC will query logs each 30-40 seconds
    BMCLogQueryTime = 60

    try:
        cmdPassOrFail = _ClearBMCLog()
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("%s: Clear Log success" %(fileName))
        else:
            UtilLogger.verboseLogger.info("%s: Failed to clear log" %(fileName))

        cmdPassOrFail = _ACPowerOnOff()
        if not cmdPassOrFail:
            UtilLogger.verboseLogger.info("%s: Failed to do AC Power on/off" %(fileName))
            return False

        # Ping and wait for BMC to boot on, max waiting time is 120 seconds
        cmdPassOrFail = _PingBMCStatus()
        if cmdPassOrFail:
            UtilLogger.summaryLogger.info("%s: BMC is on" %(fileName))
        else:
            UtilLogger.summaryLogger.info("%s: Ping BMC failed" %(fileName))
            return False

        UtilLogger.verboseLogger.info("%s: Waiting 60 seconds for log query" %(fileName))
        time.sleep(BMCLogQueryTime)

        # Get logs after create specific log, then find the key message
        snapshotPassOrFail, _ = _SnapshotLogsOnBMC()
        if not snapshotPassOrFail:
            UtilLogger.summaryLogger.info("%s: Snapshot log failed" %(fileName))
            return False
        else:
            getPassOrFail, UnZipLogs = _GetAndUnZip()
        if (not getPassOrFail) or (UnZipLogs == None):
            UtilLogger.summaryLogger.info("%s: Get snapshot log failed" %(fileName))
            return False
        else:
            cmdPassOrFail, BMCLogs, BMCLogsNumbers = LogParser(UnZipLogs)
        if cmdPassOrFail:
            if not _FindSpecificLog(BMCLogs, 0, BMCLogsNumbers):
                UtilLogger.verboseLogger.info("%s: Failed to find specific log" %(fileName))
                testPassOrFail = False
        else:
            UtilLogger.verboseLogger.error("%s: Get log data failed" %(fileName))
            testPassOrFail = False

    except Exception as e:
        UtilLogger.verboseLogger.info("%s: exception occurred - %s" %(fileName, str(e)))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global testPassOrFail, fileName
    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))

    return testPassOrFail

# Use AC Power Switch to turn on/off J2010
def _ACPowerOnOff():
    FuncPassOrFail = True

    # Power Down Server Blade
    powerPassOrFail, response = AcPowerIpSwitch.SetPowerOnOff(Config.acPowerIpSwitchOutlet, 0)
    if powerPassOrFail:
        UtilLogger.verboseLogger.info("%s: Server blade powered down." %(fileName))
    else:
        UtilLogger.verboseLogger.error("%s: Failed to power down server blade." %(fileName))
    FuncPassOrFail &= powerPassOrFail

    # Sleep
    UtilLogger.verboseLogger.info("%s: " + "Sleeping for " + str(Config.acPowerOffSleepInSeconds) + " seconds." %(fileName))
    time.sleep(Config.acPowerOffSleepInSeconds)

    # Power Up Server Blade
    powerPassOrFail, response = AcPowerIpSwitch.SetPowerOnOff(Config.acPowerIpSwitchOutlet, 1)
    if powerPassOrFail:
        UtilLogger.verboseLogger.info("%s: Server blade powered up." %(fileName))
    else:
        UtilLogger.verboseLogger.error("%s: Failed to power up server blade." %(fileName))
    FuncPassOrFail &= powerPassOrFail

    return FuncPassOrFail

# Ping BMC and check if BMC was online or not
def _PingBMCStatus():
    startTime = time.time()

    if Config.currentOs == Config.osNameWindows:
        pingCmd = "ping -n 1 " + Config.bmcIpAddress + " > nul 2>&1"
    else:
        pingCmd = "ping -c 1 " + Config.bmcIpAddress + " >/dev/null 2>&1"

    response = 1
    # Ping BMC each 10 seconds. Max timeout is 120 seconds
    while response != 0 and (time.time()-startTime < Config.acPowerOnSleepInSeconds):
        response = os.system(pingCmd)
        time.sleep(10)

    return not bool(response)

# Use sftp to get log-snapshot.zip on BMC and unzip on local folder
def _GetAndUnZip():
    Logs = None
    FuncPassOrFail = True

    try:
        if _CheckSnapshotFile():
            # Try get log-snapshot.zip on BMC
            getPassOrFail = Ssh.sftpGetFile(hostFilePath='/var/wcs/home/log-snapshot.zip', \
                            localFilePath='./log-snapshot.zip')
            if not getPassOrFail:
                UtilLogger.verboseLogger.info("%s: Get log-snapshot.zip via sftp failed!" %(fileName))
                return False, Logs

            DeletePassOrFail = Ssh.sftpRemoveFile(hostFilePath='/var/wcs/home/log-snapshot.zip')
            if not DeletePassOrFail:
                UtilLogger.verboseLogger.info("%s: Delete log-snapshot.zip on BMC via sftp failed!" \
                %(fileName))
                return False, Logs
        else:
            UtilLogger.verboseLogger.info\
            ("%s: log-snapshot.zip doesn't create on BMC. Failed with timeout" %(fileName))
            return False, Logs

        # Unzip log file
        LogZipFile = zipfile.ZipFile('./log-snapshot.zip', 'r')
        LogZipFile.extractall('./')
        FilePath = LogZipFile.namelist()
        LogZipFile.close()

        with open('./'+FilePath[0]) as LogFile:
            Logs = LogFile.readlines()

        if not Logs:
            FuncPassOrFail = False

        # Delete temparary files
        os.remove('./log-snapshot.zip')
        shutil.rmtree('./var')

    except Exception as e:
        UtilLogger.verboseLogger.error("%s: _GetAndUnZip() failed with %s" %(fileName, str(e)))
        FuncPassOrFail = False

    return FuncPassOrFail, Logs

# Call LogService.LogSnapshot to generate log-snapshot.zip on BMC
def _SnapshotLogsOnBMC():
    cmdPassOrFail = False
    resource = 'redfish/v1/Managers/System/LogServices/Log/Actions/LogService.LogSnapshot'
    # Empty payload
    Payload = {}
    Payload["data"] = []

    # Send REST Post request, and retry if failed.
    cmdPassOrFail, response = RedFish.PostResourceValues(resource, Payload)

    return cmdPassOrFail, response

# Parsing log form log file
def LogParser(BMCLogs):
    # Initial return variables
    LogList = []
    LogNumber = 0
    TempMember = {}

    # Get number of logs
    for line in BMCLogs:
        LogNumber = re.findall(r'\d+', line)
        if LogNumber:
            break

    for line in BMCLogs:
        if line == '\n':
            LogList.append(TempMember)
            TempMember = {}

        # Skip this line if it is not a log entry
        if ':' not in line:
            continue

        AfterSplit = re.split(r'\s+:\s', line)
        TempMember[AfterSplit[0]] = AfterSplit[1].split('\n')[0]

    # if LogList is empty, then return false
    return bool(LogList), LogList, int(LogNumber[0])

# Clear BMC Log
def _ClearBMCLog():
    resource = 'redfish/v1/Managers/System/LogServices/Log/Actions/LogService.ClearLog'
    # Empty payload
    Payload = {}
    Payload["data"] = []

    # Send REST Post request
    cmdPassOrFail, response = RedFish.PostResourceValues(resource, Payload)

    return cmdPassOrFail

# Find specific log
def _FindSpecificLog(Logs, preLogsNumbers, BMCLogsNumbers):
    # Set key message
    KeyMessageRegexPattern = "^PSU([1-2])_Fault_Log is Asserted. Log ([1-8]):"
    NextExpectedLog = 1
    ReOutputStr = ''
    ExpectedLogNnmbers = 8

    # Parsing log from 1 to 8
    KeyMessageRegexCompile = re.compile(KeyMessageRegexPattern, re.L)
    for index in range(preLogsNumbers, BMCLogsNumbers):
        MessageMatch = KeyMessageRegexCompile.findall(Logs[index]["Message"])
        if MessageMatch:
            if MessageMatch[0][1] == str(NextExpectedLog):
                ReOutputStr += (MessageMatch[0][0]+'Y')
                if NextExpectedLog >= ExpectedLogNnmbers:
                    break
                NextExpectedLog += 1
            else:
                ReOutputStr += (MessageMatch[0][0]+'N')

    if re.match("(1Y){"+str(ExpectedLogNnmbers)+"}|(2Y){"+str(ExpectedLogNnmbers)+"}", ReOutputStr):
        UtilLogger.verboseLogger.info("%s: We get exactly 8 logs."%(fileName))
        return True

    UtilLogger.verboseLogger.info("%s: Failed. We didn't get %d expected logs."%(fileName, ExpectedLogNnmbers))
    return False

# Check if log-snapshot.zip was generated on BMC
def _CheckSnapshotFile():

    # Initial command
    execCmds = ['\n']
    execCmds.append('cd /var/wcs/home\n')
    execCmds.append('ls | grep log-snapshot.zip\n')

    getFilePassOrFail = False
    StartTime = time.time()
    MaxTimeout = 30
    while not getFilePassOrFail and (time.time()-StartTime) < MaxTimeout:
        try:
            execPassOrFail, sshOutputs, parsedCmdOutputs = \
            Ssh.sshExecuteCommand(execCmds)
            # Check Ssh command respose
            if execPassOrFail:
                if sshOutputs[-1].split()[0] == 'log-snapshot.zip':
                    getFilePassOrFail = True
            else:
                UtilLogger.verboseLogger.info("%s: Check Snapshot File failed" %(fileName))

        except Exception as e:
            UtilLogger.verboseLogger.error\
            ("%s: CheckSnapshotFile failed. Exception: %s" %(fileName, str(e)))

    return getFilePassOrFail
