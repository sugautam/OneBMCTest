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
import UtilLogger
import os
import json
import base64
import time

# Global variables
fileName = os.path.splitext(os.path.basename(__file__))[0]
cmdPassOrFail = True

# Setup Function
def Setup(interfaceParams):
    global filename
    UtilLogger.verboseLogger.info("%s: running Setup fxn" %(fileName))

    return True


# Function will test FRU Read/Write tests
def Execute(interfaceParams):
    global cmdPassOrFail, filename

    cmdPassOrFail = True

    FRU_Fields = ["Id", "Name", "ChassisType", "Manufacturer", "Model", 
                  "SKU", "SerialNumber", "PartNumber", "AssetTag",  "PowerState"]

    try:
        # Read the current FRU values
        (fruPassOrFail, response) = _ReadFRUValues()
        cmdPassOrFail &= fruPassOrFail

        # Print the current FRU values
        if (fruPassOrFail):
            responseJson = response.json()
            for FRU_field in FRU_Fields:
                if FRU_field in responseJson:
                    FRU_value = responseJson[FRU_field]
                    UtilLogger.verboseLogger.info("%s: FRU Field: %s; Current Value: %s" %(fileName, FRU_field, FRU_value))
        else:
            UtilLogger.verboseLogger.info("%s: Error: Can't read FRU fields" %(fileName))
            cmdPassOrFail &= False 

        # Specify which FRU fields to update
        payload = {}
        payload["AssetTag"] = "NewCustomerWritableThingy"

        # Updated the specified FRU fields
        (fruPassOrFail, response) = _WriteFRUValues(payload)
        cmdPassOrFail &= fruPassOrFail
        
        # Get ALL messages for the FRU fields that were updated
        if (fruPassOrFail):
            RedFish.DisplayFRUValues(response, payload)       
            # Verify the FRU field was modified 
            cmdPassOrFail &= RedFish.VerifyFRUValues(response, payload)
        else:
            UtilLogger.verboseLogger.info("%s: Error: Can't write FRU fields" %(fileName))
            cmdPassOrFail = False 
    except Exception, e:
            UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))
            cmdPassOrFail &= False   

    return cmdPassOrFail


# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global cmdPassOrFail, filename
    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))    
    return cmdPassOrFail


def _ReadFRUValues():
    global cmdPassOrFail, filename

    # Define request variables
    port = str(Config.httpRedfishPort)
    headers = {'Content-Type':'application/json'}
    auth = (Config.bmcUser, Config.bmcPassword)
    userPasswd = "%s:%s" %(Config.bmcUser, Config.bmcPassword)
    encoded = "Basic %s" %(base64.b64encode(userPasswd))
    headers.update({"Authorization":encoded})    
    host = Config.bmcIpAddress
    getResource = 'redfish/v1/Chassis/System'
    host = Config.bmcIpAddress

    # Send REST GET request and verify response
    session = None
    try:
        cmdPassOrFail, response = RedFish.RestApiCall(session, host, getResource,  "GET", auth, port, headers )    
        # Send REST GET request
        (cmdPassOrFail, response) = RedFish.GetResourceValues(getResource)
    except Exception, e:
        UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))
        cmdPassOrFail = False           

    return (cmdPassOrFail, response)


def _WriteFRUValues(data):
    global cmdPassOrFail

    # Define Test variables
    port = str(Config.httpRedfishPort)
    headers = {'Content-Type':'application/json'}
    auth = (Config.bmcUser, Config.bmcPassword)
    userPasswd = "%s:%s" %(Config.bmcUser, Config.bmcPassword)
    encoded = "Basic %s" %(base64.b64encode(userPasswd))
    headers.update({"Authorization":encoded})
    host = Config.bmcIpAddress    
    session = None
    
    try:
        # Send REST PATCH request and verify response    
        patchResource = 'redfish/v1/Chassis/System'
        # Send REST PATCH request        
        (cmdPassOrFail, response) = RedFish.RestApiCall(session, host, patchResource, "PATCH", auth, port, data, headers)
        # Send REST GET request 
        patchResource = 'redfish/v1/Chassis/System'
        session = None
        data = None    
        (cmdPassOrFail, response) = RedFish.RestApiCall(session, host, patchResource,  "GET", auth, port, data, headers )
    except Exception, e:
        UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))
        cmdPassOrFail = False   
    
    return(cmdPassOrFail, response)
