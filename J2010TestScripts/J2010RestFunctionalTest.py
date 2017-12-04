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

import os
import Config
import RedFish
import UtilLogger
import base64

# Global variables
fileName = os.path.basename(__file__)
session = None
cmdPassOrFail = True

# Setup Function
def Setup(interfaceParams):    
    return True

# Function will test completion code for Get Device Id
def Execute(interfaceParams):

    # Declare module-scope variables
    global session, cmdPassOrFail

    # Define Test variables
    cmdPassOrFail = False
    response = None
    
    # Define request variables
    port = str(Config.httpRedfishPort)
    headers = {'Content-Type':'application/json'}
    auth = (Config.bmcUser, Config.bmcPassword)
    userPasswd = "%s:%s" %(Config.bmcUser, Config.bmcPassword)
    encoded = "Basic %s" %(base64.b64encode(userPasswd))
    headers.update({"Authorization":encoded})
    host = Config.bmcIpAddress
    
    try:
        getResource = 'redfish/v1/Chassis/System/MainBoard'
        # Send REST API and verify response
        UtilLogger.verboseLogger.info("getResource = " + getResource )
        cmdPassOrFail, response = RedFish.RestApiCall( session, host, getResource, "GET", auth, port, None, headers )
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("J2010RestFunctionalTest.Execute:" + \
                " GET REST API for resource " + getResource + \
                " passed with status code " + str(response.status_code) + \
                " and response text: " + str(response.text))
        else:
            if(response != None ):
                UtilLogger.verboseLogger.error("J2010RestFunctionalTest.Execute:" + " GET REST API for resource " + getResource + " failed with status code " + str(response.status_code) + " and response text: " + str(response.text))
            else:
                UtilLogger.verboseLogger.error("Timeout on GET REST API " + getResource +" call")
    
    except Exception, e:
        UtilLogger.verboseLogger.error( fileName + ": Test failed with exception - " + str(e))
        cmdPassOrFail = False

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams): 
    global cmdPassOrFail
    return cmdPassOrFail
