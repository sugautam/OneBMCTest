
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

import requests
from requests.auth import HTTPBasicAuth
import time
import os
import sys
import Config
import UtilLogger
import RedFish
import UtilLogger
import base64

# This test will run negative test cases for REST API calls.
# For each REST API it will be called bad URL, anauthorized header, missing authorization
# For POST and PATCH APIs it will be called with the wrong body ( payload )

# Initialize global variables
fileName = os.path.basename(__file__)
session = None
headers = None
auth = None
testPassOrFail = True
failedTestsCounter = 0

negativeTestsLoop = 1
G50URLs = [
                    # Negative test cases
                    # Chassis Collection
                    {'api':'GET',   'url' : 'redfish/v1/Chassis/Systems', 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'PATCH', 'url' : 'redfish/v1/Chassis/system', 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Chassis/System/sensors', 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Chassis/System/thermal', 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Chassis/System/Thermal#/redundancy', 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Chassis/System/power', 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Chassis/Power#/redundancy', 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Chassis/System/PCIeDevice/%s' %(Config.PCIeDeviceID), 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Chassis/System/PCIeDevices/%s/functions/1' %(Config.PCIeDeviceID), 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Chassis/System/PCIeDevices/%s/functions/2' %(Config.PCIeDeviceID), 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    # Managers Collection
                    {'api':'PATCH', 'url' : 'redfish/v1/Managers/system', 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'PATCH', 'url' : 'redfish/v1/Managers/Systems', 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'PATCH', 'url' : 'redfish/v1/Managers/System/MainBoard', 'resp' : 404, 'message' : 'Not found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/Networkprotocol', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/ethernetInterfaces', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/EthernetInterfaces/21', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/serialInterfaces', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/Serialinterfaces/21', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/Logservices', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/Logservices/Log', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/Logservices/Log/Entries', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/LogServices/Log/entries', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/Logservices/log/Entries/1', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
                    {'api':'GET',   'url' : 'redfish/v1/Managers/System/LogServices/Log/Entries/x', 'resp' : 404, 'message' : 'Not Found', 'type' : 'neg' },
#====================================================================================================================================================================================                    
                    # Positive test cases
                    # Chassis Collection                  
                    {'api':'GET', 'url' : 'redfish/v1/Chassis/System', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Chassis/System/Sensors', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Chassis/System/Thermal', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Chassis/System/Thermal#/Redundancy', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Chassis/System/Power/', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Chassis/System/Power#/Redundancy', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Chassis/System/PCIeDevices/%s' %(Config.PCIeDeviceID), 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Chassis/System/PCIeDevices/%s/Functions/1' %(Config.PCIeDeviceID), 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Chassis/System/PCIeDevices/%s/Functions/2' %(Config.PCIeDeviceID), 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    # Managers Collection
                    {'api':'GET', 'url' : 'redfish/v1/Managers/System/NetworkProtocol', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Managers/System/EthernetInterfaces', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Managers/System/EthernetInterfaces/1', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Managers/System/SerialInterfaces', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Managers/System/SerialInterface/1', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Managers/System/LogServices', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Managers/System/LogServices/Log', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Managers/System/LogServices/Log/Entries', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
                    {'api':'GET', 'url' : 'redfish/v1/Managers/System/LogServices/Log/Entries/1', 'resp' : 200, 'message' : 'OK', 'type' : 'pos' },
               ]

# Setup Function
def Setup(interfaceParams): 
    global failedTestsCounter
    failedTestsCounter = 0 
    return True

# Function will run stress test over REST
# for AC Power Cycling BMC
def Execute(interfaceParams):   
    global fileName, session, headers, auth, testPassOrFail
    global negativeTestsLoop, G50URLs, failedTestsCounter

    username = Config.bmcUser 
    password = Config.bmcPassword     

    # Define Test variables
    testPassOrFail = True
    # Define request variables            
    port = str(Config.httpRedfishPort)    
    api = ""
    
    try:
        # GET calls with a bad URLs
        for n in range(negativeTestsLoop): 
            UtilLogger.verboseLogger.info("\t=============== loop = %d ===============" %n )             
            for i in range(len(G50URLs)):                
                UtilLogger.verboseLogger.info("\t=============== test = %d ===============" %i )  
                headers = {'Content-Type':'application/json'}
                auth = (Config.bmcUser, Config.bmcPassword)
                userPasswd = "%s:%s" %(Config.bmcUser, Config.bmcPassword)
                encoded = "Basic %s" %(base64.b64encode(userPasswd))
                headers.update({"Authorization":encoded})    
                host = Config.bmcIpAddress
                api = G50URLs[i]['api']
                url = G50URLs[i]['url']            
                expResp = (int)(G50URLs[i]['resp'])
                expMessage = G50URLs[i]['message']
                # Running negative test cases
                body = None
                if(G50URLs[i]['type'] == 'neg'):
                    if( 'body' in G50URLs[i] ):
                        body = G50URLs[i]['body']

                    cmdPassOrFail, response = RedFish.RestApiCall( session, host, url, api, auth, port, body, headers ) 
                    if response != None:
                        resp = response.status_code
                        message = response.reason
                        UtilLogger.verboseLogger.info("Received:\nurl: %s\n resp = %d, \n message = %s" %(url,resp,message))
                    
                        if( resp != expResp and message != expMessage):
                            UtilLogger.verboseLogger.error("failed:\nExpected: \turl: %s\n resp = %d, \n message = %s" %( url, expResp, expMessage) )
                            failedTestsCounter += 1
                            testPassOrFail = False
                    
                        # appending now random strings to the end of the URLs
                        # if there is a 'body' key then we don't need to append a long string, we just want to see the "Bad Request" with the wrong body call
                        if( 'body' not in G50URLs[i] ):
                            rand_str = RedFish.GetRandString()
                            url = url + rand_str
                            cmdPassOrFail, response = RedFish.RestApiCall( session, host, url, api, auth, port, None, headers )               
                            resp = response.status_code
                            message = response.reason
                            UtilLogger.verboseLogger.info("Received:\nurl: %s\n resp = %d, \n message = %s" %(url,resp,message))
                        
                            if( resp != expResp and message != expMessage):
                                UtilLogger.verboseLogger.error("failed:\nExpected: \turl: %s\n resp = %d, \n message = %s" %( url, expResp, expMessage) )
                                failedTestsCounter += 1
                                testPassOrFail = False
                    else:
                        UtilLogger.verboseLogger.error("Negative test case failed on REST API call to %s. cmdPassOrFail = %s, response = %s" %(url, cmdPassOrFail, response) )
                        testPassOrFail = False
                        
                # Running positive test cases to see if Redfish is alive after responding to the negative API calls
                auth = (Config.bmcUser, Config.bmcPassword)
                userPasswd = "%s:%s" %(Config.bmcUser, Config.bmcPassword)
                encoded = "Basic %s" %(base64.b64encode(userPasswd))
                headers.update({"Authorization":encoded})
                body = None
                if(G50URLs[i]['type'] == 'pos'):
                    if( 'body' in G50URLs[i] ):
                        body = G50URLs[i]['body']
                    cmdPassOrFail, response = RedFish.RestApiCall( session, host, url, api, auth, port, body, headers )
                    if cmdPassOrFail:
                        if response:
                            resp = response.status_code
                            message = response.reason
                            UtilLogger.verboseLogger.info("Received:\nurl: %s\n resp = %d, \n message = %s" %(url,resp,message))
                            if( resp != expResp and message != expMessage):
                                UtilLogger.verboseLogger.error("failed:\nExpected: \turl: %s\n resp = %d, \n message = %s" %( url, expResp, expMessage) )
                                failedTestsCounter += 1
                                testPassOrFail = False
                            # Checking now API calls for unauthorized users
                            auth = ("", "")
                            headers["Authorization"] = ""
                            cmdPassOrFail, response = RedFish.RestApiCall( session, host, url, api, auth, port, body, headers )               
                            resp = response.status_code
                            message = response.reason
                            expResp = 401
                            expMessage = "Unauthorized"
                            UtilLogger.verboseLogger.info("Received:\nurl: %s\n resp = %d, \n message = %s" %(url,resp,message))
                            if( resp != 401 and message != "Unauthorized" ):
                                UtilLogger.verboseLogger.error("failed:\nExpected: \turl: %s\n resp = %d, \n message = %s" %( url, expResp, expMessage) )
                                failedTestsCounter += 1
                                testPassOrFail = False
                        else:
                            UtilLogger.verboseLogger.error("Failed on REST API call to %s" %(url) )
                            testPassOrFail = False
                    else:
                        UtilLogger.verboseLogger.error("Positive test case failed  on REST API call to %s. cmdPassOrFail = %s, response = %s" %(url, cmdPassOrFail, response) )
                        testPassOrFail = False

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        UtilLogger.verboseLogger.error( fileName + ": Test failed with exception - " + str(e) )
        UtilLogger.verboseLogger.error( "\nException type: %s \nLine number: %s" %(exc_type, exc_tb.tb_lineno) )
        testPassOrFail = False

    return testPassOrFail

def Cleanup(interfaceParams): 
    global fileName, testPassOrFail, failedTestsCounter 
    UtilLogger.verboseLogger.info("%s: Total failed tests are %d out of %d" %(fileName,failedTestsCounter,len(G50URLs)))
    return testPassOrFail
