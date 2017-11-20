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

# Built-in modules.
import datetime
import math
from subprocess import Popen, PIPE
import os
import re
import time
import types

# Project modules.
import Config
from Helper import calc2sComplementHexString2Int
import UtilLogger
import XmlParser

# Function runs input command
# on IpmiUtil and returns response
def RunIpmiUtil(*args):

    # Check OS and set ipmiUtilFilePath accordingly
    ipmiUtilFilePath = ''
    if Config.currentOs == Config.osNameWindows: # Windows
        ipmiUtilFilePath = Config.ipmiUtilFilePath
    elif Config.currentOs == Config.osNameLinux: # Linux
        ipmiUtilFilePath = Config.ipmiUtilLinuxFilePath

    # Create parameter list to run on shell
    processCmd = [ ipmiUtilFilePath ]
    for arg in args:
        for param in arg:
            processCmd.append(param)

    # Run IpmiUtil and get stdout and stderr
    process = Popen(processCmd, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()

    # Print additional output to verbose log
    # if debugEn is True
    if Config.debugEn:
        commandRun = ""
        for arg in args:
            for param in arg:
                commandRun += " " + str(param)
        UtilLogger.verboseLogger.info("RunIpmiUtil: Command run by IpmiUtil: " + \
            commandRun)
        UtilLogger.verboseLogger.info("RunIpmiUtil: Command output by IpmiUtil: " + \
            str(out))

    return out, err

#region IpmiUtil Commands

# Dictionary of key : [string list] pairs that define arguments for 
# specified IpmiUtil commands
IpmiUtilCmds = {
    'raw' : [ 'cmd' ],
    'powercycle' : [ 'power', '-c' ],
    'bladeon' : [ 'power', '-u' ],
    'bladeoff' : [ 'power', '-d' ],
    'getbladehealth' : [ 'cmd' ],
    'getfru' : [ 'fru' ],
    'getbladepower' : [ 'dcmi', 'power', 'get' ],
    'setnextboot2bios' : [ 'power', '-b' ],
    'setnextboot2efi' : [ 'power', '-e' ],
    'setnextboot2removable' : [ 'power', '-f' ],
    'setnextboot2hdd' : [ 'power', '-h' ],
    'setnextboot2network' : [ 'power', '-p' ],
    'wcsfile' : [ 'wcs', 'file' ]
    }

# Function uses IpmiUtil Wcs Extention
# to run commands defined in specified filePath
def RunWcsFile(interfaceParams, filePath):

    # Default: cmd failed
    cmdPassOrFail = False
    respData = []
    processCmd = []

    # Check that file exists
    if not os.path.isfile(filePath):
            UtilLogger.verboseLogger.error(\
                "RunWcsFile: file path " + \
                filePath + " is invalid. Will not execute.")
    else:
        # Construct command line to execute with IpmiUtil
        for cmdParam in IpmiUtilCmds.get('wcsfile'):
            processCmd.append(cmdParam)
        processCmd.append(filePath)
        for interfaceParam in interfaceParams:
            processCmd.append(interfaceParam)

        # Process command using RunIpmiUtil
        out, err = RunIpmiUtil(processCmd)
        if err:
            UtilLogger.verboseLogger.error("Received error for RunIpmiUtil: " + err)
        else:
            # Parse output
            cmdPassOrFail = True
            respData = out

    return cmdPassOrFail, respData

def SendRawCmd(interfaceParams, netFn, cmd, rawBytesList):

    # Default: cmd failed
    cmdPassOrFail = False
    respData = []
    processCmd = []

    # Convert NetFn for use with IpmiUtil
    # [7:2] : Netfn ; [1:0] : Lun
    fnLun = '00'
    if netFn is not '00' and netFn:
        fnLun = hex(int(netFn, 16) << 2).lstrip("0x")

    # Construct command line to execute with IpmiUtil
    for cmdParam in IpmiUtilCmds.get('raw'):
        processCmd.append(cmdParam)
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)
    processCmd.append(Config.bmcBusId)
    processCmd.append(Config.bmcSlaveAddr)
    processCmd.append(fnLun)
    processCmd.append(cmd)
    for rawByte in rawBytesList:
        processCmd.append(rawByte)

    # Process command using RunIpmiUtil
    out, err = RunIpmiUtil(processCmd)
    if err:
        UtilLogger.verboseLogger.error("Received error for RunIpmiUtil: " + err)
    else:
        # Parse output
        cmdPassOrFail, respData = GetRespData(out)

    return cmdPassOrFail, respData

# Function will send raw request packet to ME using 
# -m IpmiUtil parameter (SendMessage)
def SendRawCmd2ME(interfaceParams, rawBytesList):

    # Default: cmd failed
    cmdPassOrFail = False
    respData = []
    processCmd = []

    # Define -m parameter for IpmiUtil Send Message
    meParam = '-m' + \
        Config.ipmbChannel + \
        Config.meSlaveAddr + \
        Config.meLun

    # Construct command line to execute with IpmiUtil
    for cmdParam in IpmiUtilCmds.get('raw'):
        processCmd.append(cmdParam)
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)
    processCmd.append(meParam)
    for rawByte in rawBytesList:
        processCmd.append(rawByte)

    # Retry send message for max sendRawCmd2MEMaxRetryCount count
    retryCount = Config.ipmiUtilSendMsgMaxRetries
    while retryCount > 0:

        # Process command using RunIpmiUtil
        out, err = RunIpmiUtil(processCmd)

        if err:
            UtilLogger.verboseLogger.error("Received error for RunIpmiUtil: " + err)
            break
        else:
            # Parse output
            cmdPassOrFail, respData = GetRespData(out)

        # Check for non-Success completion codes
        # Allowed:
        #   0xCC Node Busy
        if not cmdPassOrFail and respData == 'c0':
            retryCount -= 1
        else:
            break

    return cmdPassOrFail, respData

# Function will parse respData
# from IpmiUtil output for IpmiUtil raw 'cmd'
def GetRespData(parseData):

    # Init variables
    parseSuccess = False
    parsedData = []

    # parse output
    for item in parseData.split("\n"):
        
        # Check for response data raw bytes
        if "respData" in item:

            # Extract raw bytes from output of syntax
            # "respData[len=<num>]: <rawByte> <rawByte>.."
            parsedData = item.split(": ")[1].split(" ")
            parseSuccess = True

            # Check that last byte is an integer
            if len(parsedData) > 0:
                if not parsedData[len(parsedData) - 1].isdigit():
                    parsedData.pop(len(parsedData) - 1)

            break
    
        # Check for completion code string if 
        # cmd execution failed
        elif "ccode" in item:

            # Command failed to execute
            # Retrieve completion code (ccode)
            # "..ccode <completion code>.."
            itemList = item.split(" ")
            parsedData = itemList[itemList.index("ccode") + 1]

            break

        # Check for "completed successfully" string
        # This scenario arises when a command has 00 completion code
        # but no response bytes
        elif "completed successfully" in item:
            parseSuccess = True
            parsedData = 'No Response Bytes'

    return parseSuccess, parsedData

# Funtion will get sensor ID using 'IpmiUtil.exe sensor'
# Inputs:
#   interfaceParams (list; string): interface parameters for LAN+/KCS
#   sensorName (string): name of sensor 
#       as it appears in IpmiUtil sensor reading output
# Outputs:
#   parseSuccess (bool): if sensor reading is success (True)
#       or failure (False)
#   sensorId (string): 
def GetIpmiUtilSensorId(interfaceParams, sensorName):

    # Init variables
    parseSuccess = False
    sensorId = None
    processCmd = []

    # Generate IpmiUtil command
    processCmd.append('sensor')
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)

    # Get sensor reading using 'IpmiUtil.exe sensor -i <sdrId>'
    out, err = RunIpmiUtil(\
        processCmd)
    if err:
        UtilLogger.verboseLogger.error("Received error for RunIpmiUtil: " + err)
        sensorReading = err
    else:
        # Parse output
        for item in out.split("\n"):
        
            # Check for response data raw bytes
            if (IsThisSensor(item, sensorName)):

                # Extract sensor reading from output of syntax
                # "<sensor> = <> OK   <sensorReading> ..."
                sensorId = item.split()[0]
                parseSuccess = True

                break

    return parseSuccess, sensorId

#endregion

# Funtion will get sensor reading using 'IpmiUtil.exe sensor -i <sdrId>'
# Inputs:
#   interfaceParams (list; string): interface parameters for LAN+/KCS
#   sdrId (string, formatted as hex e.g. '0f'): SDR ID of sensor to be read
#   sensorName (string): name of sensor 
#       as it appears in IpmiUtil sensor reading output
# Outputs:
#   parseSuccess (bool): if sensor reading is success (True)
#       or failure (False)
#   sensorReading (string): 
def GetIpmiUtilSensorReading(interfaceParams, sdrId, sensorName):

    # Init variables
    parseSuccess = False
    sensorReading = []
    processCmd = []

    # Generate IpmiUtil command
    processCmd.append('sensor')
    processCmd.append('-i')
    processCmd.append(sdrId)
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)

    # Get sensor reading using 'IpmiUtil.exe sensor -i <sdrId>'
    out, err = RunIpmiUtil(\
        processCmd)
    if err:
        UtilLogger.verboseLogger.error("Received error for RunIpmiUtil: " + err)
        sensorReading = err
    else:
        # Parse output
        for item in out.split("\n"):
        
            # Check for response data raw bytes
            if (IsThisSensor(item, sensorName)):

                # Extract sensor reading from output of syntax
                # "<sensor> = <> OK   <sensorReading> ..."
                parsedData = item.split(sensorName)[1].split()[3]
                parseSuccess = True

                # Convert sensor reading to float
                sensorReading = float(parsedData)

                break

    return parseSuccess, sensorReading

"""
This method checks whether sensor reading 'sensorReadingLine' corresponds to sensor 'sensorName' or not.

Input Parameters:
    sensorReadingLine: A line returned by IPMI command 'sensor' or 'sensor -i <sensorID>' for a sensor reading.
    sensorName: A sensor name.

Output:
    Boolean True if sensorReadingLine corresponds to the reading for sensorName and False otherwise.
"""
def IsThisSensor(sensorReadingLine, sensorName):

    # Validate input parameters.
    assert(sensorReadingLine != None)
    assert(sensorName != None)
    assert(type(sensorReadingLine) is types.StringType)
    assert(type(sensorName) is types.StringType)

    # Generate regular expression to search in 
    # sensorReadingLine
    regEx = sensorName + '\s+='
    if re.compile(regEx).search(sensorReadingLine):
        return True

    return False

#endregion

"""
This method verifies the SEL (System Events Log) by comparing the logs returned
from the IPMI command 'IpmiUtil sel -u' (actual log events) with a list of log
events in an XML file containing the required and optional log events.

Input Parameters:
    interfaceParams: List of all parameters needed to execute the IPMI interface
                     call 'IpmiUtil sel -u'.
    selListXml: XML file containing all log events to compare against.
                It contains all required and optional SEL events.
                This is the full path and file name.

Return Values:
    selPassOrFail: This is a boolean variable.
                   True: If all required SEL events are in the list of actual log events,
                         and every event in the actual log events list is either
                         required or optional and nothing else.
    unexpectedSels: List of all unexpected SEL events (i.e. neither required nor optional)
                    found in the list of actual log events.
                    It has the value None if there is no such SEL event (i.e. all actual
                    log events are either required or optional and nothing else).
"""
def VerifySelAgainstXmlList(interfaceParams, selListXml):

    # Validate input parameters.
    assert(interfaceParams != None)
    assert(selListXml != None)
    assert(os.path.isfile(selListXml))

    # Initialize results.
    selPassOrFail = False
    unexpectedSels = None

    # Get Sel entries
    processCmd = ['sel', '-u']
    for param in interfaceParams:
        processCmd.append(param)
    out, err = RunIpmiUtil(processCmd)  # out and err are strings.
    if err:
        UtilLogger.verboseLogger.error("IpmiUtil.py - VerifySelAgainstXmlList(): " + \
            "IPMI Command 'sel -u' Error: " + str(err))
        return selPassOrFail, unexpectedSels
    else:
        UtilLogger.verboseLogger.info("IpmiUtil.py - VerifySelAgainstXmlList(): " + \
            "IPMI Command 'sel -u' returned SEL events: \n" + str(out))

    # No errors from IPMI Command 'sel -u'.

    # Get list of all SEL records returned from command (this is the
    # list of actual event logs).
    # First get list of all log messages returned from command (this
    # includes some information other than the SEL events, such as
    # BMC version, IPMI version, etc.).
    rawSelList = out.splitlines()  # List of lines in the string out.
                                   # Each line is either an SEL event
                                   # or some other info.
    # Next we get the list of SEL events only.
    count = len(rawSelList)
    headerIndex = -1  # Index of header of SEL records in list.
    for i in range(count-1):
        if (rawSelList[i].startswith("RecId Date/Time")):
            headerIndex = i
            break
    if (headerIndex == -1):
        UtilLogger.verboseLogger.error("IpmiUtil.py - VerifySelAgainstXmlList(): " + \
            "Header for SEL Records was not found!")
        return selPassOrFail, unexpectedSels
    actualSelList = rawSelList[headerIndex+1 : count-1]

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
        UtilLogger.verboseLogger.error("IpmiUtil.py - VerifySelAgainstXmlList(): " + \
                                       "failed to parse input XML file.")
        return selPassOrFail, unexpectedSels
    for selEntry in xmlParserObj.root:
        required = (selEntry.attrib["required"] == "true")
        selText = selEntry.attrib["contains"]
        allowDupl = (selEntry.attrib["allowduplicates"] == "true")
        if (required):  # Required event log.
            if (allowDupl):
                selReqList.append([selText, -1])
            else:
                selReqList.append([selText, 1])
        else:  # Optional event log.
            if (allowDupl):
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
                if (validEvent[1] == 0):
                    break  # Event already matched and cannot be duplicate, hence cannot
                           # be matched again.
                           # This SEL record (variable event) is a duplicate.
                if (validEvent[1] == 1):
                    validEvent[1] = 0  # Mark event as already matched and no duplicate
                                       # is allowed.
                IsEventIn = True
                break
        if not IsEventIn:
            AreAllActualIn = False
            unexpectedSels.append(event)
            # We don't break here in order to find all unexpected SEL events.

    # Ready to return results.
    if (AreAllReqIn and AreAllActualIn):
        selPassOrFail = True
        unexpectedSels = None
    elif (not AreAllActualIn):
        selPassOrFail = False
    else:  # AreAllActualIn = True, AreAllReqIn = False.
        selPassOrFail = False
        unexpectedSels = None

    return selPassOrFail, unexpectedSels


"""
This method verifies whether the reading for the list of sensors in file 'sensorListFile'
is whithin the acceptable range of values for each sensor.

Input Parameters:
    interfaceParams: List of all parameters needed to execute the IPMI interface
                     call 'IpmiUtil sensors'.
    sensorListFile: XML file containing the needed information regarding the sensors
                    to monitor.
                    This includes the absolute or relative directory path of the file
                    and the file name. If no directory path is specified, then it is
                    assumed that the file is in the current working directory.
                    An example of this file would be: <platform>TestScripts\XmlFiles\sensorlistxmlfile.xml.

Return Value:
    True if all sensors pass (actual value for all sensors is within expected range) and False
    otherwise.
"""
def VerifyThresholdSensors(interfaceParams, sensorListFile):

    # Validate input parameters.
    assert(interfaceParams != None)
    assert(sensorListFile != None)
    assert(os.path.isfile(sensorListFile))

    methodResult = True  # Method result (True/False).

    sensorList = []  # List containing information about each sensor to monitor.
                     # Each element in the list is a tuple =
                     # (sensorName, sensorId, nominalValue, tolerance),
                     # where sensorName and sensorId are strings, and
                     # nominalValue and tolerance are floats.

    xmlParserObj = XmlParser.XmlParser(sensorListFile)
    if not xmlParserObj.root:
        UtilLogger.verboseLogger.error("ImpiUtil.py - VerifyThresholdSensors() - XmlParser: " + \
                                       "failed to parse sensor list XML file.")
        return False

    # Store info regarding all sensors to be monitored in sensorList.
    for sensorEntry in xmlParserObj.root:
        sensorName = sensorEntry.attrib["name"]
        gotSensorIdSuccess, sensorId = GetIpmiUtilSensorId(interfaceParams, sensorName)
        if (not gotSensorIdSuccess):
            UtilLogger.verboseLogger.error("IpmiUtil.py - VerifyThresholdSensors(): " + \
                                       "Failed to get sensor ID for sensor '%s'." % sensorName)
            return False
        sensorInfo = SdrInfo([ sensorId[2] + sensorId[3], \
            sensorId[0] + sensorId[1] ], sensorName, interfaceParams)
        updatePassOrFail = sensorInfo.UpdateSdrInfo(interfaceParams) # Update SDR Info for sensor
        if updatePassOrFail:
            UtilLogger.verboseLogger.info("SensorThresholdStressTest.py - Setup(): " + \
                "Successfully received sensor thresholds for sensor '%s'." % sensorName)
        else:
            UtilLogger.verboseLogger.error("SensorThresholdStressTest.py - Setup(): " + \
                "Failed to get sensor thresholds for sensor '%s'." % sensorName)
        sensorList.append((sensorName, sensorId, sensorInfo))

    # Compare actual sensor values with expected values and log results.
    UtilLogger.verboseLogger.info('')
    UtilLogger.verboseLogger.info("ImpiUtil.py - VerifyThresholdSensors(): Starting sensor readings validation.")
    for sensorEntry in sensorList:
        
        # Do the validation for this sensor.
        sensorName = sensorEntry[0]
        sensorId = sensorEntry[1]
        sensorSdrInfo = sensorEntry[2]

        if (sensorId == ""):  # We got an invalid sensor ID.
            # Log failure.
            UtilLogger.verboseLogger.info("Sensor Name: {} - Result: Fail - Got invalid sensor ID".format(sensorName))
            continue

        # Get reading for this sensor.
        sensorReadSuccess, sensorReading = GetIpmiUtilSensorReading(interfaceParams, sensorId, sensorName)
        if (not sensorReadSuccess):
            UtilLogger.verboseLogger.error("ImpiUtil.py - VerifyThresholdSensors(): " + \
                                    "Failed to get sensor reading for sensor '%s'." % sensorName)
            methodResult = False
            # Log failure.
            UtilLogger.verboseLogger.info("Sensor Name: {} - Result: Fail".format(sensorName))
            continue

        # Define acceptable sensor reading range
        validRangeLow = 0.0  # Lower bound of valid range.
        validRangeHigh = None  # Upper bound of valid range.

        # Get acceptable sensor reading range
        getPassOrFail, validRangeLow, validRangeHigh = sensorSdrInfo.GetAcceptableThresholdRange()

        # Validate if sensor reading is in range
        valid = (sensorReading > validRangeLow)
        if validRangeHigh is not None: # make sure threshold defined for sensor
            valid &= sensorReading < validRangeHigh

        result = None  # Verification result.
        if (valid):
            result = 'Pass'
        else:
            result = 'Fail'
            methodResult = False

        # Log result.
        UtilLogger.verboseLogger.info("Sensor Name: {} - Result: {} - ".format(sensorName, result) + \
                                      "Acceptable Range: {} ... {} - Actual Value: {}".format(validRangeLow, validRangeHigh, sensorReading))

    UtilLogger.verboseLogger.info("")

    return methodResult

# Function verifies Get Nic Info completion code
# Note: function uses the following Config variables:
#   maxNicIndex: variable states the currently supported max Nic Index.
#       Function uses this variable to test the next index for 0xCC completion code
#   getNicInfoAllowCC: variable is a list of bool where each index corresponds
#       to the NIC index and specified whether the NIC index should be allowed to
#       return 0xCC completion code (True) or not (False). The length of this variable
#       must match (maxNicIndex + 1)
#
# Inputs: 
#   interfaceParams (list; string): interface parameters for LAN+/KCS 
#
# Outputs: 
#   cmdPassOrFail (bool): all NIC indexes return the expected completion code
def VerifyGetNicInfo(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetNicInfo variables
    cmdName = 'GetNicInfo'
    cmdNum = Config.cmdGetNicInfo
    netFn = Config.netFnOem30

    # Verify Config variable getNicInfoAllowCC correct length
    if len(Config.getNicInfoAllowCC) != (Config.maxNicIndex + 1):
        UtilLogger.verboseLogger.error("IpmiUtil.VerifyGetNicInfo: " + \
            "Config variable list getNicInfoAllowCC fails to match " + \
            "expected length. Expected: " + str(Config.maxNicIndex + 1) + \
            " Actual: " + str(len(Config.getNicInfoAllowCC)))
        return False, respData

    # Define sample raw bytes (config defines max NIC index)
    for idx in range(0, Config.maxNicIndex + 1):

        # Set rawByte to NIC index
        nicIdx = hex(idx).lstrip('0x')
        if idx == 0:
            nicIdx = '0'
        rawBytesList = [ nicIdx ]

        # Send raw bytes via IpmiUtil
        nicPassOrFail, respData = SendRawCmd(interfaceParams, \
            netFn, cmdNum, rawBytesList)

        # Verify response
        if nicPassOrFail:
            UtilLogger.verboseLogger.info(cmdName + \
                ": Command passed for nic 0x"\
                + nicIdx + ": " + str(respData))
        else:
            if Config.getNicInfoAllowCC[idx] and respData == 'cc':
                UtilLogger.verboseLogger.info(cmdName + \
                    ": Command passed for nic 0x"\
                    + nicIdx + ". Completion Code: " + \
                    str(respData) + " 0xCC completion code allowed.")
                nicPassOrFail = True
            else:
                UtilLogger.verboseLogger.error(cmdName + \
                    ": Command failed for nic 0x" + nicIdx + \
                    ". Completion Code: " + str(respData))
        cmdPassOrFail &= nicPassOrFail

    # Test for completion code 0xCC for NIC index past max
    rawBytesList = [ hex(Config.maxNicIndex + 1).lstrip('0x') ]
    
    # Send raw bytes via IpmiUtil
    nicPassOrFail, respData = SendRawCmd(interfaceParams, \
        netFn, cmdNum, rawBytesList)

    # Verify 0xCC completion code
    if not nicPassOrFail and respData == 'cc':
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed for 0xCC test with nic index " + \
            str(rawBytesList))
    else:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command failed for 0xCC nic test with nic index " + \
            str(rawBytesList) + " and completion code: " + str(respData))
        cmdPassOrFail = False

    return cmdPassOrFail

class SdrInfo:

    # Define Threshold Name Constants
    constUpperNonRecName = 'Upper Non-Recoverable Threshold'
    constUpperCritName = 'Upper Critical Threshold'
    constUpperNonCritName = 'Upper Non-Critical Threshold'
    constLowerNonRecName = 'Lower Non-Recoverable Threshold'
    constLowerCritName = 'Lower Critical Threshold'
    constLowerNonCritName = 'Lower Non-Critical Threshold'

    # Define Response Index Constants
    constSensorInitIdx = 12
    constLowerThresholdReadingMaskLsbIdx = 16
    constLowerThresholdReadingMaskMsbIdx = 17
    constSettableThresoldMaskIdx = 20
    constLinearizationIdx = 25
    constMValLsbIdx = 26
    constMValMsbIdx = 27
    constBValLsbIdx = 28
    constBValMsbIdx = 29
    constRExpBExpIdx = 31
    constUpperNonRecThresholdIdx = 38
    constUpperCritThresholdIdx = 39
    constUpperNonCritThresholdIdx = 40
    constLowerNonRecThresholdIdx = 41
    constLowerCritThresoldIdx = 42
    constLowerNonCritThresholdIdx = 43

    # Define Sensor Initialization Byte Offsets
    constSensorInitThresholdsOffset = 4

    # Define Readable Threshold Mask Offsets
    constUpperNonRecMaskOffset = 5
    constUpperCritMaskOffset = 4
    constUpperNonCritMaskOffset = 3
    constLowerNonRecMaskOffset = 2
    constLowerCritMaskOffset = 1
    constLowerNonCritMaskOffset = 0

    # Define Lower Threshold Reading Mask Offsets
    constUpperNonRecLowerThreshGoingHighMaskOffset = 11
    constUpperNonRecLowerThreshGoingLowMaskOffset = 10
    constUpperCritLowerThreshGoingHighMaskOffset = 9
    constUpperCritLowerThreshGoingLowMaskOffset = 8
    constUpperNonCritLowerThreshGoingHighMaskOffset = 7
    constUpperNonCritLowerThreshGoingLowMaskOffset = 6
    constLowerNonRecLowerThreshGoingHighMaskOffset = 5
    constLowerNonRecLowerThreshGoingLowMaskOffset = 4
    constLowerCritLowerThreshGoingHighMaskOffset = 3
    constLowerCritLowerThreshGoingLowMaskOffset = 2
    constLowerNonCritLowerThreshGoingHighMaskOffset = 1
    constLowerNonCritLowerThreshGoingLowMaskOffset = 0

    # Define dictionary with the following constants:
    #   Key: Threshold Name (string)
    #   Value:
    #     [0]: Threshold Reading Sdr Response Index (int)
    #     [1]: Threshold Reading Value (float)
    #     [2]: Readable Threshold Mask Response Byte Offset (int)
    #     [3]: Lower Threshold Reading Mask (Going High) Response Byte Offset (int)
    #     [4]: Lower Threshold Reading Mask (Going Low) Response Byte Offset (int)
    #     [5]: Is Threshold Going High (True) or Low (False) or neither (None)
    constDictThresholdInfo = {\
        constUpperNonRecName : \
        [ constUpperNonRecThresholdIdx, None, 5, 11, 10, None ], \
        constUpperCritName : \
        [ constUpperCritThresholdIdx, None, 4, 9, 8, None ], \
        constUpperNonCritName : \
        [ constUpperNonCritThresholdIdx, None, 3, 7, 6, None ], \
        constLowerNonRecName : \
        [ constLowerNonRecThresholdIdx, None, 2, 5, 4, None ], \
        constLowerCritName : \
        [ constLowerCritThresoldIdx, None, 1, 3, 2, None ], \
        constLowerNonCritName : \
        [ constLowerNonCritThresholdIdx, None, 0, 1, 0, None ]}

    # Define index constants for contDicThersholdInfo
    constThresholdReadingIdxDictIdx = 0
    constThresholdReadingDictIdx = 1
    constReadableThresholdMaskOffsetDictIdx = 2
    constLowerThresholdMaskGoingHighOffsetDictIdx = 3
    constLowerThresholdMaskGoingLowOffsetDictIdx = 4
    constThresoldGoingHighOrLowDictIdx = 5

    # Constructor
    def __init__(self, sensorId, sensorName, interfaceParams):

        # SDR General Info Variables
        self.sensorId = sensorId # [ LS byte, MS byte ]
        self.sensorName = sensorName

        # SDR Sensor Threshold Variables
        self.sensorUpperNonRecThreshold = None # Upper Non-Recoverable Threshold
        self.sensorUpperCritThreshold = None # Upper Critical Threshold
        self.sensorUpperNonCritThreshold = None # Upper Non-Critical Threshold
        self.sensorLowerNonRecThreshold = None # Lower Non-Recoverable Threshold
        self.sensorLowerCritThresold = None # Lower Critical Threshold
        self.sensorLowerNonCritThreshold = None # Lower Non-Critical 

        # SDR Sensor Threshold Going High Or Low Variables
        self.sensorUpperNonRecGoingHighOrLow = None
        self.sensorUpperCritGoingHighOrLow = None
        self.sensorUpperNonCritGoingHighOrLow = None
        self.sensorLowerNonRecGoingHighOrLow = None
        self.sensorLowerCritGoingHighOrLow = None
        self.sensorLowerNonCritGoingHighOrLow = None

        return

    def ConvertSensorReading(self, respData, rawReading):

        # Initialize local variables
        convertPassOrFail = False
        sensorReading = None
        linearizationType = respData[self.constLinearizationIdx]
        mValLsb = respData[self.constMValLsbIdx]
        mValMsb = hex(((int(respData[self.constMValMsbIdx], 16) >> 6) & 3))[2:] # bits [7:6]
        mVal = calc2sComplementHexString2Int(mValMsb + mValLsb, 10)
        bValLsb = respData[self.constBValLsbIdx]
        bValMsb = hex(((int(respData[self.constBValMsbIdx], 16) >> 6) & 3))[2:] # bits [7:6]
        bVal = calc2sComplementHexString2Int(bValMsb + bValLsb, 10)
        rExp = calc2sComplementHexString2Int(hex((int(respData[self.constRExpBExpIdx], 16) >> 4) & \
            int('0f', 16))[2:], 4) # 4-bit 2's complement with bits [7:4]
        bExp = calc2sComplementHexString2Int(hex(int(respData[self.constRExpBExpIdx], 16) & \
            int('0f', 16))[2:], 4) # 4-bit 2's complement with bits [4:0]

        # Convert Sensor Reading 
        sensorReading = float((mVal * int(rawReading, 16) + (bVal * (10**bExp))) * (10**rExp))

        # Linearize sensor reading based on Linearization Type with function f(x) so that y = f(x)
        if respData[self.constLinearizationIdx] == '00': # linear, y = x
            convertPassOrFail = True
        elif respData[self.constLinearizationIdx] == '01': # y = ln(x)
            sensorReading = math.log(sensorReading)
            convertPassOrFail = True
        elif respData[self.constLinearizationIdx] == '02': # y = log10(x)
            sensorReading = math.log10(sensorReading)
            convertPassOrFail = True
        elif respData[self.constLinearizationIdx]  == '03': # y = log2(x)
            sensorReading = math.log(sensorReading, 2)
            convertPassOrFail = True

        return convertPassOrFail, sensorReading

    # Convert Sensor Threshold from raw reading
    def ConvertSensorThreshold(self, respData, settableMaskOffset, rawReading):

        # Initialize local variables
        convertPassOrFail = False
        sensorReading = None

        # Check Sensor Init Thresholds Mask and Settable 
        if not (((int(respData[self.constSensorInitIdx], 16) >> \
            self.constSensorInitThresholdsOffset) & 1) and \
            ((int(respData[self.constSettableThresoldMaskIdx], 16) >> \
            settableMaskOffset) & 1)):
            return convertPassOrFail, sensorReading

        # Get if assertion event for 

        # Convert Sensor Reading based on linearization type
        convertPassOrFail, sensorReading = self.ConvertSensorReading(\
            respData, rawReading)

        return convertPassOrFail, sensorReading

    # Update SDR Info Variables
    def UpdateSdrInfo(self, interfaceParams):

        # Initialize local variables
        updatePassOrFail = False
        respData = None

        # Reserve SDR Repository via IPMI
        reserveSdrBytes = None # [ LS byte, MS byte ]
        cmdPassOrFail, respData = SendRawCmd(interfaceParams, Config.netFnStorage, \
            Config.cmdReserveSdrRepository, [])
        if cmdPassOrFail:
            if Config.debugEn:
                UtilLogger.verboseLogger.info('ReserveSdrRepository' + \
                    ': Command passed: ' + str(respData))
            reserveSdrBytes = respData
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error('ReserveSdrRepository' + \
                    ': Command failed. Completion Code: ' + str(respData))
            return False

        # Generate request data for Get SDR
        getSdrRequest = [ reserveSdrBytes[0], reserveSdrBytes[1], \
            self.sensorId[0], self.sensorId[1], '00', 'FF' ]

        # Update Sensor Threshold Values
        cmdPassOrFail, respData = SendRawCmd(interfaceParams, Config.netFnStorage, \
            Config.cmdGetSdr, getSdrRequest)
        if cmdPassOrFail:
            if Config.debugEn:
                UtilLogger.verboseLogger.info('GetSdr' + \
                    ': Command passed: ' + str(respData))
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error('GetSdr' + \
                    ': Command failed. Completion Code: ' + str(respData))
            return False

        # Parse Get SDR response to update SDR Info

        # Update sensor thresholds
        
        # Update Upper Non-Recoverable Threshold
        convertPassOrFail, sensorThreshold = self.ConvertSensorThreshold(\
            respData, self.constUpperNonRecMaskOffset, \
            respData[self.constUpperNonRecThresholdIdx])
        if convertPassOrFail:
            if Config.debugEn:
                UtilLogger.verboseLogger.info('SdrInfo.UpdateSdrInfo' + \
                    ': successfully converted Non-Recoverable Threshold for sensor ' + \
                    self.sensorName)
            self.sensorUpperNonRecThreshold = sensorThreshold
            updatePassOrFail = True
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error('SdrInfo.UpdateSdrInfo' + \
                    ': unable to convert Upper Non-Recoverable Threshold for sensor ' + \
                    self.sensorName)

        # Update Sensor Threshold Going High Or Low
        self.sensorUpperNonRecGoingHighOrLow = self.DetermineThresholdGoingHighOrLow(\
            respData, self.constUpperNonRecLowerThreshGoingHighMaskOffset, \
            self.constUpperNonRecLowerThreshGoingLowMaskOffset)

        # Update Upper Critical Threshold
        convertPassOrFail, sensorThreshold = self.ConvertSensorThreshold(\
            respData, self.constUpperCritMaskOffset, \
            respData[self.constUpperCritThresholdIdx])
        if convertPassOrFail:
            if Config.debugEn:
                UtilLogger.verboseLogger.info('SdrInfo.UpdateSdrInfo' + \
                    ': successfully converted Upper Critical Threshold for sensor ' + \
                    self.sensorName)
            self.sensorUpperCritThreshold = sensorThreshold
            updatePassOrFail = True
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error('SdrInfo.UpdateSdrInfo' + \
                    ': unable to convert Upper Critical Threshold for sensor ' + \
                    self.sensorName)

        # Update Sensor Threshold Going High Or Low
        self.sensorUpperCritGoingHighOrLow = self.DetermineThresholdGoingHighOrLow(\
            respData, self.constUpperCritLowerThreshGoingHighMaskOffset, \
            self.constUpperCritLowerThreshGoingLowMaskOffset)

        # Update Upper Non-Critical Threshold
        convertPassOrFail, sensorThreshold = self.ConvertSensorThreshold(\
            respData, self.constUpperNonCritMaskOffset, \
            respData[self.constUpperNonCritThresholdIdx])
        if convertPassOrFail:
            if Config.debugEn:
                UtilLogger.verboseLogger.info('SdrInfo.UpdateSdrInfo' + \
                ': successfully converted Upper Non-Critical Threshold for sensor ' + \
                self.sensorName)
            self.sensorUpperNonCritThreshold = sensorThreshold
            updatePassOrFail = True
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error('SdrInfo.UpdateSdrInfo' + \
                    ': unable to convert Upper Non-Critical Threshold for sensor ' + \
                    self.sensorName)

        # Update Upper Non-Critical Threshold Going High Or Low
        self.sensorUpperNonCritGoingHighOrLow = self.DetermineThresholdGoingHighOrLow(\
            respData, self.constUpperNonCritLowerThreshGoingHighMaskOffset, \
            self.constUpperNonCritLowerThreshGoingLowMaskOffset)

        # Update Lower Non-Recoverable Threshold
        convertPassOrFail, sensorThreshold = self.ConvertSensorThreshold(\
            respData, self.constLowerNonRecMaskOffset, \
            respData[self.constLowerNonRecThresholdIdx])
        if convertPassOrFail:
            if Config.debugEn:
                UtilLogger.verboseLogger.info('SdrInfo.UpdateSdrInfo' + \
                    ': successfully converted Lower Non-Recoverable Threshold for sensor ' + \
                    self.sensorName)
            self.sensorLowerNonRecThreshold = sensorThreshold
            updatePassOrFail = True
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error('SdrInfo.UpdateSdrInfo' + \
                    ': unable to convert Lower Non-Recoverable Threshold for sensor ' + \
                    self.sensorName)

        # Update Lower Non-Recoverable Threshold Going High Or Low
        self.sensorLowerNonRecGoingHighOrLow = self.DetermineThresholdGoingHighOrLow(\
            respData, self.constLowerNonRecLowerThreshGoingHighMaskOffset, \
            self.constLowerNonRecLowerThreshGoingLowMaskOffset)

        # Update Lower Critical Threshold
        convertPassOrFail, sensorThreshold = self.ConvertSensorThreshold(\
            respData, self.constLowerCritMaskOffset, \
            respData[self.constLowerCritThresoldIdx])
        if convertPassOrFail:
            if Config.debugEn:
                UtilLogger.verboseLogger.info('SdrInfo.UpdateSdrInfo' + \
                    ': successfully converted Lower Critical Threshold for sensor ' + \
                    self.sensorName)
            self.sensorLowerCritThresold = sensorThreshold
            updatePassOrFail = True
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error('SdrInfo.UpdateSdrInfo' + \
                    ': unable to convert Lower Critical Threshold for sensor ' + \
                    self.sensorName)

        # Update Lower Critical Threshold Going High Or Low
        self.sensorLowerCritGoingHighOrLow = self.DetermineThresholdGoingHighOrLow(\
            respData, self.constLowerCritLowerThreshGoingHighMaskOffset, \
            self.constLowerCritLowerThreshGoingLowMaskOffset)

        # Update Lower Non-Critical Threshold
        convertPassOrFail, sensorThreshold = self.ConvertSensorThreshold(\
            respData, self.constLowerNonCritMaskOffset, \
            respData[self.constLowerNonCritThresholdIdx])
        if convertPassOrFail:
            if Config.debugEn:
                UtilLogger.verboseLogger.info('SdrInfo.UpdateSdrInfo' + \
                    ': successfully converted Lower Non-Critical Threshold for sensor ' + \
                    self.sensorName)
            self.sensorLowerNonCritThreshold = sensorThreshold
            updatePassOrFail = True
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error('SdrInfo.UpdateSdrInfo' + \
                    ': unable to convert Lower Non-Critical Threshold for sensor ' + \
                    self.sensorName)

        # Update Lower Non-Critical Threshold Going High Or Low
        self.sensorLowerNonCritGoingHighOrLow = self.DetermineThresholdGoingHighOrLow(\
            respData, self.constLowerNonCritLowerThreshGoingHighMaskOffset, \
            self.constLowerNonCritLowerThreshGoingLowMaskOffset)

        return updatePassOrFail

    # Function will return the lowest threshold value for threshold going high
    # and the highest threshold value for threshold going low 
    # for the sensor and the associated threshold name
    # 
    # Input:
    #   self: SdrInfo self object
    # Outputs:
    #   getPassOrFail (bool): whether function returned acceptable range or not
    #                         Note: getPassOrFail returns true if validHighRange is not None
    #   validLowRange (float): minimum value in acceptable threshold range. Calculated
    #                          based on highest threshold value going low.
    #   validHighRange (float): maximum value in acceptable threshold range. Calculated
    #                          based on lowest threshold value going high.
    def GetAcceptableThresholdRange(self):

        # Initialize local variables
        getPassOrFail = False
        validLowRange = None
        validHighRange = None
        lowestThresholdName = None
        highestThresholdName = None
        thresholdDict = {\
            'Upper Non-Recoverable Threshold' : \
            [ self.sensorUpperNonCritThreshold, self.sensorUpperNonCritGoingHighOrLow ], \
            'Upper Critical Threshold': \
            [ self.sensorUpperCritThreshold, self.sensorUpperCritGoingHighOrLow ], \
            'Upper Non-Critical Threshold' : \
            [ self.sensorUpperNonCritThreshold, self.sensorUpperNonCritGoingHighOrLow ], \
            'Lower Non-Recoverable Threshold' : \
            [ self.sensorLowerNonRecThreshold, self.sensorLowerNonRecGoingHighOrLow ], \
            'Lower Critical Threshold' : \
            [ self.sensorLowerCritThresold, self.sensorLowerCritGoingHighOrLow ], \
            'Lower Non-Critical Threshold' : \
            [ self.sensorLowerNonCritThreshold, self.sensorLowerNonCritGoingHighOrLow ]}

        # Find threshold with lowest value going high and highest value going low
        for (pairKey, pairValue) in thresholdDict.iteritems():

            # Determine lowest threshold value for threshold going high
            if lowestThresholdName is not None:
                if pairValue[0] < thresholdDict[lowestThresholdName][0] and \
                    pairValue[1]:
                    lowestThresholdName = pairKey
            elif pairValue[1]:
                lowestThresholdName = pairKey

            # Determine highest threshold value for threshold going low
            if highestThresholdName is not None:
                if pairValue[0] > thresholdDict[highestThresholdName][0] and \
                    not pairValue[1] and pairValue[1] is not None:
                    highestThresholdName = pairKey
            elif not pairValue[1] and pairValue[1] is not None:
                highestThresholdName = pairKey

        # Verify valid high range
        if lowestThresholdName is not None and \
            thresholdDict[lowestThresholdName][0] is not None:
            getPassOrFail = True
            validHighRange = thresholdDict[lowestThresholdName][0]
            if Config.debugEn:
                UtilLogger.verboseLogger.info("IpmiUtil.GetAcceptableThresholdRange" + \
                    ": successfully determined high range value." + \
                    " Value: " + str(thresholdDict[lowestThresholdName][0]) + \
                    " Associated threshold: " + str(lowestThresholdName))
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error("IpmiUtil.GetAcceptableThresholdRange" + \
                    ": failed to determine high range value." + \
                    " Value: " + str(thresholdDict[lowestThresholdName][0]) + \
                    " Associated threshold: " + str(lowestThresholdName))

        # Verify valid low range
        if highestThresholdName is not None and \
            thresholdDict[highestThresholdName][0] is not None:
            validLowRange = thresholdDict[highestThresholdName][0]
            if Config.debugEn:
                UtilLogger.verboseLogger.info("IpmiUtil.GetAcceptableThresholdRange" + \
                    ": successfully determined low range value." + \
                    " Value: " + str(thresholdDict[highestThresholdName][0]) + \
                    " Associated threshold: " + str(highestThresholdName))
        else: # default to 0 if no low range defined
            validLowRange = 0.0
            if Config.debugEn:
                UtilLogger.verboseLogger.error("IpmiUtil.GetAcceptableThresholdRange" + \
                    " failed to determine low range value. Setting to default value: 0.0")

        return getPassOrFail, validLowRange, validHighRange

    def DetermineThresholdGoingHighOrLow(self, respData, goingHighMaskOffset, \
        goingLowMaskOffset):

        goingHighOrLow = None

        # Join Msb and Lsb for Lower Threshold Reading Mask Response bytes
        lowerThresholdReadingMaskBytes = respData[self.constLowerThresholdReadingMaskMsbIdx] + \
            respData[self.constLowerThresholdReadingMaskLsbIdx]

        # Check if threshold assertion is supported for going high or low
        goingHigh = bool((int(lowerThresholdReadingMaskBytes, 16) >> goingHighMaskOffset) & 1)
        goingLow = bool((int(lowerThresholdReadingMaskBytes, 16) >> goingLowMaskOffset) & 1)

        # Determine if going high or low
        if goingHigh:
            goingHighOrLow = True
        elif goingLow:
            goingHighOrLow = False
        
        return goingHighOrLow

class ConfigureFwUpdate:

    # Configure Firmware Update Request Variables
    cmdName = 'ConfigureFirmwareUpdate'
    cmdNum = Config.cmdConfigureFirmwareUpdate
    netFn = Config.netFnOem38
    
    # Configure Firmware Update General Variables
    componentByte = ''
    componentIdx = ''
    componentType = ''
    imageType = ''
    imageFileName = ''
    imageFilePath = ''
    imageFileNameBytes = []
    fwFileNameLenLimit = 60

    # Configure Firmware Update Static Component Variables
    compTypePsu = '10'
    compTypeBios = '20'
    compIdx1 = '01'
    compIdx2 = '02'

    # Configure Firmware Update Static Image Type Variables
    imageTypeFwBootloader = '00'
    imageTypeFwImageA = '01'
    imageTypeFwImageB = '02'

    # Configure Firmware Update Static Operation Variables
    opStartFwUpdate = '01'
    opAbortFwUpdate = '02'
    opQueryFwUpdate = '03'
    opResInvalidResValue = '00'
    opResFwImageNotFound = '01'
    opResFwUpdateNotStarted = '02'
    opResFwUpdateInProgress = '03'
    opResFwUpdateCompleted = '04'
    opResFwUpdateAborted = '05'
    opResFwImageCorrupted = '06'

    # Dictionary of key (hex string): value (string) pairs that define arguments for
    # Configure Firmware Update Component (Type/Index)
    configureFwUpdateComponent = {
        compIdx1 : 'Component Index 1',
        compIdx2 : 'Component Index 2',
        compTypePsu : 'PSU',
        compTypeBios : 'BIOS'
        }

    # Dictionary of key (hex string): value (string) pairs that define arguments for
    # Configure Firmware Update Image Type
    configureFwUpdateImageType = {
        imageTypeFwBootloader : 'FW Bootloader / BIOS Primary',
        imageTypeFwImageA : 'FW Image A',
        imageTypeFwImageB : 'FW Image B'
        }

    # Dictionary of key (hex string): value (string) pairs that define arguments for 
    # Configure Firmware Update response Operation Result
    configureFwUpdateOpResults = {
        opResInvalidResValue : 'Invalid Operation Result',
        opResFwImageNotFound : 'Fw Image Not Found',
        opResFwUpdateNotStarted : 'Fw Update Not Started',
        opResFwUpdateInProgress : 'Fw Update In Progress',
        opResFwUpdateCompleted : 'Fw Update Completed',
        opResFwUpdateAborted : 'Fw Update Aborted',
        opResFwImageCorrupted : 'Fw Image Corrupted'
        }

    # Constructor
    # Inputs:
    #   componentType (int): type is either PSU (1) or BIOS (2)
    #   componentIdx (int): Component Index 1 (1) or Component Index 2 (2)
    #   imageType (int): FW Bootloader or BIOS Primary (0), FW Image A (1), FW Image B (2)
    def __init__(self, componentType, componentIdx, imageType, fwFilePath):

        # Initialize variables
        self.componentType = hex(componentType << 4)[2:]
        self.componentIdx = '0' + hex(componentIdx)[2:]
        self.componentByte = hex((componentType << 4) | componentIdx)[2:]
        self.imageType = '0' + hex(imageType)[2:]

        # Verify FW File Exists and is correct length
        # If so, extract file name from filepath
        if not os.path.isfile(fwFilePath):
            UtilLogger.verboseLogger.error(self.cmdName + '.init:' + \
                ' file at local path ' + fwFilePath + \
                ' does not exist. Renaming image as \'\'')
        elif len(os.path.basename(fwFilePath)) > self.fwFileNameLenLimit:
            UtilLogger.verboseLogger.error(self.cmdName + '.init:' + \
                ' file at local path ' + fwFilePath + \
                ' exceeds filename length. Renaming image as \'\'.' + \
                ' Expected Max Length: ' + str(self.fwFileNameLenLimit) + \
                ' Actual Length: ' + str(len(os.path.basename(fwFilePath))))
        # FW File Name is correct length and exists
        # Extract File Name and convert to ASCII bytes
        else:
            self.imageFilePath = fwFilePath
            self.imageFileName = os.path.basename(fwFilePath)
            self.imageFileNameBytes = []
            for fwFileChar in self.imageFileName:
                self.imageFileNameBytes.append("{0:02x}".format(ord(fwFileChar)))
            self.imageFileNameBytes.append('00') # end image name with ASCII NULL ie '\0'

        return

    # Function will update FW using Configure Firmware Update
    # Inputs:
    #   interfaceParams (list of strings): base parameters used to interface with IpmiUtil
    #   fwUpdateTimeLimit (int): time limit to allow FW to update (in seconds)
    #   fwUpdatePollInterval (int): minimum time between each 
    #       Configure Firmware Update (QUERY_FW_UPDATE) request for polling FW update status
    # Outputs:
    #   updatePassOrFail (bool): output determines if FW Update successful (True) or not (False)
    #   fwUpdateDuration (float): output provides duration for FW Update to be completed
    def UpdateFw(self, interfaceParams, fwUpdateTimeLimit, fwUpdatePollInterval):

        # Initialize local variables
        updatePassOrFail = False
        fwUpdateDuration = 0.0

        # Upload FW Image to BMC
        if not self.UploadImage():
            UtilLogger.verboseLogger.error(self.cmdName + '.UpdateFw' + \
                ' Unable to upload image to BMC')
            return updatePassOrFail, fwUpdateDuration

        # Define request bytes
        rawBytesList = [ self.componentByte, self.imageType, \
            self.opStartFwUpdate ]
        for fwFileNameChar in self.imageFileNameBytes:
            rawBytesList.append(fwFileNameChar)

        # Send Configure Firmware Update request (START_FW_UPDATE)
        cmdPassOrFail, respData = SendRawCmd(interfaceParams, \
            self.netFn, self.cmdNum, rawBytesList)
        if cmdPassOrFail and respData[0] == self.opResFwUpdateInProgress:
            UtilLogger.verboseLogger.info(self.cmdName + '.UpdateFw' + \
                ' (START_FW_UPDATE): command passed. PSU FW update in progress.')
        elif cmdPassOrFail and respData[0] != self.opResFwUpdateInProgress:
            UtilLogger.verboseLogger.error(self.cmdName + '.UpdateFw' + \
                ' (START_FW_UPDATE): command failed. Success completion code but ' + \
                ' Operation Results is ' + self.configureFwUpdateOpResults[respData[0]])
        else:
            UtilLogger.verboseLogger.error(self.cmdName + '.UpdateFw' + \
                ' (START_FW_UPDATE): command failed. Completion Code: ' + str(respData))
            return updatePassOrFail, fwUpdateDuration

        # Poll FW Update Status until update is complete
        fwUpdateStartTime = time.time()
        fwUpdateTimeLimit = fwUpdateStartTime + fwUpdateTimeLimit
        while time.time() < fwUpdateTimeLimit:

            # Send Configure Firmware Update request (QUERY_FW_UPDATE)
            cmdPassOrFail, respData = SendRawCmd(interfaceParams, \
                self.netFn, self.cmdNum, \
                [ self.componentByte, self.imageType, self.opQueryFwUpdate ])
            if cmdPassOrFail and respData[0] == self.opResFwUpdateCompleted:
                UtilLogger.verboseLogger.info(self.cmdName + '.UpdateFw' + \
                    ' (QUERY_FW_UPDATE): command passed. FW update completed. ' + \
                    ' Component Type: ' + \
                    self.configureFwUpdateComponent[self.componentType] + '.' + \
                    ' Image Type: ' + \
                    self.configureFwUpdateImageType[self.imageType])
                updatePassOrFail = True
                break
            elif cmdPassOrFail and respData[0] == self.opResFwUpdateInProgress:
                UtilLogger.verboseLogger.info(self.cmdName + '.UpdateFw' + \
                    ' (QUERY_FW_UPDATE): command passed. FW Update in Progress. ' + \
                    ' Component Type: ' + \
                    self.configureFwUpdateComponent[self.componentType] + '.' + \
                    ' Image Type: ' + \
                    self.configureFwUpdateImageType[self.imageType])
            elif cmdPassOrFail:
                if respData[0] not in self.configureFwUpdateOpResults:
                    respData[0] = self.opResInvalidResValue
                UtilLogger.verboseLogger.error(self.cmdName + '.UpdateFw' + \
                    ' (QUERY_FW_UPDATE): command passed.' + \
                    ' But unexpected operation result. Expected Operation Result: ' + \
                    self.configureFwUpdateOpResults[self.opResFwUpdateInProgress] + '.' + \
                    ' Actual Operation Result: ' + \
                    self.configureFwUpdateOpResults[respData[0]] + '.' + \
                    ' Component Type: ' + \
                    self.configureFwUpdateComponent[self.componentType] + '.' + \
                    ' Image Type: ' + \
                    self.configureFwUpdateImageType[self.imageType])
            else:
                UtilLogger.verboseLogger.error(self.cmdName + '.UpdateFw' + \
                    ' (QUERY_FW_UPDATE): command failed. Completion Code: ' + \
                    str(respData[0]) + '.' + \
                    ' Component Type: ' + \
                    self.configureFwUpdateComponent[self.componentType] + '.' + \
                    ' Image Type: ' + \
                    self.configureFwUpdateImageType[self.imageType])
                break

            # Sleep for poll Interval
            UtilLogger.verboseLogger.info(self.cmdName + '.UpdateFw' + \
                ' (QUERY_FW_UPDATE): Polling again in ' + \
                str(fwUpdatePollInterval) + ' seconds.')
            time.sleep(fwUpdatePollInterval)

        # Summarize results
        fwUpdateDuration = datetime.timedelta(seconds=time.time() - fwUpdateStartTime)
        if updatePassOrFail:
            UtilLogger.verboseLogger.info(self.cmdName + '.UpdateFw:' + \
                ' FW Update passed. Component Type: ' + \
                self.configureFwUpdateComponent[self.componentType] + '.' + \
                ' Image Type: ' + \
                self.configureFwUpdateImageType[self.imageType] + '.' + \
                ' Image File Name: ' + self.imageFileName + '.' + \
                ' FW Update Duration: ' + str(fwUpdateDuration))
        else:
            UtilLogger.verboseLogger.info(self.cmdName + '.UpdateFw:' + \
                ' FW Update failed. Component Type: ' + \
                self.configureFwUpdateComponent[self.componentType] + '.' + \
                ' Image Type: ' + \
                self.configureFwUpdateImageType[self.imageType] + '.' + \
                ' Image File Name: ' + self.imageFileName + '.' + \
                ' FW Update Duration: ' + str(fwUpdateDuration))

        return updatePassOrFail, fwUpdateDuration

    def UploadImage(self):

        # Intialize local variables
        uploadPassOrFail = False
        hostFilePath = Config.sftpUploadFilePath + self.imageFileName

        # Verify image file path
        if not self.imageFilePath:
            UtilLogger.verboseLogger.error(self.cmdName + '.UploadImage:' + \
                ' Unable to upload image because file path empty.')
            return uploadPassOrFail, hostFilePath

        # Copy FW Image over to BMC 
        try:
            import Ssh
            if Ssh.sftpPutFile(self.imageFilePath, hostFilePath):
                UtilLogger.verboseLogger.info(self.cmdName + '.UploadImage:' + \
                    ' Successfully Put file ' + \
                    self.imageFileName + ' to ' + Config.sftpUploadFilePath + \
                    ' BMC directory via SFTP.')
                uploadPassOrFail = True
            else:
                UtilLogger.verboseLogger.info(self.cmdName + '.UploadImage:' + \
                    ' Unable to Put file ' + \
                    self.imageFileName + ' to ' + Config.sftpUploadFilePath + \
                    ' BMC directory via SFTP.')
        except Exception, e:
            UtilLogger.verboseLogger.error(self.cmdName + '.UploadImage:' + \
                ' Unable to upload file to BMC via SFTP due to exception: ' + \
                str(e))
            uploadPassOrFail = False

        return uploadPassOrFail