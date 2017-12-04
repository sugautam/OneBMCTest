"""
PyTestUtil

Copyright (c) Microsoft Corporation

All rights reserved.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the ""Software""),
to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import os
import Config
import RedFish
import UtilLogger
import Ssh
import inspect
import re
from Helpers.Connection import Connection

# Global variables
fileName = os.path.basename(__file__)

# Setup Function
def Setup(interfaceParams):
    return True

# Function will test Expander FW recovery using G3XFlash and check CPU utilization during update
def Execute(interfaceParams):

    ExpanderBinFile = Config.expanderBinFilePath
    connection = Connection()
    testPassOrFail = True

    try:
        expandFilePath = _GetFirmwareImageName(ExpanderBinFile)
        if not expandFilePath:
            return False

        for seId in Config.J2010allSeIDs:
            UtilLogger.verboseLogger.info("================Expander %s================" %(seId))
            # Update the Firmware
            execPassOrFail = UpdateFWwithMonitorCPU(expandFilePath, connection.auth, connection.port, connection.auth[0], connection.auth[1], seId)
            if execPassOrFail:
                UtilLogger.verboseLogger.info("%s: Expander %s update success!" %(fileName, seId))
                execCmds = ['\n']
                execCmds.append("cat /var/wcs/home/CPU.txt\n")
                execPassOrFail, sshOutputs, parsedCmdOutputs = Ssh.sshExecuteCommand( execCmds, username=connection.auth[0], password=connection.auth[1])
                # Check CPU utilization
                if execPassOrFail:
                    # CPU utilization matches 70%-199%
                    regexPattern = r"([7-9]\d|1\d{2})%"
                    regex = re.compile(regexPattern)
                    matches = regex.findall(sshOutputs[-1])
                    if not matches:
                        UtilLogger.verboseLogger.info("%s: CPU utilization passed!" %(fileName))
                    else:
                        maxCPU = max(matches)
                        UtilLogger.verboseLogger.error("%s: failed: CPU utilization goes pass 70 percent. CPU utilization up to %s percent." %(fileName, maxCPU))
                        testPassOrFail = False
                else:
                    UtilLogger.verboseLogger.error("%s: failed to monitor CPU utilization during update." %(fileName))
                    testPassOrFail = False
            else:
                UtilLogger.verboseLogger.info("%s: Expander #%s update failed!" %(fileName, seId))
                testPassOrFail = False
                continue

    except Exception, e:
            UtilLogger.verboseLogger.error( fileName + ": Test failed with exception - " + str(e))
            testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    return True

def UpdateFWwithMonitorCPU( expBinFile, auth, port, username, password, expId, times = 350, interval = 2 ):
    global  filename
    cmdPassOrFail = True
    execPassOrFail = True
    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("%s: running %s fxn.  Fw: %s" %(fileName, funcName, expBinFile))

    execPassOrFail = CheckExpanderFirmware(auth, port, expId)
    if not execPassOrFail:
        return False

    # Push expander's image to BMC
    execPassOrFail = RedFish.PushImage(expBinFile, Config.expanderFlashFilePath, username, password)
    if execPassOrFail:
        UtilLogger.verboseLogger.info("%s: \t2: PushImage passed" %(fileName))
    else:
        UtilLogger.verboseLogger.info("%s: \t2: PushImage failed" %(fileName))
        return False

    sshCmd = "rm -f /var/wcs/home/CPU.txt;"
    sshCmd += "$(top -b -n %d -d %d| grep CPU | awk '/CPU:\s/{print $2}' > /var/wcs/home/CPU.txt &)\n " %(times, interval)
    execCmds = ['\n']
    execCmds.append(sshCmd)

    resource = "redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate"
    postResource = 'file://image-expander.fw?component=expander%s' %(expId)
    payload = {'ImageURI':postResource, 'TransferProtocol': 'OEM' }
    execPassOrFail, response = RedFish.SendRestRequest(resource, auth, port, payload, restRequestMethod="POST", timeout = 5)   
    cmdPassOrFail &= execPassOrFail
    UtilLogger.verboseLogger.info("RestApiCall call: " + resource + \
    "Response Status Code: " + str(response.status_code) + " " + \
    "Response Content: " + str(response.text))

    if execPassOrFail:
        UtilLogger.verboseLogger.info("%s: \t3: SimpleUpdate POST call passed" %(fileName))
    else:
        UtilLogger.verboseLogger.info("%s: \t3: SimpleUpdate POST call failed" %(fileName))
        return False

    # Check CPU utilization and wait for the FirmwareUpdate command to complete
    execPassOrFail, sshOutputs, parsedCmdOutputs = Ssh.sshExecuteCommand( execCmds, username=username, password=password, timeSleep = 700)
    if execPassOrFail:
        UtilLogger.verboseLogger.info("%s: \t2: Ssh commands execution passed" %(fileName))
    else:
        UtilLogger.verboseLogger.info("%s: \t2: Ssh commands execution failed" %(fileName))
        return False

    execPassOrFail = CheckExpanderFirmware(auth, port, expId)
    if not execPassOrFail:
        cmdPassOrFail = False

    return cmdPassOrFail

def _GetFirmwareImageName(expBinFilePath):
    try:
        expBinFile = os.listdir(expBinFilePath)
    except Exception as e:
        expBinFile = []
    if not len(expBinFile):
        UtilLogger.verboseLogger.error("%s.Execute: No binary image found in %s" %(fileName, expBinFilePath))
        return False

    # Use the FIRST filename found (should only be one image in the directory)
    for file in expBinFile:
        if file[0] == '.':     # Ignore hidden files
            continue
        expBinFile = os.path.join(expBinFilePath, file)
        break
    return expBinFile

# Get the Version of the existing Firmware
def _GetFirmwareVersion(auth, port, timeout = 180, exId = 1):
    global fileName

    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("%s: running %s fxn" %(fileName, funcName))

    # Define Test variables
    fmVersion = None
    getResource = 'redfish/v1/Chassis/System/StorageEnclosure/{:d}/Storage'.format(exId)

    # Get the Firmware Version using Redfish
    cmdPassOrFail, response = RedFish.SendRestRequest(getResource, auth, port, data = None, restRequestMethod = "GET", timeout = timeout)

    if cmdPassOrFail:
        responseJSON = response.json()
        if "StorageController" in responseJSON:
            fmVersion = responseJSON["StorageController"]["FirmwareVersion"]
            UtilLogger.verboseLogger.info("%s.version: Current Firmware Version: %s" %(fileName, fmVersion))
        else:
            UtilLogger.verboseLogger.error("%s.version: did NOT find Firmware Version" %(fileName))

    return cmdPassOrFail, fmVersion

def CheckExpanderFirmware(auth, port, expId):
    execPassOrFail, version = _GetFirmwareVersion(auth, port, exId=expId)
    if(execPassOrFail and (version != 'N/A')):
        UtilLogger.verboseLogger.info("%s: \t1: GetFirmwareVersion passed" %(fileName))
    else:
        if version == 'N/A':
            UtilLogger.verboseLogger.error("%s: \t1: Expander #%s: nonexistent or update failed." %(fileName, expId))
        else:
            UtilLogger.verboseLogger.info("%s: \t1: GetFirmwareVersion failed." %(fileName))
        execPassOrFail = False
    return execPassOrFail