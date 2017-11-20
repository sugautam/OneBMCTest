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

import os
import time
import re
import inspect
import Config
import RedFish
import UtilLogger
import Helper
import FwFlash
import Ssh
import json

# Global variables
fileName = os.path.splitext(os.path.basename(__file__))[0]
session = None
headers = None
auth = None
bmcPrevBinFile = None           # Previous version of the FW
bmcNextBinFile = None           # Latest version of the FW
testPassOrFail = True

# Setup Function
def Setup(interfaceParams):
    global fileName, bmcPrevBinFile, bmcNextBinFile, auth
    
    bmcPrevBinFile = Config.bmcPrevBinFilePath
    bmcNextBinFile = Config.bmcNextBinFilePath
    username = Config.bmcUser
    password = Config.bmcPassword
    auth = (Config.bmcUser, Config.bmcPassword)
    port = str(Config.httpRedfishPort)

    UtilLogger.verboseLogger.info("%s: running Setup fxn" %(fileName))

    # Get the name of the Previous image
    bmcPrevBinFile = _GetFirmwareImageName(bmcPrevBinFile )
    UtilLogger.verboseLogger.info( "Old firmware image is %s" %(bmcPrevBinFile) )
    if (not bmcPrevBinFile):
        return False

    # Get the name of the Latest image
    bmcNextBinFile = _GetFirmwareImageName(bmcNextBinFile)
    UtilLogger.verboseLogger.info( "New firmware image is %s" %(bmcNextBinFile) )
    if (not bmcNextBinFile):
        return False

    return True

# Function will update the FW
def Execute(interfaceParams):
    global bmcPrevBinFile, bmcNextBinFile, fileName, session, headers, auth, testPassOrFail

    username = Config.bmcUser
    password = Config.bmcPassword
    auth = (Config.bmcUser, Config.bmcPassword)
    port = str(Config.httpRedfishPort)    
    # Steps to be performed:
    #  - Execute Redfish FW Update command to update to previous version
    #  - Execute Redfish FW Update command to update to current version
    #  - Compare previous and current versions to comfirm update worked
    #  - Update to current version (compare: expect version to be same as version from previous update)
    #  - Update to previous version (compare: expect version to be older than version from previous update)
    #  - Update to previous version (compare: expect version to be same as version from previous update)
    #  - Cleanup: Update to current 

    # Define Test variables
    testPassOrFail = True
    
    # Get existing FW Version
    timeout = 10

    try:
        (execPassOrFail, _) =  RedFish.GetFirmwareVersion(auth, port, timeout)
        testPassOrFail &= execPassOrFail

        if(execPassOrFail):
            UtilLogger.verboseLogger.info("%s: \t1: GetFirmwareVersion passed" %(fileName))
        else:
            UtilLogger.verboseLogger.info("%s: \t1: GetFirmwareVersion failed" %(fileName))

        # V1: Update the Firmware to the previous version
        (execPassOrFail, previous_version) = RedFish.UpdateFW(bmcPrevBinFile, auth, port, username, password)
        testPassOrFail &= execPassOrFail
    
        if(execPassOrFail):
            UtilLogger.verboseLogger.info("%s: \t2: UpdateFW bmcPrevBinFile passed. \n\tFirmware updated to the versions of %s" %(fileName, previous_version))
        else:
            UtilLogger.verboseLogger.info("%s: \t2: UpdateFW bmcPrevBinFile failed" %(fileName))
            testPassOrFail = False
            return testPassOrFail

        # V2: Update the Firmware to the next version
        (execPassOrFail, current_version) = RedFish.UpdateFW(bmcNextBinFile, auth, port, username, password)
        testPassOrFail &= execPassOrFail

        if(execPassOrFail):
            UtilLogger.verboseLogger.info("%s: \t3: UpdateFW bmcNextBinFile passed. \n\tFirmware updated to the versions of %s" %(fileName, current_version))
        else:
            UtilLogger.verboseLogger.info("%s: \t3: UpdateFW bmcNextBinFile failed" %(fileName))
            testPassOrFail = False
            return testPassOrFail

        # Compare version's (V1 to V2).  Expect current (next) version (V2) to be newer than previous version (V1)
        # expectedCompare:
        #       1: first input is newer (greater) than second input
        #       0: first and second input are equal
        #      -1: first input is older (less) than second input
        execPassOrFail = _compareFWVersions(current_version, previous_version, 1)
        testPassOrFail &= execPassOrFail

        if(execPassOrFail):
            UtilLogger.verboseLogger.info("%s: \t4: compareFWVersions passed" %(fileName))
        else:
            UtilLogger.verboseLogger.info("%s: \t4: compareFWVersions failed" %(fileName))

        # V3: Update the Firmware to the next version (again)(should already be at next version)  
        previous_version = current_version  
        (execPassOrFail, current_version) = RedFish.UpdateFW(bmcNextBinFile, auth, port, username, password)
        testPassOrFail &= execPassOrFail

        if(execPassOrFail):
            UtilLogger.verboseLogger.info("%s: \t5: UpdateFW bmcNextBinFile passed. \n\tFirmware updated to the versions of %s" %(fileName, current_version))
        else:
            UtilLogger.verboseLogger.info("%s: \t5: UpdateFW bmcNextBinFile failed" %(fileName))
            testPassOrFail = False
            return testPassOrFail

        # Compare version's (V2 to V3).  Expect current (next) version (V3) to be the same from previous update (V2)
        if( previous_version != current_version ):
            UtilLogger.verboseLogger.info("%s: \t5: failed. Expected to be the same from previous update" %(fileName))
            testPassOrFail = False
            return testPassOrFail

        execPassOrFail = _compareFWVersions(current_version, current_version, 0)
        testPassOrFail &= execPassOrFail

        if(execPassOrFail):
            UtilLogger.verboseLogger.info("%s: \t6: compareFWVersions passed" %(fileName))
        else:
            UtilLogger.verboseLogger.info("%s: \t6: compareFWVersions failed" %(fileName))

        # V4: Update the Firmware to the previous version
        (execPassOrFail, previous_version) = RedFish.UpdateFW(bmcPrevBinFile, auth, port, username, password)
        testPassOrFail &= execPassOrFail

        if(execPassOrFail):
            UtilLogger.verboseLogger.info("%s: \t7: UpdateFW bmcPrevBinFile passed" %(fileName))
        else:
            UtilLogger.verboseLogger.info("%s: \t7: UpdateFW bmcPrevBinFile failed" %(fileName))
            testPassOrFail = False
            return testPassOrFail

        # Compare version's (V3 to V4).  Expect current version (V4) to be older than previous version (V3)
        execPassOrFail = _compareFWVersions(current_version, previous_version, 1)
        testPassOrFail &= execPassOrFail

        if(execPassOrFail):
            UtilLogger.verboseLogger.info("%s: \t8: compareFWVersions passed" %(fileName))
        else:
            UtilLogger.verboseLogger.info("%s: \t8: compareFWVersions failed" %(fileName))

        # V5: Update the Firmware to the previous version (again)
        (execPassOrFail, current_version) = RedFish.UpdateFW(bmcPrevBinFile, auth, port, username, password)
        testPassOrFail &= execPassOrFail

        if(execPassOrFail):
            UtilLogger.verboseLogger.info("%s: \t9: UpdateFW bmcPrevBinFile passed" %(fileName))
        else:
            UtilLogger.verboseLogger.info("%s: \t9: UpdateFW bmcPrevBinFile failed" %(fileName))
            testPassOrFail = False
            return testPassOrFail

        # Compare version's (V4 to V5).  Expect current (prev) version (V5) to be the same from previous update (V4)
        execPassOrFail = _compareFWVersions(current_version, previous_version, 0)
        testPassOrFail &= execPassOrFail

        if(execPassOrFail):
            UtilLogger.verboseLogger.info("%s: \t10: compareFWVersions passed" %(fileName))
        else:
            UtilLogger.verboseLogger.info("%s: \t10: compareFWVersions failed" %(fileName))

    except Exception, e:
            UtilLogger.verboseLogger.error( fileName + ": Test failed with exception - " + str(e))
            testPassOrFail = False

    return testPassOrFail


# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global testPassOrFail, fileName, bmcNextBinFile, auth
    
    username = Config.bmcUser
    password = Config.bmcPassword
    auth = (Config.bmcUser, Config.bmcPassword)
    port = str(Config.httpRedfishPort)

    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))

    # Restore the image to the latest version
    if (bmcNextBinFile):
        (testPassOrFail, latest_version) = RedFish.UpdateFW(bmcNextBinFile, auth, port, username, password)
        if (testPassOrFail):
            UtilLogger.verboseLogger.info("%s.Cleanup: FW Restored to latest version %s: which should be %s" %(fileName, latest_version, bmcNextBinFile))
    
    return testPassOrFail

# Compare the FW Versions to determine if the update was successful
def _compareFWVersions(version1, version2, expectedCompare):

    if (not version1 or not version2):
        UtilLogger.verboseLogger.error("%s.compare: Version Argument(s) are None" %(fileName))
        return (False)

    #  Version Format: v0.11.00
    regexPattern = "v(\d{1,2}).(\d{2}).(\d{2})"
    comparePassOrFail = True

    # Split the version into major/minor components
    regexCompile = re.compile(regexPattern)

    m = regexCompile.match(version1)
    if (m and len(m.groups()) == 3):
        major1 = m.group(1)
        minor1 = m.group(2)
        aux1 = m.group(3)
    else:
        UtilLogger.verboseLogger.error("%s.compare: Unexpected version format: %s" %(fileName, version1))
        return (False)

    m = regexCompile.match(version2)
    if (m and len(m.groups()) == 3):
        major2 = m.group(1)
        minor2 = m.group(2)
        aux2 = m.group(3)
    else:
        UtilLogger.verboseLogger.error("%s.compare: Unexpected version format: %s" %(fileName, version2))
        return (False)

    # Compare the 2 versions
    compareOut = FwFlash.CompareBmcFwVersion(major1, minor1, aux1, major2, minor2, aux2)
    # compareOut:
    #   1: first input is newer (greater) than second input
    #   0: first and second input are equal
    #  -1: first input is older (less) than second input

    if (compareOut == -1):
        UtilLogger.verboseLogger.info("%s.compare: Version %s is OLDER than Version %s" %(fileName, version1, version2))
        if (not expectedCompare == compareOut):
            comparePassOrFail = False
            UtilLogger.verboseLogger.error("%s.compare: Expected version %s to be OLDER or the SAME as Version %s" %(fileName, version1, version2))
    elif (compareOut == 0):
        UtilLogger.verboseLogger.info("%s.compare: Version %s is EQUAL to Version %s" %(fileName, version1, version2))
        if (not expectedCompare == compareOut):
            comparePassOrFail = False
            UtilLogger.verboseLogger.error("%s.compare: Expected version %s to be OLDER or NEWER than Version %s" %(fileName, version1, version2))
    else:
        UtilLogger.verboseLogger.info("%s.compare: Version %s is NEWER than Version %s" %(fileName, version1, version2))
        if (not expectedCompare == compareOut):
            comparePassOrFail = False
            UtilLogger.verboseLogger.error("%s.compare: Expected version %s to be NEWER or the SAME as Version %s" %(fileName, version1, version2))

    return (comparePassOrFail)


def _GetFirmwareImageName(bmcBinFilePath):
    """ Locate the Binary fileName from the indicated directory """

    try:
        bmcBinFile = os.listdir(bmcBinFilePath)
    except Exception as e:
        bmcBinFile = []
    if not len(bmcBinFile):
        UtilLogger.verboseLogger.error("%s.Execute: No binary image found in %s" %(fileName, bmcBinFilePath))
        return (False)

    # Use the FIRST filename found (should only be one image in the directory)
    for file in bmcBinFile:
        if file[0] == '.':     # Ignore hidden files
            continue
        bmcBinFile = os.path.join(bmcBinFilePath, file)
        break

    return  (bmcBinFile)

