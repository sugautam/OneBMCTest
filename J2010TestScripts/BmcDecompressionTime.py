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
import time
import inspect
import AcPowerIpSwitch
import UtilLogger
import Config
import RedFish

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

    return True


# Function will calcuate the time to power cycle a Server Blade
def Execute(interfaceParams):
    global fileName, session, headers, auth, testPassOrFail

    # Define Test variables
    funcName = inspect.stack()[0][3]    

    testPassOrFail = True
    startTest = time.time()

    try:
        # Power Down Server Blade
        (powerPassOrFail, response) = AcPowerIpSwitch.SetPowerOnOff(Config.acPowerIpSwitchOutlet, 0)
        testPassOrFail &= powerPassOrFail
        if powerPassOrFail:
            UtilLogger.verboseLogger.info("%s: Server blade powered down." %(fileName))
        else:
            UtilLogger.verboseLogger.error("%s: Failed to power down server blade." %(fileName))

        # Sleep
        UtilLogger.verboseLogger.info("%s: Sleeping for %s seconds." %(fileName, Config.acPowerOffSleepInSeconds))
        time.sleep(Config.acPowerOffSleepInSeconds)

        # Power Up Server Blade
        (powerPassOrFail, response) = AcPowerIpSwitch.SetPowerOnOff(Config.acPowerIpSwitchOutlet, 1)
        testPassOrFail &= powerPassOrFail
        if powerPassOrFail:
            UtilLogger.verboseLogger.info("%s: Server blade powered up." %(fileName))
        else:
            UtilLogger.verboseLogger.error("%s: Failed to power up server blade." %(fileName))

        # Wait for Redfish Server to start
        username = Config.bmcUser
        password = Config.bmcPassword    
        redfishPassOrFail = RedFish.CheckForRunningRedfishServer( username, password )
        testPassOrFail &= redfishPassOrFail
        if (redfishPassOrFail):
            UtilLogger.verboseLogger.error("%s: RedFish server started." %(fileName))
        else:
            UtilLogger.verboseLogger.error("%s: Failed to start RedFish server." %(fileName))
            
        endTest = time.time()
        testTime = endTest - startTest
        UtilLogger.verboseLogger.error("%s: Test took %f." %(fileName, testTime))
    except Exception, e:
        UtilLogger.verboseLogger.info( fileName + ": Test failed with exception - " + str(e))
        testPassOrFail = False

    return testPassOrFail


# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global fileName, testPassOrFail
    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))    
    return testPassOrFail


