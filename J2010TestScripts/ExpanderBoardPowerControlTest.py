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

import Config
import RedFish
import Ssh
import UtilLogger
import os
import time
import json

# Global variables
# Initialize global variables
session = None
headers = None
auth = None
testPassOrFail = True

fileName = os.path.splitext(os.path.basename(__file__))[0]

# Setup Function
def Setup(interfaceParams):
    global fileName


    UtilLogger.verboseLogger.info("%s: running Setup fxn" %(fileName))

    return True


# Function will test the Power On/Off sequence for the Expander Board
def Execute(interfaceParams):
    global fileName, session, headers, auth, testPassOrFail
    
    username = Config.bmcUser
    password = Config.bmcPassword

    testPassOrFail = True
    execCmds = ['\r']                       # 
    execCmds.append('\rhelp\r')             # Help command
    execCmdsResponse = "CLI Help"
    sshPort = None

    try:

        FRU_Fields = ["Id", "Name", "ChassisType", "Manufacturer", "Model", "SKU", "IndicatorLED",  "PowerState"]

        # Read the current FRU values        
        (fruPassOrFail, response) = _GetStorageEnclosureValues()
        testPassOrFail &= fruPassOrFail               
        responseJson = response.json()                         
        

        # Print the current FRU values
        if (fruPassOrFail):
            for FRU_field in FRU_Fields:
                if FRU_field in responseJson:
                    FRU_value = responseJson[FRU_field]
                    UtilLogger.verboseLogger.info("%s: FRU Field: %s; Current Value: %s" %(fileName, FRU_field, FRU_value))
        else:
            UtilLogger.verboseLogger.info("%s: test failed with error code %d" %(fileName, response.status_code))
                
        # Specify Expander Board to Power Off
        payload = {}
        payload["ResetType"] = "ForceOff"

        # Update the specified Storage Enclosure fields
        (fruPassOrFail, response) = _PatchStorageEnclosureValues(payload)
        testPassOrFail &= fruPassOrFail

        # Get ALL messages for the FRU fields that were updated
        if (fruPassOrFail):
            RedFish.DisplayFRUValues(response, payload)

        # Verify the FRU fields
        testPassOrFail &= RedFish.VerifyFRUValues(response, payload)

        # Specify Expander Board to Power On
        payload = {}
        payload["ResetType"] = "ForceOn"

        # Update the specified Storage Enclosure field
        (fruPassOrFail, response) = _PatchStorageEnclosureValues(payload)
        testPassOrFail &= fruPassOrFail

        # Get ALL messages for the FRU fields that were updated
        if (fruPassOrFail):
            RedFish.DisplayFRUValues(response, payload)

        # Verify the FRU fields 
        testPassOrFail &= RedFish.VerifyFRUValues(response, payload)

        # Sleep for 5 seconds
        UtilLogger.verboseLogger.info("%s: sleeping for 5 seconds.." %(fileName))
        
        sshPort = Config.J2010sshPorts[Config.J2010seId]
        UtilLogger.verboseLogger.info("SSH executing commands %s with username %s and password %s" %( execCmds, username, password ))
        (execPassOrFail, sshOutputs, parsedCmdOutputs) = Ssh.sshExecuteCommand( execCmds, username, password, sshPort )

        # Verify Expander is powered ON by checking console redirection
        UtilLogger.verboseLogger.info("%s: running Expander Console Redirection validation for Port %s" %(fileName, Config.sshPort))

        if (execPassOrFail):
            for sshOutput in sshOutputs:
                if execCmdsResponse in sshOutput:
                    UtilLogger.verboseLogger.info("%s: successfully found '%s' in response" %(fileName, execCmdsResponse))
                    testPassOrFail = True
        else:
           UtilLogger.verboseLogger.info("%s: test failed with error code %d" %(fileName, response.status_code))
        
        if (not execPassOrFail):
            UtilLogger.verboseLogger.error("%s: failed to find '%s' in response" %(fileName, execCmdsResponse))

    except Exception, e:
        UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))
        testPassOrFail = False   

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global fileName

    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))    
    return True


def _GetStorageEnclosureValues():    
    seId = Config.J2010seId        
    getResource = 'redfish/v1/Chassis/System/StorageEnclosure/%s' %(seId)
    # Send REST GET request
    (testPassOrFail, response) = RedFish.GetResourceValues(getResource)

    return(testPassOrFail, response)

def _PatchStorageEnclosureValues(data):
    # Define Test variables    
    seId = Config.J2010seId
    postResource = 'redfish/v1/Chassis/System/StorageEnclosure/%s/Actions/Chassis.Reset' %(seId)

    # Send REST Post request    
    (testPassOrFail, response) = RedFish.PostResourceValues( postResource, data )

    return(testPassOrFail, response)


