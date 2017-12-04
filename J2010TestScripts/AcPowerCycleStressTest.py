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

import datetime
import os
import time
import AcPowerIpSwitch
import Config
import Helper
import RedFish
import UtilLogger
import Ssh
import XmlParser
import zipfile
import shutil
import re

# Initialize global variables
fileName = os.path.basename(__file__)
testPassOrFail = True

# Setup Function
def Setup(interfaceParams):      
    return True

# Function will run stress test over REST
# for AC Power Cycling BMC
def Execute(interfaceParams):      
    global fileName, testPassOrFail

    username = Config.bmcUser 
    password = Config.bmcPassword     

    # Define Test variables
    testPassOrFail = True
    BMCLogQueryTime = 60
    respData = []
    testName = 'AcPowerCycleStressTest'
    fwDecompList = []
    startTime = time.time()

    # total test time in seconds
    # total test time = 60 seconds/minute *
    #   60 minutes/hour * <totalTestTimeInHours>
    totalTestTime = startTime + 60 * 60 * Config.acPowerCycleStressTestTotalTime
    
    try:
        if not interfaceParams:
            UtilLogger.consoleLogger.info(\
                "Currently running in-band in server blade. Will not execute test.")
            UtilLogger.verboseLogger.info(\
                "Currently running in-band in server blade. Will not execute test.")
            return True
        else:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.acPowerCycleStressTestTotalTime) + \
                "-hour AC Power Cycle stress test for J2010 REST")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.acPowerCycleStressTestTotalTime) + \
                "-hour AC Power Cycle stress test for J2010 REST")

        # Run test
        # Print Cycle # PASS/FAIL for every test cycle
        testCycle = 0
        cyclesPassed = 0
        cyclesFailed = 0
        while time.time() < totalTestTime:

            cyclePassOrFail = True
            cycleStartTime = time.time()

            cmdPassOrFail, _ = _ClearBMCLog()
            if cmdPassOrFail:
                UtilLogger.verboseLogger.info("%s: BMC log cleard!" %(fileName))
            else:
                UtilLogger.verboseLogger.info("%s: Failed to clear BMC logs!" %(fileName))

            # Power Down Server Blade
            if Config.acPowerCycleStressTestPowerSwitchMethod == 0:
                powerPassOrFail, response = AcPowerIpSwitch.SetPowerOnOff(\
                    Config.acPowerIpSwitchOutlet, 0)
            elif Config.acPowerCycleStressTestPowerSwitchMethod == 1:
                powerPassOrFail, response = _PowerOnOffByRackManager('Off')
            if powerPassOrFail:
                UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: Server blade powered down.")
            else:
                UtilLogger.verboseLogger.error("AcPowerCycleStressTest.py: Failed to power down server blade.")
            cyclePassOrFail &= powerPassOrFail

            # Sleep
            UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: " + "Sleeping for " + str(Config.acPowerOffSleepInSeconds) + " seconds.")
            time.sleep(Config.acPowerOffSleepInSeconds)

            # Power Up Server Blade
            if Config.acPowerCycleStressTestPowerSwitchMethod == 0:
                powerPassOrFail, response = AcPowerIpSwitch.SetPowerOnOff(Config.acPowerIpSwitchOutlet, 1)
            elif Config.acPowerCycleStressTestPowerSwitchMethod == 1:
                powerPassOrFail, response = _PowerOnOffByRackManager('On')
            if powerPassOrFail:
                UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: Server blade powered up.")
            else:
                UtilLogger.verboseLogger.error("AcPowerCycleStressTest.py: Failed to power up server blade.")
            cyclePassOrFail &= powerPassOrFail

            # Ping BMC until it responds
            pingPassOrFail, decompEndTime = Helper.PingAndCheckResponse(Config.acPowerOnSleepInSeconds, Config.bmcIpAddress)
            if pingPassOrFail:
                fwDecompList.append(decompEndTime)
            cyclePassOrFail &= pingPassOrFail

            # Connect to BMC via SSH and test to see if 
            #   boot to BMC Start screen can be detected
            cyclePassOrFail &= Helper.SshBootToBMCStartScreenTest( cycleStartTime, username, password, "j2010" )
            if( cyclePassOrFail ):
                UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: Got the BMC command prompt")
                cyclePassOrFail &= True
            else:
                UtilLogger.verboseLogger.error("AcPowerCycleStressTest.py: Failed to get the BMC command prompt")
                cyclePassOrFail &= False

            # Waiting BMC query logs
            time.sleep(BMCLogQueryTime)

            # Create log snapshot on BMC
            cmdPassOrFail, _ = _SnapshotLogsOnBMC()
            if cmdPassOrFail:
                UtilLogger.verboseLogger.info("%s: Create snapshot succees!" %(fileName))
                verifyPassOrFail, unexpectedSels = _VerifySelAgainstXmlList(interfaceParams, \
                './J2010TestScripts/XmlFiles/accyclesellist.xml')
            else:
                UtilLogger.verboseLogger.info("%s: Create snapshot failed!" %(fileName))
                verifyPassOrFail = False

            if verifyPassOrFail:
                UtilLogger.verboseLogger.info("%s: All SEL Event Log are correct!" %(fileName))
            else:
                UtilLogger.verboseLogger.info("%s: Verify SEL Event Log failed!" %(fileName))
                if unexpectedSels:
                    UtilLogger.verboseLogger.info("%s: Unexpected SEL Event Logs:" %(fileName))
                    for selEvent in unexpectedSels:
                        UtilLogger.verboseLogger.info("\t%s" %(selEvent))
                else:
                    UtilLogger.verboseLogger.info("%s: Failed! Miss required Event Log" %(fileName))
            cyclePassOrFail &= verifyPassOrFail

            # Define request variables
            getResource = 'redfish/v1/Chassis/System/MainBoard'
            tryGet = 0
            # Send REST API and verify response
            waitTime = time.time()
            while( (time.time() - waitTime) < Config.bootToOsSleepInSeconds ):
                cmdPassOrFail, response = RedFish.GetResourceValues(getResource)
                if cmdPassOrFail:
                    UtilLogger.verboseLogger.info("AcPowerCycleStressTest:" + \
                        " GET REST API for resource " + getResource + \
                        " passed with status code " + str(response.status_code) + \
                        " and response text: " + str(response.text))
                    break
                else:
                    if response is not None:
                        UtilLogger.verboseLogger.error("AcPowerCycleStressTest:" + \
                            " GET REST API for resource " + getResource + \
                            " failed with status code " + str(response.status_code) + \
                            " and response text: " + str(response.text))
                    else:
                        tryGet += 1
                        UtilLogger.verboseLogger.error("AcPowerCycleStressTest:  === try " + str(tryGet) +" ===\n" +\
                            " GET REST API for resource " + getResource + \
                            " failed with response None.")
                        time.sleep(3)
            # Verify test cycle
            if cyclePassOrFail:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " AcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " AcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                cyclesPassed += 1
            else:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " AcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " AcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                cyclesFailed += 1
            UtilLogger.verboseLogger.info("")
            testCycle += 1
            testPassOrFail &= cyclePassOrFail

        # Log FW Decompression Results
        Helper.LogFwDecompressionResults(fwDecompList)

        # Print Test Summary results
        endTime = time.time()
        UtilLogger.consoleLogger.info(\
            "AC Power Cycle over REST Stress Test" + \
            " Summary - Cycles Passed: " + \
            str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
            " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
            " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
        UtilLogger.verboseLogger.info(\
            "AC Power Cycle over REST Stress Test" + \
            " Summary - Cycles Passed: " + \
            str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
            " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
            " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
    except Exception, e:
        UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: exception occurred - " + \
            str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global testPassOrFail
    return testPassOrFail

# Verify SEL log in Xml list
def _VerifySelAgainstXmlList(interfaceParams, selListXml):

    # Validate input parameters.
    assert selListXml != None
    assert os.path.isfile(selListXml)

    # Initialize results.
    selPassOrFail = False
    unexpectedSels = None

    # Get Sel entries
    cmdPassOrFail, LogFromZipFile = _GetAndUnZip()

    if cmdPassOrFail:
        cmdPassOrFail, BMCLogs, BMCLogsNumber = LogParser(LogFromZipFile)
    else:
        return selPassOrFail, unexpectedSels

    if cmdPassOrFail:
        UtilLogger.verboseLogger.info("%s: Get log data success!" %(fileName))
    else:
        UtilLogger.verboseLogger.error("%s: Parsing log failed!" %(fileName))
        return selPassOrFail, unexpectedSels

    actualSelList = []
    for Log in BMCLogs:
        actualSelList.append(Log['Message'])

    # Validate the returned SEL log events against list of SEL events
    # in input selListXml.
    selReqList = []  # List containing all required SEL events.
                     # Each element in the list is a nested list [Event_Text, duplicate],
                     # where Event_Text is an SEL event as a string, and duplicate
                     # is an integer indicating whether the event is allowed to be
                     # used as a duplicate or not (-1: allow as duplicate, 1: only
                     # use once (no duplicate, hasn't been used yet), 0: can no longer
                     # be used (no duplicate, already used once).
    selOptList = []  # List containing all optional SEL events.
                     # Each element in the list is a nested list [Event_Text, duplicate],
                     # where Event_Text is an SEL event as a string, and duplicate
                     # is an integer indicating whether the event is allowed to be
                     # used as a duplicate or not (-1: allow as duplicate, 1: only
                     # use once (no duplicate, hasn't been used yet), 0: can no longer
                     # be used (no duplicate, already used once).
    # Parse the input XML file to get selReqList and selOptList.
    xmlParserObj = XmlParser.XmlParser(selListXml)
    if not xmlParserObj.root:
        UtilLogger.verboseLogger.error("%s: failed to parse input XML file." %(fileName))
        return selPassOrFail, unexpectedSels
    for selEntry in xmlParserObj.root:
        required = (selEntry.attrib["required"] == "true")
        selText = selEntry.attrib["contains"]
        allowDupl = (selEntry.attrib["allowduplicates"] == "true")
        if required:  # Required event log.
            if allowDupl:
                selReqList.append([selText, -1])
            else:
                selReqList.append([selText, 1])
        else:  # Optional event log.
            if allowDupl:
                selOptList.append([selText, -1])
            else:
                selOptList.append([selText, 1])

    # Ready to do the validation.
    # Verify whether all required event logs are in the list of actual event logs.
    AreAllReqIn = True  # Indicates wether all required events were found (True) in
                        # list of actual event or not (False).
    for event in selReqList:
        IsEventIn = False
        for actualEvent in actualSelList:
            if event[0] in actualEvent:
                IsEventIn = True
                break
        if not IsEventIn:
            AreAllReqIn = False
            break

    # Verify whether all actual events are either required or optional and nothing
    # else.
    AreAllActualIn = True  # Indicates whether all actual events are either required
                           # or optional and nothing else (True) or not (False).
    unexpectedSels = []
    selValidList = selReqList + selOptList
    for event in actualSelList:
        IsEventIn = False
        for validEvent in selValidList:
            if validEvent[0] in event:
                if validEvent[1] == 0:
                    break  # Event already matched and cannot be duplicate, hence cannot
                           # be matched again.
                           # This SEL record (variable event) is a duplicate.
                if validEvent[1] == 1:
                    validEvent[1] = 0  # Mark event as already matched and no duplicate
                                       # is allowed.
                IsEventIn = True
                break
        if not IsEventIn:
            AreAllActualIn = False
            unexpectedSels.append(event)
            # We don't break here in order to find all unexpected SEL events.

    # Ready to return results.
    if AreAllReqIn and AreAllActualIn:
        selPassOrFail = True
        unexpectedSels = None
    elif not AreAllActualIn:
        selPassOrFail = False
    else:  # AreAllActualIn = True, AreAllReqIn = False.
        selPassOrFail = False
        unexpectedSels = None

    return selPassOrFail, unexpectedSels

# Use Rack Manager to turn on/off BMC.
# Note: This function is for Quanta team to test the script.
def _PowerOnOffByRackManager(PowerSwitch, RMSlotNumber=Config.BMCSlotIDOnRM, RackManagerIP=Config.RackManagerIPAddress,\
                             RMUsername=Config.RackManagerUsername, RMPasswaord=Config.RackManagerPassword):

    if (not RMSlotNumber) or (not RackManagerIP) or (not RMUsername) or (not RMPasswaord):
        UtilLogger.verboseLogger.info(\
        "%s: Some of rack manager arguments in Config.py are empty. Failed to execute rack manager command!" %(fileName))
        return False, None

    # Initial command
    execCmds = ['\n']
    execCmds.append('wcscli setpower' + PowerSwitch + ' -i ' + str(RMSlotNumber) + '\n')

    try:
        execPassOrFail, sshOutputs, parsedCmdOutputs = Ssh.sshExecuteCommand(execCmds,\
         username=RMUsername, password=RMPasswaord, connectAddress=RackManagerIP)
        # Parcing log number
        if execPassOrFail:
            tokens = sshOutputs[1].split()
            for word in tokens:
                if word == 'Success:':
                    return True, sshOutputs[1]
        else:
            UtilLogger.verboseLogger.info("%s: Execute PowerOnOff commmand failed" %(fileName))

    except Exception, e:
        UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))

    return False, None

# Clear BMC Log
def _ClearBMCLog():
    resource = 'redfish/v1/Managers/System/LogServices/Log/Actions/LogService.ClearLog'
    # Empty payload
    Payload = {}
    Payload["data"] = []

    # Send REST Post request
    cmdPassOrFail, response = RedFish.PostResourceValues(resource, Payload)

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

            # Try delete log-snapshot.zip on BMC
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
    retryInterval = 5
    resource = 'redfish/v1/Managers/System/LogServices/Log/Actions/LogService.LogSnapshot'
    # Empty payload
    Payload = {}
    Payload["data"] = []

    # Send REST Post request, and retry if failed.
    MaxTryTimes = 5
    for tryTimes in range(MaxTryTimes):
        UtilLogger.verboseLogger.info("SnapshotLogsOnBMC try %s" %(tryTimes+1))
        cmdPassOrFail, response = RedFish.PostResourceValues(resource, Payload)
        if cmdPassOrFail:
            break
        time.sleep(retryInterval)

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
