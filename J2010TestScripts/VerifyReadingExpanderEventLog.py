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
import Config
import RedFish
import UtilLogger
import re
import Ssh
import zipfile
import shutil

# Global variables
fileName = os.path.splitext(os.path.basename(__file__))[0]
testPassOrFail = True
ExpanderSshResponseLimit = 300

# Setup Function
def Setup(interfaceParams):
    global fileName
    UtilLogger.verboseLogger.info("%s: running Setup fxn" %(fileName))

    return True

def Execute(interfaceParams):
    global testPassOrFail
    BMCLogQueryTimeout = 120

    # This test will perform in these steps:
    #       1.Turn on all Disk on all expander.
    #       2.Clear BMC logs.
    #       3.Clear Expander log and create 7900 logs on each expander.
    #       4.Use RedFish DISK on/off command to create real logs and fill up expander log entry.
    #       5.Get BMC logs.
    #       6.Check BMC logs and match every DISK logs.
    #         Each existed DISK should have at least a pair of DISK on/off logs.
    #       7.Print out the list that disks are not existed.

    # Turn on all Disks on all expander
    cmdPassOrFail, _ = _DiskOnAndOff('On', Config.J2010allSeIDs)
    if not cmdPassOrFail:
        UtilLogger.verboseLogger.info("%s: Failed to turn on all Disks in the first time" %(fileName))
        return False

    # Waiting for DISK status change
    time.sleep(Config.ExpanderDiskStateChangeTime)

    # Clean logs
    cmdPassOrFail, _ = _ClearBMCLogs()
    if not cmdPassOrFail:
        UtilLogger.verboseLogger.info("%s: Clear logs failed" %(fileName))
        return False
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
        cmdPassOrFail, _, currentLogsNumbers = LogParser(UnZipLogs)
    if cmdPassOrFail and currentLogsNumbers == 1:
        UtilLogger.verboseLogger.info("%s: Log is cleared" %(fileName))
    else:
        UtilLogger.verboseLogger.info("%s: Logs are more than 1. Clear logs failed" %(fileName))
        return False

    # Waiting for log service to query logs
    time.sleep(BMCLogQueryTimeout)
    # Generate fake logs
    cmdPassOrFail = _CreateFakeLog()
    if not cmdPassOrFail:
        UtilLogger.verboseLogger.info("%s: Create fake Log failed" %(fileName))
        return False
    else:
        # Make sure all expander commands are complete
        time.sleep(Config.ExpanderDiskStateChangeTime)
        # Fill Expanders log entries
        UtilLogger.verboseLogger.info("%s: Starting to fill up Expander log entry with real disk on/off log" %(fileName))
        cmdPassOrFail = _FillUpRealExpanderLog()

    if not cmdPassOrFail:
        UtilLogger.verboseLogger.info("%s: Fill up Expander logs failed" %(fileName))
        return False

    # Waiting for log service to query logs
    time.sleep(BMCLogQueryTimeout)

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
        cmdPassOrFail, BMCLogs, _ = LogParser(UnZipLogs)
    if cmdPassOrFail:
        FuncPassOrFail, UnUsedDiskList, DiskMissMatchList = _FindSpecificLog(BMCLogs)
        if not FuncPassOrFail:
            UtilLogger.verboseLogger.info("%s: Match disk failed" %(fileName))
            for ExpanderID in Config.J2010allSeIDs:
                for DiskID in DiskMissMatchList[ExpanderID-1]:
                    UtilLogger.verboseLogger.info("%s: Failed to match Expander %s Disk %s" %(fileName, ExpanderID, DiskID))
                    UtilLogger.verboseLogger.info("%s: Expander %s Disk %s may not able to work or failed to create log" %(fileName, ExpanderID, DiskID))
            testPassOrFail = False

        # Print unused disk list
        for ExpanderID in Config.J2010allSeIDs:
            for DiskID in UnUsedDiskList[ExpanderID-1]:
                UtilLogger.verboseLogger.info("%s: Expander %s Disk %s is not used" %(fileName, ExpanderID, DiskID))
    else:
        UtilLogger.verboseLogger.info("%s: Get log data failed" %(fileName))
        return False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global testPassOrFail, fileName
    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))

    return testPassOrFail

# Use RedFish to turn on/off storage device
def _DiskOnAndOff(data, ExpanderList):
    ExpanderMaxDiskNumber = 22
    FuncPassOrFail = True
    # Empty payload
    Payload = {}
    Payload["data"] = []

    for ExpanderID in ExpanderList:
        UtilLogger.verboseLogger.info("%s: Start to turn %s disk on Expander %s" %(fileName, data, ExpanderID))

        for DiskID in range(ExpanderMaxDiskNumber):
            resource = 'redfish/v1/Chassis/System/StorageEnclosure/{0}/Drives/{1}/Actions/{2}'.format(ExpanderID, DiskID+1, data)
            # Send REST Post request
            (cmdPassOrFail, response) = RedFish.PostResourceValues(resource, Payload)
            # Waiting for Expander executing
            time.sleep(1)

            if not cmdPassOrFail:
                UtilLogger.verboseLogger.info("%s: Failed to turn %s Expander %s Disk %s" %(fileName, data, ExpanderID, DiskID+1))
            FuncPassOrFail &= cmdPassOrFail

        UtilLogger.verboseLogger.info("%s: Turn %s disk on Expander %s finished" %(fileName, data, ExpanderID))

    return FuncPassOrFail, response

# Clear BMC logs before testing
def _ClearBMCLogs():

    resource = 'redfish/v1/Managers/System/LogServices/Log/Actions/LogService.ClearLog'
    # Empty payload
    Payload = {}
    Payload["data"] = []
    # Send REST Post request
    (cmdPassOrFail, response) = RedFish.PostResourceValues(resource, Payload)

    return cmdPassOrFail, response

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

# check BMC logs and match all Disks list
def _FindSpecificLog(Logs):
    OldestMessageId = _CheckBMCRollover(Logs)
    ExpanderMaxDiskNumber = 22
    FuncPassOrFail = False

    # Set Regex variable
    removedRegexPattern = "^Expander [0-9]: DISK [0-9]{2} was removed$"
    installedRegexPattern = "^Expander [0-9]: DISK [0-9]{2} is installed$"
    removedregexCompile = re.compile(removedRegexPattern, re.L)
    installedregexCompile = re.compile(installedRegexPattern, re.L)
    numberMatch = re.compile('\d+')

    # Set Disk list and initial DiskNotUseList data
    # DiskOffList will save the Disks that been removed
    # DiskOnList will save the Disks that been installed
    # DiskNotUseList will save all Disks.
    #  When Disks are in DisksOffList or DisksOnList,
    #  then this Disk will been removed from DiskNotUseList
    DisksOffList = [[] for ExpanderNumber in range(len(Config.J2010allSeIDs))]
    DisksOnList = [[] for ExpanderNumber in range(len(Config.J2010allSeIDs))]
    DiskNotUseList = [[] for ExpanderNumber in range(len(Config.J2010allSeIDs))]
    for ExpanderID in Config.J2010allSeIDs:
        for DiskID in range(ExpanderMaxDiskNumber):
            DiskNotUseList[ExpanderID-1].append(DiskID+1)

    # The first real expander log will be DISK removed message
    # Start parsing log message and make list
    OutOfFakeLogRange = False
    for index in range(OldestMessageId, len(Logs)):
        m = removedregexCompile.match(Logs[index]["Message"])
        if m:
            numResult = numberMatch.findall(Logs[index]["Message"])
            if int(numResult[1]) not in DisksOffList[int(numResult[0])-1]:
                OutOfFakeLogRange = True
                DisksOffList[int(numResult[0])-1].append(int(numResult[1]))
        else:
            m = installedregexCompile.match(Logs[index]["Message"])
            if m:
                numResult = numberMatch.findall(Logs[index]["Message"])
                if OutOfFakeLogRange:
                    if int(numResult[1]) not in DisksOnList[int(numResult[0])-1]:
                        DisksOnList[int(numResult[0])-1].append(int(numResult[1]))

    # This part will do when BMC rollover happened
    # And will parsing message that generate after rollover
    for index in range(0, OldestMessageId):
        m = removedregexCompile.match(Logs[index]["Message"])
        if m:
            numResult = numberMatch.findall(Logs[index]["Message"])
            if int(numResult[1]) not in DisksOffList[int(numResult[0])-1]:
                OutOfFakeLogRange = True
                DisksOffList[int(numResult[0])-1].append(int(numResult[1]))
        else:
            m = installedregexCompile.match(Logs[index]["Message"])
            if m:
                numResult = numberMatch.findall(Logs[index]["Message"])
                if OutOfFakeLogRange:
                    if int(numResult[1]) not in DisksOnList[int(numResult[0])-1]:
                        DisksOnList[int(numResult[0])-1].append(int(numResult[1]))

    for ExpanderID in Config.J2010allSeIDs:
        DisksOffList[ExpanderID-1].sort()
        DisksOnList[ExpanderID-1].sort()

    # Remove Disks that used
    for ExpanderID in Config.J2010allSeIDs:
        index = 0
        while index < len(DiskNotUseList[ExpanderID-1]):
            if (DiskNotUseList[ExpanderID-1][index] in DisksOffList[ExpanderID-1]) or \
                (DiskNotUseList[ExpanderID-1][index] in DisksOnList[ExpanderID-1]):
                DiskNotUseList[ExpanderID-1].remove(DiskNotUseList[ExpanderID-1][index])
                index -= 1
            index += 1

    # Check Disks that not match between DisksOffList and DisksOnList
    DiskMissMatchList = [[] for ExpanderNumber in range(len(Config.J2010allSeIDs))]
    for ExpanderID in Config.J2010allSeIDs:
        for DiskID in range(ExpanderMaxDiskNumber):
            if (((DiskID+1) in DisksOnList[ExpanderID-1]) or ((DiskID+1) in DisksOffList[ExpanderID-1])) and \
                (not ((DiskID+1) in DisksOnList[ExpanderID-1]) and ((DiskID+1) in DisksOffList[ExpanderID-1])):
                DiskMissMatchList[ExpanderID-1].append(DiskID+1)

    # If DiskMissMatchList is not empty, means DisksOffList and DisksOnList are not matched
    if not DiskMissMatchList[0] and not DiskMissMatchList[1] and not DiskMissMatchList[2] and not DiskMissMatchList[3]:
        if (not DisksOffList[0] and not DisksOffList[1] and not DisksOffList[2] and not DisksOffList[3]) and \
            (not DisksOnList[0] and not DisksOnList[1] and not DisksOnList[2] and not DisksOnList[3]):
            UtilLogger.verboseLogger.info("%s: Failed. No Disks are on Expander." %(fileName))
        else:
            FuncPassOrFail = True
            UtilLogger.verboseLogger.info("%s: All Disks on each Expander are matched" %(fileName))

    return FuncPassOrFail, DiskNotUseList, DiskMissMatchList

# Create expander event log
def _CreateFakeLog():
    global ExpanderSshResponseLimit
    cmdPassOrFail = True
    # Fake Expander Log command
    execCmds = ['test 100']
    execCmds.append('\r')
    # Clear Expander Log command
    ClearLogCmds = ['syslog clr']
    ClearLogCmds.append('\r')
    MaxExpanderLogNumber = 8000
    LogGenBuffer = 100

    try:
        # Create logs
        for ExpanderID in Config.J2010allSeIDs:
            # Clear expander logs
            execPassOrFail, sshOutputs, parsedCmdOutputs = Ssh.sshExecuteCommand(ClearLogCmds, username=Config.bmcUser,\
                    password=Config.bmcPassword, port=Config.J2010sshPorts[ExpanderID-1], sshResponseLimit=ExpanderSshResponseLimit)

            if execPassOrFail:
                UtilLogger.verboseLogger.info("%s: Expander %s log is cleared" %(fileName, ExpanderID))
                CreateLogsComplete = False

                while not CreateLogsComplete:
                    # Get expander log number to excuted how many fake log we should genarate
                    execPassOrFail, ExpanderLogNumbers = _CheckExpanderLogNumber(ExpanderID)
                    if not execPassOrFail:
                        UtilLogger.verboseLogger.info("%s: Failed to get expander %s log number" %(fileName, ExpanderID))
                        cmdPassOrFail = False
                        break
                    else:
                        if ((MaxExpanderLogNumber-1) - ExpanderLogNumbers) <= LogGenBuffer:
                            UtilLogger.verboseLogger.info("%s: Expander %s is almost rollover with %s logs, ready to fill with real logs" \
                            %(fileName, ExpanderID, ExpanderLogNumbers))
                            TimesNeeded = 0
                            CreateLogsComplete = True
                            break
                        # Logs not enough
                        else:
                            UtilLogger.verboseLogger.info("%s: We need more fake logs on Expander %s, current logs: %s" \
                            %(fileName, ExpanderID, ExpanderLogNumbers))
                            TimesNeeded = ((MaxExpanderLogNumber-1) - ExpanderLogNumbers)/LogGenBuffer
                            CreateLogsComplete = False

                    # Generate logs
                    for runTimes in range(TimesNeeded):
                        execPassOrFail, sshOutputs, parsedCmdOutputs = Ssh.sshExecuteCommand(execCmds, username=Config.bmcUser,\
                        password=Config.bmcPassword, port=Config.J2010sshPorts[ExpanderID-1], sshResponseLimit=ExpanderSshResponseLimit)

                        # Sleep 110 seconds for each 'test100' command cost 100 seconds to execute.
                        time.sleep(110)

                        if execPassOrFail:
                            UtilLogger.verboseLogger.info("%s: Log created %s" %(fileName, ExpanderLogNumbers + (runTimes+1) * LogGenBuffer))
                        else:
                            UtilLogger.verboseLogger.info("%s: Log create failed" %(fileName))

            else:
                UtilLogger.verboseLogger.info("%s: Clear expander log on expander %s failed" %(fileName, ExpanderID))
                cmdPassOrFail = False

    except Exception, e:
        UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))
        cmdPassOrFail = False

    return cmdPassOrFail

# Fill up expander log with real disk log
def _FillUpRealExpanderLog():
    global ExpanderDiskStateChangeTime

    for ExpanderID in Config.J2010allSeIDs:
        ExpanderIDList = [ExpanderID]
        if _CheckExpanderDiskNumber(ExpanderID) != 0:
            # Generate log until expander rollover
            while not _CheckExpanderRollOver(ExpanderID):

                # Turn off the Disk
                cmdPassOrFail, response = _DiskOnAndOff('Off', ExpanderIDList)
                # Wait for disk stage change
                time.sleep(Config.ExpanderDiskStateChangeTime)

                # Turn on the Disk
                cmdPassOrFail, response = _DiskOnAndOff('On', ExpanderIDList)
                # Wait for disk stage change
                time.sleep(Config.ExpanderDiskStateChangeTime)

            UtilLogger.verboseLogger.info("%s: Expander %s Rollover happened" %(fileName, ExpanderID))
        else:
            UtilLogger.verboseLogger.info("%s: No Disks on Expander %s" %(fileName, ExpanderID))
            UtilLogger.verboseLogger.info("%s: Unable to fill up log entry. Expander %s will be skipped." %(fileName, ExpanderID))

    return True

# Get Expander log number
def _CheckExpanderLogNumber(ExpanderID):
    global ExpanderSshResponseLimit
    # Initial command
    execCmds = ['test oem2']
    execCmds.append('\r')

    try:
        (execPassOrFail, sshOutputs, parsedCmdOutputs) = Ssh.sshExecuteCommand(execCmds, username=Config.bmcUser,\
         password=Config.bmcPassword, port=Config.J2010sshPorts[ExpanderID-1], sshResponseLimit=ExpanderSshResponseLimit)
        # Parsing log number
        if execPassOrFail:
            tokens = sshOutputs[1].split()
            for line in tokens:
                Keyword = line.split(':')
                if Keyword[0] == "offset":
                    LogNumber = int(Keyword[1])/8
                    return True, LogNumber
                    break
        else:
            UtilLogger.verboseLogger.info("%s: Excute get expander log number command failed" %(fileName))

    except Exception as e:
        UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))

    return False, 0

# Check if Expander log is rollover
def _CheckExpanderRollOver(ExpanderID):
    global ExpanderSshResponseLimit
    # Initial command
    execCmds = ['test oem2']
    execCmds.append('\r')

    try:
        execPassOrFail, sshOutputs, parsedCmdOutputs = Ssh.sshExecuteCommand(execCmds,\
         username=Config.bmcUser, password=Config.bmcPassword, port=Config.J2010sshPorts[ExpanderID-1], sshResponseLimit=ExpanderSshResponseLimit)

        # Find "log is full:1" message
        if execPassOrFail:
            tokens = sshOutputs[1].split()
            for line in tokens:
                Keyword = line.split(':')
                if Keyword[0] == "full":
                    if Keyword[1] == '1':
                        return True
                    else:
                        return False
        else:
            UtilLogger.verboseLogger.info("%s: Failed to get Expander %s rollover status" %(fileName, ExpanderID))

    except Exception as e:
        UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))

    return False

# Check how many disk are on this Expander
def _CheckExpanderDiskNumber(ExpanderID):
    global ExpanderSshResponseLimit
    # Initial command
    execCmds = ['status']
    execCmds.append('\r')
    RegexPattern = "^Disk\[[0-9]{2}\] status : \[Present\]"
    regexCompile = re.compile(RegexPattern, re.L)
    DiskCounter = 0
    ExpanderStatusResponseSize = 4096

    try:
        execPassOrFail, sshOutputs, parsedCmdOutputs = Ssh.sshExecuteCommand(execCmds,\
         username=Config.bmcUser, password=Config.bmcPassword, port=Config.J2010sshPorts[ExpanderID-1], \
         sshResponseLimit=ExpanderSshResponseLimit, sshResponseSize=ExpanderStatusResponseSize)

        # Find Present Disk
        if execPassOrFail:
            tokens = sshOutputs[1].split('\n')
            for line in tokens:
                m = regexCompile.match(line)
                if m:
                    DiskCounter += 1
            return DiskCounter
        else:
            UtilLogger.verboseLogger.info("%s: Failed to get Expander %s status" %(fileName, ExpanderID))

    except Exception as e:
        UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))

    return 0

# Check BMC rollover status
def _CheckBMCRollover(BMCLogs):
    BMCRolloverMessageID = 0

    # Get ID of Log Rollover is Asserted Message
    for index in range(len(BMCLogs)):
        if BMCLogs[index]["Message"] == "Log Rollover is Asserted":
            BMCRolloverMessageID = index+1

    # if BMCRolloverMessageID is still 0, means BMC has not rollover
    if BMCRolloverMessageID == 0:
        return BMCRolloverMessageID

    currentTime = int(time.mktime(time.strptime(BMCLogs[BMCRolloverMessageID-1]["Created"], "%Y-%m-%d %H:%M:%S")))
    OldestTimeID = BMCRolloverMessageID
    # Get oldest message in BMC log
    for index in range(0, len(BMCLogs)):
        if int(time.mktime(time.strptime(BMCLogs[index]["Created"], "%Y-%m-%d %H:%M:%S"))) < currentTime:
            OldestTimeID = index
            currentTime = int(time.mktime(time.strptime(BMCLogs[index]["Created"], "%Y-%m-%d %H:%M:%S")))

    return OldestTimeID

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
