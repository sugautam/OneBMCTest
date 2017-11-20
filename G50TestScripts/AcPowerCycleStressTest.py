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

import datetime
import os
import time
import AcPowerIpSwitch
import Config
import Helper
import RedFish
import UtilLogger
import base64
import Ssh

# Initialize global variables
fileName = os.path.basename(__file__)
session = None
headers = None
auth = None
testPassOrFail = True

# Setup Function
def Setup(interfaceParams):      
    return True

# Function will run stress test over REST
# for AC Power Cycling BMC
def Execute(interfaceParams):      
    global fileName, session, headers, auth, testPassOrFail

    username = Config.bmcUser 
    password = Config.bmcPassword     

    # Define Test variables
    testPassOrFail = True
    respData = []
    testName = 'AcPowerCycleStressTest'
    fwDecompList = []
    startTime = time.time()
    
    # total test time in seconds
    # total test time = 60 seconds/minute *
    #   60 minutes/hour * <totalTestTimeInHours>
    totalTestTime = startTime + 60 * 60 * Config.acPowerCycleStressTestTotalTime
    
    try:
        if not interfaceParams:
            UtilLogger.consoleLogger.info(\
                "Currently running in-band in server blade. Will not execute test.")
            UtilLogger.verboseLogger.info(\
                "Currently running in-band in server blade. Will not execute test.")
            return True
        else:
            UtilLogger.consoleLogger.info(\
                "Starting " + \
                str(Config.acPowerCycleStressTestTotalTime) + \
                "-hour AC Power Cycle stress test")
            UtilLogger.verboseLogger.info(\
                "Starting " + \
                str(Config.acPowerCycleStressTestTotalTime) + \
                "-hour AC Power Cycle stress test")

        # Run test
        # Print Cycle # PASS/FAIL for every test cycle
        testCycle = 0
        cyclesPassed = 0
        cyclesFailed = 0
        while time.time() < totalTestTime:

            cyclePassOrFail = True
            cycleStartTime = time.time()

            # Power Down Server Blade
            powerPassOrFail, response = AcPowerIpSwitch.SetPowerOnOff(Config.acPowerIpSwitchOutlet, 0)
            if powerPassOrFail:
                UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: Server blade powered down.")
            else:
                UtilLogger.verboseLogger.error("AcPowerCycleStressTest.py: Failed to power down server blade.")
            cyclePassOrFail &= powerPassOrFail

            # Sleep
            UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: " + "Sleeping for " + str(Config.acPowerOffSleepInSeconds) + " seconds.")
            time.sleep(Config.acPowerOffSleepInSeconds)

            # Power Up Server Blade
            powerPassOrFail, response = AcPowerIpSwitch.SetPowerOnOff( Config.acPowerIpSwitchOutlet, 1)
            if powerPassOrFail:
                UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: Server blade powered up.")
            else:
                UtilLogger.verboseLogger.error("AcPowerCycleStressTest.py: Failed to power up server blade.")
            cyclePassOrFail &= powerPassOrFail

            # Ping BMC until it responds
            pingPassOrFail, decompEndTime = Helper.PingAndCheckResponse(Config.acPowerOnSleepInSeconds, Config.bmcIpAddress)
            if pingPassOrFail:
                fwDecompList.append(decompEndTime)
            cyclePassOrFail &= pingPassOrFail

            # Connect to BMC via SSH and test to see if 
            #   boot to BMC Start screen can be detected
            cyclePassOrFail &= Helper.SshBootToBMCStartScreenTest( cycleStartTime, username, password, "g50" )
            
            if( cyclePassOrFail ):
                UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: Got the BMC command prompt")
                cyclePassOrFail &= True
            else:
                UtilLogger.verboseLogger.error("AcPowerCycleStressTest.py: Failed to get the BMC command prompt")
                cyclePassOrFail &= False

            # Define request variables
            port = str(Config.httpRedfishPort)
            headers = {'Content-Type':'application/json'}
            auth = (Config.bmcUser, Config.bmcPassword)
            userPasswd = "%s:%s" %(Config.bmcUser, Config.bmcPassword)
            encoded = "Basic %s" %(base64.b64encode(userPasswd))
            headers.update({"Authorization":encoded})
            host = Config.bmcIpAddress
            getResource = 'redfish/v1'
            timeout = Config.httpTimeout
            tryGet = 0
            # Send REST API and verify response
            waitTime = time.time()
            while( (time.time() - waitTime) < Config.bootToOsSleepInSeconds ):
                cmdPassOrFail, response = RedFish.RestApiCall( session, host, getResource, "GET", auth, port, None, headers, timeout )
                if cmdPassOrFail:
                    UtilLogger.verboseLogger.info("AcPowerCycleStressTest:" + \
                        " GET REST API for resource " + getResource + \
                        " passed with status code " + str(response.status_code) + \
                        " and response text: " + str(response.text))
                    break
                else:
                    if response is not None:
                        UtilLogger.verboseLogger.error("AcPowerCycleStressTest:" + \
                            " GET REST API for resource " + getResource + \
                            " failed with status code " + str(response.status_code) + \
                            " and response text: " + str(response.text))
                    else:
                        tryGet += 1
                        UtilLogger.verboseLogger.error("AcPowerCycleStressTest:  === try " + str(tryGet) +" ===\n" +\
                            " GET REST API for resource " + getResource + \
                            " failed with response None.")
                        time.sleep(3)
            # Verify test cycle
            if cyclePassOrFail:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " AcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " AcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " passed.")
                cyclesPassed += 1
            else:
                UtilLogger.consoleLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " AcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                UtilLogger.verboseLogger.info(\
                    str(datetime.timedelta(seconds=(time.time() - cycleStartTime))) + \
                    " AcPowerCycleStressTest.py: Cycle " + str(testCycle) + 
                    " failed.")
                cyclesFailed += 1
            UtilLogger.verboseLogger.info("")
            testCycle += 1
            testPassOrFail &= cyclePassOrFail

        # Log FW Decompression Results
        Helper.LogFwDecompressionResults(fwDecompList)

        # Print Test Summary results
        endTime = time.time()
        UtilLogger.consoleLogger.info(\
            "AC Power Cycle over REST Stress Test" + \
            " Summary - Cycles Passed: " + \
            str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
            " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
            " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
        UtilLogger.verboseLogger.info(\
            "AC Power Cycle over REST Stress Test" + \
            " Summary - Cycles Passed: " + \
            str(cyclesPassed) + " Cycles Failed: " + str(cyclesFailed) + \
            " Total Cycles: " + str(cyclesPassed + cyclesFailed) + \
            " Test Duration: " + str(datetime.timedelta(seconds=endTime-startTime)))
    except Exception, e:
        UtilLogger.verboseLogger.info("AcPowerCycleStressTest.py: exception occurred - " + \
            str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global testPassOrFail    
    return testPassOrFail
