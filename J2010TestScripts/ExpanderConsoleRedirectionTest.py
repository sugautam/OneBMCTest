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
import Ssh
import os
import time
import json

# Global variables
fileName = os.path.basename(__file__)
cmdPassOrFail = True

# Setup Function
def Setup(interfaceParams):
    global fileName
    UtilLogger.verboseLogger.info("%s: running Setup fxn" %(fileName))

    return True

# Function will test completion code for the serial ports
def Execute(interfaceParams):
    global cmdPassOrFail, fileName
    # Define Test variables
    cmdPassOrFail = True
    response = None

    # Specify Expander Board to Power On
    data = {"ResetType":"ForceOn"}    
    # Update the specified Storage Enclosure field
    # Define Test variables    

    try:
        for seId in Config.J2010allSeIDs:
            postResource = 'redfish/v1/Chassis/System/StorageEnclosure/%s/Actions/Chassis.Reset' %(seId)
            # Send REST Post request    
            (execPassOrFail, response) = RedFish.PostResourceValues( postResource, data )     
            cmdPassOrFail &= execPassOrFail

            if(cmdPassOrFail == False ):
                UtilLogger.verboseLogger.error("%s: Powering ON the board on seId %d failed with response %s" %(fileName, seId, response))
                return False    
        execCmds = ['\r']                       # 
        execCmds.append('\rhelp\r')             # Help command
        execCmdsResponse = "CLI Help"
    
        for sshPort in Config.J2010sshPorts:
            UtilLogger.verboseLogger.info("%s: running Execute for Port %s" %(fileName, sshPort))
        
            (execPassOrFail, sshOutputs, parsedCmdOutputs) = Ssh.sshExecuteCommand( execCmds, Config.bmcUser, Config.bmcPassword, sshPort )
            if (execPassOrFail):
                for sshOutput in sshOutputs:
                    if execCmdsResponse in sshOutput:
                        UtilLogger.verboseLogger.info("%s: successfully found '%s' in response" %(fileName, execCmdsResponse))
                        cmdPassOrFail = True

            if (not execPassOrFail):
                UtilLogger.verboseLogger.error("%s: failed to find '%s' in response" %(fileName, execCmdsResponse))
                cmdPassOrFail = False

    except Exception, e:
        UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))
        return False

    return cmdPassOrFail


# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global cmdPassOrFail, fileName
    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))    
    return cmdPassOrFail
