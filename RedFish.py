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
import inspect
import os
import requests
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib3.exceptions import InsecureRequestWarning
import Ssh
import Config
import Helper
import UtilLogger
import base64
import json
import random
from random import choice
from string import ascii_uppercase
from string import ascii_lowercase
from string import digits
from J2010TestScripts import ConfigJ2010
from Helpers import PSU_Details
from Helpers.Connection import Connection

# Global Variables
fileName = os.path.splitext(os.path.basename(__file__))[0]

# Function will send HTTP GET/POST/PATCH request to BMC using the specified arguments
#
# Inputs:
#   session (object):   REST session#                      
#   hostname (string):  name of host or IP address
#   resource (string):  resource to GET/POST/PATCH information for
#
# Returns: 
#   sendPassOrFail (bool): command success (200 status code) or failure
#   response (object): http response
#       response object includes:
#           response.status_code (int): response status code
#           response.text (unicode): response content   
def RestApiCall(session, hostname, resource, restRequestMethod=None, auth=None, port=None, payload=None, headers=None, restAPITimeout = 180):

    sendPassOrFail = False
    response = None
    
    if not restRequestMethod:
        restRequestMethod = "GET"

    # Use "requests" class if "session" class not initialized (using J210Login)
    if not session:
        session = requests

    try:
        # Determine http vs https
        request = ''
        if Config.BmcSslEn:
            request = 'https://'
        else:
            request = 'http://'
    
        # Suppress ALL Warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        #requests.packages.urllib3.disable_warnings()

        # Generate Request URI
        request += hostname
        if port:
            request += ':' + str(port)
        request += '/'
        request += resource

        # Send HTTP GET/POST/PATCH Request to BMC and get response
        if payload:        # POST/PATCH Request
            if restRequestMethod == "PATCH":
                body = json.dumps(payload)
                response = session.patch(request, data=body, headers=headers, auth=auth, json=None, verify=Config.BmcVerifyCert)
            else:   
                body = json.dumps(payload)
                response = session.post(request, data=body, headers=headers, auth=auth, json=None, verify=Config.BmcVerifyCert)
        else:           # GET Request
            restRequestMethod = "GET"
            response = session.get(request, auth=auth, headers=headers, verify=Config.BmcVerifyCert, timeout=restAPITimeout )

        if response.status_code != 200:
            UtilLogger.verboseLogger.error("RestApiCall: HTTP " + restRequestMethod + " Request " + \
                request + " failed. Error status " + str(response.status_code) + \
                ". Error message: " + str(response.text))
            sendPassOrFail = False
        else:
            sendPassOrFail = True

        if Config.debugEn:
            UtilLogger.verboseLogger.info(": " + \
                "HTTP " + restRequestMethod + " Request URL: " + request + " " + \
                "Response Status Code: " + str(response.status_code) + " " + \
                "Response Content: " + str(response.text))

    except Exception, e:
        UtilLogger.verboseLogger.error("RestApiCall: exception failure - " + \
            str(e))
        sendPassOrFail = False

    return sendPassOrFail, response


# Function will SSH to BMC and check if the redfish
# server is running and has an active listening port
def CheckForRunningRedfishServer(username=Config.bmcUser, password=Config.bmcPassword, timeout = Config.sshRedfishResponseLimit):

    # Define test variables
    cmdPassOrFail = False
    totalWaitTime = time.time() + timeout
    funcName = inspect.stack()[0][3]
    auth = (username, password)
    port = Config.httpRedfishPort
    getResource = "redfish/v1/Chassis"
    
    UtilLogger.verboseLogger.info("%s: Waiting for Redfish server..." %(funcName))

    # Wait for Redfish server to be started
    while (time.time() < totalWaitTime) and not cmdPassOrFail:

        # Issue Redfish HTTP command
        session = None
        (execPassOrFail, response) = RestApiCall( session, Config.bmcIpAddress, getResource, "GET", auth, port )
 
        if (execPassOrFail):
            UtilLogger.verboseLogger.info("%s: Redfish Server is Running"
                                              %(funcName))
            cmdPassOrFail = True
        else:
            # Wait and try again....
            time.sleep(Config.acPowerOffSleepInSeconds)

    if (not cmdPassOrFail):
        UtilLogger.verboseLogger.error("%s: Redfish server failed to start" %(funcName))

    return(cmdPassOrFail)


def is_psu_ready(current_psu):
    """
    Checking to see if the PSU is ready for an update of the FW in case it was still in the middle of an update. This
    is here because we may want to try to update while an update is already happening. This allows us a way to make sure
    that we don't step on one in case we don't want to overlap updates.
    :param current_psu: The PSU object
    :param psu: The PSU number. Either a 1 or 2
    :return: True or False depending on if the PSU is ready or not
    """

    if current_psu.state == "Updating":
        UtilLogger.verboseLogger.error("Failed: The PSU is not ready to be updated. Current PSU state is '{}'"
                                       .format(current_psu.state))
        return False
    return True


# Update PSU firmware
def initiate_fw_update(connection, payload, psu):
    """
    Initiates the FW update for either the PSU or RFU
    :param connection: The connection object for the API call
    :param payload: The initiation URL needed for the respective device that you're updating. It's different for the
    FRU and the PSU.
    :param psu: This is needed for the re-initialization of the PSU object to check current state
    :return: True or False depending on if the initiation of the update appears to be successful
    """

    exec_pass_or_fail = True

    # Execute image flash
    exec_pass_or_fail, response = SendRestRequest(ConfigJ2010.FW_RESOURCE_URL, connection.auth, connection.port,
                                                  payload, restRequestMethod="POST", timeout=5)

    if exec_pass_or_fail:
        UtilLogger.verboseLogger.info("Image was successfully initiated")
    else:
        UtilLogger.verboseLogger.error("Failed: Image was not successfully initiated")
        return False

    # Get the current state of the PSU
    current_psu = PSU_Details.PSU(psu)

    # Watch for it to change state to 'Updating'
    timeout = time.time() + 10
    while time.time() < timeout and current_psu.state != "Updating":
        current_psu = PSU_Details.PSU(psu)  # Re-initialized the object with the current values

    if current_psu.state != "Updating":
        UtilLogger.verboseLogger.error("Failed: The PSU didn't start the update process in a timely manner.")
        return False

    return True


# Update the firmware
def UpdateFW( bmcBinFile, auth, port, username, password, partition):
    global  filename

    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("%s: running %s fxn.  Fw: %s" %(fileName, funcName, bmcBinFile))

    # Define Test variables
    cmdPassOrFail = True
    execPassOrFail = True

    (execPassOrFail, version) =  GetFirmwareVersion(auth, port)
    cmdPassOrFail &= execPassOrFail

    if(execPassOrFail):
        UtilLogger.verboseLogger.info("%s: \t1: GetFirmwareVersion passed" %(fileName))
    else:
        UtilLogger.verboseLogger.info("%s: \t1: GetFirmwareVersion failed" %(fileName))

    # Push image to BMC
    execPassOrFail = PushImage(bmcBinFile, Config.bmcFlashFilePath1, username, password)
    cmdPassOrFail &= execPassOrFail

    if(execPassOrFail):
        UtilLogger.verboseLogger.info("%s: \t2: PushImage passed" %(fileName))
    else:
        UtilLogger.verboseLogger.info("%s: \t2: PushImage failed" %(fileName))
        cmdPassOrFail = False
        return (cmdPassOrFail, version)
    
    host = Config.bmcIpAddress
    resource = "redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate"        
    payload = {'ImageURI':'file://{}?component=bmc&partition={}'.format(bmcBinFile, partition), 'TransferProtocol':'OEM' }
    # Wait for the FirmwareUpdate command to complete
    execPassOrFail, response = SendRestRequest(resource, auth, port, payload, restRequestMethod="POST", timeout = 5)
    cmdPassOrFail &= execPassOrFail

    UtilLogger.verboseLogger.info("RestApiCall call: " + resource + \
    "Response Status Code: " + str(response.status_code) + " " + \
    "Response Content: " + str(response.text))

    if(execPassOrFail):
        UtilLogger.verboseLogger.info("%s: \t3: SimpleUpdate POST call passed" %(fileName))
    else:
        UtilLogger.verboseLogger.info("%s: \t3: SimpleUpdate POST call failed" %(fileName))

    # time.sleep(Config.waitForFirmwareUpdate)

    # Query Firmware Status until we've disconnected with a timeout in case it doesn't happen soon enough
    attempt_timeout = time.time() + 10
    while execPassOrFail and time.time() < attempt_timeout:
        execPassOrFail = GetFirmwareStatus(auth, port)
        cmdPassOrFail &= execPassOrFail

    if not execPassOrFail:
        UtilLogger.verboseLogger.error("{}: \t4: Wait For System to Shutdown for FW Update failed".format(fileName))
        return cmdPassOrFail, version

    # Query Firmware Status (wait for Firmware Complete)
    attempt_timeout = time.time() + Config.waitForFirmwareUpdate
    while not execPassOrFail and time.time() < attempt_timeout:
        execPassOrFail = GetFirmwareStatus(auth, port)
        cmdPassOrFail &= execPassOrFail

    if(execPassOrFail):
        UtilLogger.verboseLogger.info("%s: \t4: GetFirmwareStatus passed" %(fileName))
    else:
        UtilLogger.verboseLogger.info("%s: \t4: GetFirmwareStatus failed" %(fileName))

    # Get FW Version to confirm if image was re-flashed successfully
    (execPassOrFail, version) =  GetFirmwareVersion(auth, port)
    cmdPassOrFail &= execPassOrFail

    if(execPassOrFail):
        UtilLogger.verboseLogger.info("%s: \t5: GetFirmwareVersion passed" %(fileName))
    else:
        UtilLogger.verboseLogger.info("%s: \t5: GetFirmwareVersion failed" %(fileName))

    return (cmdPassOrFail, version)


def push_fw_for_staging(fw_file, local_location, dest_location=None):
    """
    Pushes any kind of FW or file to the BMC from a specified location to either a specified or default location on the
    BMC.
    :param fw_file: The name of the file that's being transferred
    :param local_location: The local relative location of where the file to be transferred is located
    :param dest_location: OPTIONAL: If left as None, the default location will be used. In most cases this is the way
    to go since all FW updates are staged in the same remote location. If you wish to push to another location then
    you can specify a new path.
    :return: True or False based on the success
    """

    cmd_pass_or_fail = True

    if dest_location is None:
        dest_location = "/var/wcs/home/"

    local_file = "{0}{1}".format(local_location, fw_file)
    dest_file = "{0}{1}".format(dest_location, fw_file)

    UtilLogger.verboseLogger.info("Transferring {0} to BMC location {1}".format(fw_file, dest_location))

    trySFTP = 0
    exec_pass_or_fail = False

    timeout = time.time() + Config.sftpSleepTimeout
    while time.time() < timeout and exec_pass_or_fail is not True:
        trySFTP += 1
        UtilLogger.verboseLogger.error("PushImage:  === try " + str(trySFTP) + " ===\n")
        exec_pass_or_fail = Ssh.sftpPutFile(local_file, dest_file, Config.bmcUser, Config.bmcPassword)
        # time.sleep(3)

    cmd_pass_or_fail &= exec_pass_or_fail

    return cmd_pass_or_fail


# Prepare for Firmware Update
def PrepareFirmwareUpdate(auth, port):

    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("%s: running %s fxn" %(fileName, funcName))

    # Define REST variables Prepare
    data = {"Operation":"Prepare"}    
    getResource = 'redfish/v1/Managers/System/Actions/Manager.FirmwareUpdate'

    # Send REST request and verify response (will reboot the BMC)    
    (cmdPassOrFail, response) = SendRestRequest( getResource, auth, port, data, "POST" )

    if(cmdPassOrFail):
        UtilLogger.verboseLogger.info("%s: \t18: SendRestRequest passed" %(fileName))
    else:
        UtilLogger.verboseLogger.info("%s: \t18: SendRestRequestfailed" %(fileName))

    # Wait for the FirmwareUpdate command to complete
    time.sleep(Config.waitForFirmwareUpdate)

    return cmdPassOrFail

# Get Firmware Status (Wait for the BMC Update Progress)
def GetFirmwareStatus(auth, port):

    applyPassOrFail = False

    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("%s: running %s fxn" %(fileName, funcName))    
    getResource = 'redfish/v1/Managers/System'
    
    # Query the BMC for a "Update Progress" response.
    totalWaitTime = time.time() + Config.applyFirmwareResponseLimit

    while (time.time() < totalWaitTime) and not applyPassOrFail:
        # Send REST API and verify response
        (cmdPassOrFail, response) = SendRestRequest( getResource, auth, port )        
        if (cmdPassOrFail):
            jsonResponse = response.json()
            if( (str(jsonResponse["Status"]["State"]).strip() == "Enabled" ) and (str(jsonResponse["Status"]["Health"]).strip() == "OK" ) ):
                applyPassOrFail = True
                break
        # Wait and try again...
        time.sleep(Config.applyFirmwareToSleepInSeconds)

    return applyPassOrFail

# Get Firmware Status (Wait for the BMC Update Progress)
def Old_GetFirmwareStatus(auth, port):

    applyPassOrFail = False

    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("%s: running %s fxn" %(fileName, funcName))

    # Define Action variables
    data = {"Operation":"Query"}    
    getResource = 'redfish/v1/Managers/System/Actions/Manager.FirmwareUpdateState'
    
    # Query the BMC for a "Update Progress" response.
    totalWaitTime = time.time() + Config.applyFirmwareResponseLimit

    while (time.time() < totalWaitTime) and not applyPassOrFail:
        # Send REST API and verify response
        (cmdPassOrFail, response) = SendRestRequest(getResource, auth, port, data, "POST")
        if (cmdPassOrFail):
            jsonResponse = response.json()
            if 'BMC Update Progress' in jsonResponse:
                updateProgress = jsonResponse['BMC Update Progress']
                UtilLogger.verboseLogger.info("%s: Progress Status: %s" %(fileName, updateProgress))
                if "Apply Complete" in updateProgress: 
                    UtilLogger.verboseLogger.info("%s: Apply Completed" %(fileName))
                    applyPassOrFail = True
                    break

        # Wait and try again...
        time.sleep(Config.applyFirmwareToSleepInSeconds)

    return applyPassOrFail


# Apply Firmware Update
def ApplyFirmwareUpdate(auth, port):

    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("%s: running %s fxn" %(fileName, funcName))

    # Define REST variables Apply
    data = {"Operation":"Apply"}    
    getResource = 'redfish/v1/Managers/System/Actions/Manager.FirmwareUpdate'

    # Send REST API and verify response.
    (cmdPassOrFail, response) = SendRestRequest(getResource, auth, port, data, "POST")

    return cmdPassOrFail


# Reset Firmware
def ResetFirmware(auth, port):

    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("%s: running %s fxn" %(fileName, funcName))

    # Define REST variables for Reset
    data = {"ResetType":"GracefulRestart"}    
    getResource = 'redfish/v1/Managers/System/Actions/Manager.Reset'

    # Send REST API and verify response
    (cmdPassOrFail, response) = SendRestRequest(getResource, auth, port, data, "POST")

    # Define REST variables for Abort
    data = {"Operation":"Abort"}    
    getResource = 'redfish/v1/Managers/System/Actions/Manager.FirmwareUpdate'

    # Send REST API and verify response
    (cmdPassOrFail, _) = SendRestRequest(getResource, auth, port, data, "POST" )

    # Wait for the Reset command to complete
    time.sleep(Config.resetFirmwareToSleepInSeconds)

    return cmdPassOrFail

# Copy (FTP) the image to the BMC
def PushImage(localFilePath, hostFilePath, username, password):

    # This needs to be False here since we are waiting for it to became True within a specified amount of time
    cmdPassOrFail = False

    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("{0}: running {1} fxn".format(fileName, funcName))

    # Copy the image to the BMC
    UtilLogger.verboseLogger.info("{0}: Copying {1} to {2}, username {3} password {4}"
                                  .format(fileName, localFilePath, hostFilePath, username, password))
    trySFTP = 0

    timeout = time.time() + Config.sftpSleepTimeout
    while time.time() < timeout and cmdPassOrFail is not True:
        trySFTP += 1
        UtilLogger.verboseLogger.error("PushImage:  === try " + str(trySFTP) + " ===\n")
        cmdPassOrFail = Ssh.sftpPutFile(localFilePath, hostFilePath, username, password)
        time.sleep(3)

    return cmdPassOrFail


# Get the Version of the existing Firmware
def GetFirmwareVersion(auth, port=Config.httpRedfishPort, timeout = 180):
    global fileName

    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("%s: running %s fxn" %(fileName, funcName))

    # Define Test variables
    fmVersion = None              
    getResource = 'redfish/v1/Managers/System'
        
    # Get the Firmware Version using Redfish 
    (cmdPassOrFail, response) = SendRestRequest(getResource, auth, port, data = None, restRequestMethod = "GET", timeout = timeout)
    
    if cmdPassOrFail:
        responseJSON = response.json()
        if "FirmwareVersion" in responseJSON:
            fmVersion = responseJSON["FirmwareVersion"]
            UtilLogger.verboseLogger.info("%s.version: Current Firmware Version: %s" %(fileName, fmVersion))

        else:
            UtilLogger.verboseLogger.error("%s.version: did NOT find Firmware Version" %(fileName))

    UtilLogger.verboseLogger.info("%s.version: FW Version: %s" %(fileName, fmVersion)) 

    return (cmdPassOrFail, fmVersion)


def GetResourceValues(restResource):
    """ GET REST resource fields """
     # Define request variables
    port = str(Config.httpRedfishPort)
    headers = {'Content-Type':'application/json'}    
    auth = (Config.bmcUser, Config.bmcPassword)
    userPasswd = "%s:%s" %(Config.bmcUser, Config.bmcPassword)
    encoded = "Basic %s" %(base64.b64encode(userPasswd))
    headers.update({"Authorization":encoded})
    host = Config.bmcIpAddress    
    # Send REST GET request and verify response
    session = None                      
    (cmdPassOrFail, response) = RestApiCall( session, host, restResource, "GET", auth, port, None, headers, restAPITimeout = Config.restAPICallTimeout )

    return(cmdPassOrFail, response)

def PostResourceValues( restResource, data ):
    """ Update the REST resource fields specified in the payload (data) """

 # Define request variables
    port = str(Config.httpRedfishPort)
    headers = {'Content-Type':'application/json'}    
    username = Config.bmcUser
    password = Config.bmcPassword
    auth = (username, password)
    host = Config.bmcIpAddress    
    # Send REST POST request and verify response
    session = None
    (cmdPassOrFail, response) = RestApiCall( session, host, restResource, "POST", auth, port, data, headers )

    return  (cmdPassOrFail, response)


def VerifyFRUValues( response, data ):
    """
        Compare the values in the response to the expected values
        in payload (data)
    """

    # Define Test variables
    fruPassOrFail = True
    responseJson = response.json()

    # Example all of the FRU values for modification
    for FRU_field in data:
        if FRU_field in responseJson:
            FRU_response_value = responseJson[FRU_field]
            FRU_data_value = data[FRU_field]
            if not FRU_response_value == FRU_data_value:
                UtilLogger.verboseLogger.error("%s: FRU Field %s was not updated successfully" %(fileName, FRU_field))
                fruPassOrFail = False
            else:
                UtilLogger.verboseLogger.info("%s: FRU Field: %s; New Value: %s" %(fileName, FRU_field, FRU_data_value))

    return(fruPassOrFail)


def DisplayFRUValues(response, data):
    """
        Display the values of the FRU Fields that were specified
        in the payload (data)
    """

    # Define Test variables
    responseJson = response.json()

    for key in data.keys():
        msgKey = "%s@Message.ExtendedInfo" %key
        if msgKey in responseJson:
            message = responseJson[msgKey]["Message"]
            UtilLogger.verboseLogger.info("%s: REST Response Message: %s" %(fileName, message))

    return

# Issue the REST command and get the REST response
def SendRestRequest(getResource, auth, port, data=None, restRequestMethod="GET", timeout = 5):

    # Send POST Rest Request
    session = None
    jsonResponse = None
    host = Config.bmcIpAddress
    headers = {'Content-Type':'application/json'}
    userPasswd = "%s:%s" %(auth[0], auth[1])
    encoded = "Basic %s" %(base64.b64encode(userPasswd))
    headers.update({"Authorization":encoded})
    cmdPassOrFail, response = RestApiCall( session, host, getResource,  restRequestMethod, auth, port, data, headers, timeout )

    if response:
        jsonResponse = response.json()
        ErrorMsg = None
        if 'error' in jsonResponse:
            ErrorMsg = jsonResponse['error']

    if cmdPassOrFail:
        if ErrorMsg:
            UtilLogger.verboseLogger.info(fileName + ".Execute:" + \
                " ====> ERROR returned in response: " + response.text)

        UtilLogger.verboseLogger.info(fileName + ".Execute:" + \
            " REST API for resource " + getResource + \
            " passed with status code " + str(response.status_code) + \
            " and response text: " + str(response.text))
    else:
        responseStatusCode = str(response.status_code) if response else "None"
        responseText = str(response.text)  if response else "None"
        UtilLogger.verboseLogger.error(fileName + ".Execute:" + \
            " REST API for resource " + getResource + \
            " failed with status code " + responseStatusCode + \
            " and response text: " + responseText)

    return (cmdPassOrFail, response)

def GetRandString():
    x = random.randint(1,256)
    random_str = ''.join(choice(ascii_uppercase)+''.join(choice(ascii_lowercase))+''.join(choice(digits)) for i in range( int(x) ) )
    return random_str
