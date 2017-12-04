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

import requests
from requests.auth import HTTPBasicAuth
import time

import Config
import UtilLogger

# Function sends power action
# to AcIpPowerSwitch via 
# Http GET Request
# 
# Inputs:
#   outlet (int): 0 (all outlets), 1 (outlet 1), 2 (outlet 2)
#   powerAction (int): 
#       0 - power off
#       1 - power on
#       2 - power toggle (on -> off, off -> on)
#       3 - UIS on
#       4 - UIS off
#
# Outputs:
#   sendPassOrFail (bool): successful (true), failed (false)
#   response (object): Http response object
def SetPowerOnOff(outlet, powerAction):
    # Send Http Request
    # to send power action to Ac Switch
    sendPassOrFail, response =  SendHttpGetRequest(\
        Config.acPowerIpSwitchSsnEn,\
        Config.acPowerIpSwitchIpAddress,\
        Config.acPowerIpSwitchPort,\
        '/cgi-bin/control.cgi',\
        { 'target' : outlet,\
        'control' : powerAction },\
        Config.acPowerIpSwitchUserName,\
        Config.acPowerIpSwitchPassword)

    return sendPassOrFail, response

# Function will AC Power Cycle Blade
def AcPowerCycleBlade(interfaceParams):

    # Initialize variables
    acCyclePassOrFail = False

    # AC power cycle blade
    
    # AC Power Off Server Blade
    powerPassOrFail, response = SetPowerOnOff(\
        Config.acPowerIpSwitchOutlet, 0)
    if powerPassOrFail:
        UtilLogger.verboseLogger.info("AcPowerCycleBlade: " + \
            "Server blade powered down.")
    else:
        UtilLogger.verboseLogger.error("AcPowerCycleBlade: " + \
            "Failed to power down server blade.")
    acCyclePassOrFail &= powerPassOrFail

    # Sleep
    UtilLogger.verboseLogger.info("AcPowerCycleBlade: " + \
        "Sleeping for " + str(Config.acPowerOffSleepInSeconds) + " seconds.")
    time.sleep(Config.acPowerOffSleepInSeconds)

    # AC Power On Server Blade
    powerPassOrFail, response = SetPowerOnOff(\
        Config.acPowerIpSwitchOutlet, 1)
    if powerPassOrFail:
        UtilLogger.verboseLogger.info("AcPowerCycleBlade: " + \
            "Server blade powered up.")
    else:
        UtilLogger.verboseLogger.error("AcPowerCycleBlade: " + \
            "Failed to power up server blade.")
    acCyclePassOrFail &= powerPassOrFail

    # Sleep
    UtilLogger.verboseLogger.info("AcPowerCycleBlade: " + \
        "Sleeping for " + str(Config.acPowerOnSleepInSeconds) + " seconds.")
    time.sleep(Config.acPowerOnSleepInSeconds)

    return acCyclePassOrFail

# Function will send HTTP GET request using the specified arguments
#
# Inputs:
#   hostname (string): name of host or IP address
#   port (int or string): host port
#   sslEn (bool): https (true) or http (false)
#   command (string): needs to be prepended with '/'
#   params (dictionary - key: string, value: int or string): parameters
#       needed for command
#   username (string): optional
#   password (string): optional
#
# Returns: 
# sendPassOrFail (bool): command success (200 status code) or failure
# response (object): http response
#   response object includes:
#       response.status_code (int): response status code
#       response.text (unicode): response content
def SendHttpGetRequest(sslEn, hostname, port, command, params=None, username=None, password=None) :

    # initialize function variables
    request = ''
    sendPassOrFail = False

    # Determine http vs https
    if sslEn:
        request = 'https://'
    else:
        request = 'http://'

    # Concatenate hostname and port
    request += hostname
    request += ':'
    request += str(port)

    # Concatenate command
    request += command

    # Concatenate parameters if not None
    if params is not None:
        request += '?'
        for paramKey, paramValue in params.iteritems():
            request += str(paramKey)
            request += '='
            request += str(paramValue)
            request += '&'

    # Send HTTP GET Request and get response    
    response = requests.get(request, auth=HTTPBasicAuth(username, password), timeout=120 )
    if response.status_code != 200:
        UtilLogger.verboseLogger.error("AcPowerIpSwitch.SendHttpGetRequest: HTTP Request " + \
            request + " returned error status " + str(response.status_code))
    else:
        sendPassOrFail = True

    if Config.debugEn:
        UtilLogger.verboseLogger.info("AcPowerIpSwitch.SendHttpGetRequest: " + \
            "Http Request URL: " + request + " " + \
            "Response Status Code: " + str(response.status_code) + " " + \
            "Response Content: " + str(response.text))

    return sendPassOrFail, response