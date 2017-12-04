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
import RedFish
import UtilLogger
import Ssh
import os
import json
import XmlParser
import base64

# Global variables
fileName = os.path.splitext(os.path.basename(__file__))[0]
# Initialize global variables
session = None
headers = None
auth = None
testPassOrFail = True

# Setup Function
def Setup(interfaceParams):
    global fileName

    UtilLogger.verboseLogger.info("%s: running Setup fxn" %(fileName))

    # Test Variable
    sensorListFile = Config.J2010sensorListXmlFile
    xmlParserObj = XmlParser.XmlParser(sensorListFile)

    if not xmlParserObj.root:
        UtilLogger.verboseLogger.error("SensorReadingStressTest.py - XmlParser: failed to parse sensor list XML file.")
        return False

    return True


# Function to read Event Log entries 
def Execute(interfaceParams):    
    # Test Variables
    global session, headers, auth, testPassOrFail, fileName

    testPassOrFail = True
    SEL_EntryTypes = []
    logFields = ["Severity", "SensorType", "SensorNumber", "Message"]

    # Read the current Log Entries
    (logPassOrFail, response) = _ReadLogEntries()
    testPassOrFail &= logPassOrFail

    # Save ALL SEL Entry Types
    if (logPassOrFail):
        responseJson = response.json()
        if "members" in responseJson:
            members = responseJson["members"]
            for member in members:
                if "EntryType" in member:
                    entryType = member["EntryType"]
                    if entryType == "SEL":
                        SEL_EntryTypes.append(member)

                # Print the current Log Entries
                if Config.debugEn:
                    for logField in logFields:
                        if logField in member:
                            logValue = member[logField]
                            UtilLogger.verboseLogger.info("%s: Log Field: %s: %s" %(fileName, logField, logValue))

    # Print the current Log Entries
    for selField in SEL_EntryTypes:
        UtilLogger.verboseLogger.info("")
        for logField in logFields:
            if not logField in selField:
                continue
            logValue = selField[logField]
            UtilLogger.verboseLogger.info("%s: SEL Field: %s: %s" %(fileName, logField, logValue))

    # SEL_EntryTypes

    (validatePassOrFail, unexpectedSels ) = _Validate(SEL_EntryTypes)
    testPassOrFail &= validatePassOrFail

    return testPassOrFail


# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global testPassOrFail, fileName
    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))
    
    return testPassOrFail


def _ReadLogEntries():
    global session, headers, auth, testPassOrFail, fileName
# Example Output
#
#    "members": [
#        "Severity": "Information",
#        "Created": "2000:01:01 00:00:18",
#        "@odata.id": "/redfish/v1/Managers/System/0/LogServices/Log1/Entries/341",
#        "@odata.type": "#LogEntry.1.0.2.LogEntry",
#        "Id": "341",
#        "Name": "Log Entry 341",
#        "SensorType": "39",
#        "SensorNumber": "2",
#        "Message": "DISK 02 is installed",
#        "ExpanderIndex": "3"
#    ]


    # Define request variables
    port = str(Config.httpRedfishPort)
    headers = {'Content-Type':'application/json'}
    auth = (Config.bmcUser, Config.bmcPassword)
    userPasswd = "%s:%s" %(Config.bmcUser, Config.bmcPassword)
    encoded = "Basic %s" %(base64.b64encode(userPasswd))
    headers.update({"Authorization":encoded})
    slotId = Config.J2010slotId
    host = Config.bmcIpAddress
    getResource = 'redfish/v1/Managers/System/%s/LogServices/Log/Entries/1' %(slotId)

    # Send REST GET request and verify response
    session = None
    cmdPassOrFail, response = Redfish.RestApiCall( session, host, getResource, "GET", auth, port, None, headers )

    return (cmdPassOrFail, response)


def _Validate(_):
    # Note:  Most of this code was stolen from IpmiUtil.py (VerifySelAgainstXmlList)

    # Test Variable
    sensorListFile = Config.J2010sensorListXmlFile
    xmlParserObj = XmlParser.XmlParser(sensorListFile)
    selPassOrFail = False
    unexpectedSels = None

    if not xmlParserObj.root:
        UtilLogger.verboseLogger.error("SensorReadingStressTest.py - XmlParser: failed to parse sensor list XML file.")
        return False


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
    actualSelList = []  # FIXME
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

    actualSelList = []

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
