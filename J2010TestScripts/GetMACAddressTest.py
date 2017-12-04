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

import Config
import RedFish
import UtilLogger
import Ssh
import os
import re

# Global variables
fileName = os.path.basename(__file__)
cmdPassOrFail = True

# Setup Function
def Setup(interfaceParams):
    global fileName
    UtilLogger.verboseLogger.info("%s: running Setup fxn" %(fileName))

    return True


# Function will test completion code for GPIO Registers
def Execute(interfaceParams):
    global cmdPassOrFail
    # Define Test variables
    cmdPassOrFail = False
    HWaddr = None
    interface = "eth0"
    regexPattern = "^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$"

    execCmds = ['\n']                      
    execCmds.append("ifconfig %s\n" %(interface))

    try:
        # Get MAC Address
        (execPassOrFail, sshOutputs, parsedCmdOutputs) = Ssh.sshExecuteCommand(execCmds, username=Config.bmcUser, password=Config.bmcPassword)
    
        # Search ALL lines in response from the HWaddr
        if (execPassOrFail):
            for sshOutput in sshOutputs:
                if "HWaddr" in sshOutput:
                    tokens = sshOutput.split("HWaddr")
                    HWaddr = tokens[1].split()[0]

                    # Validate the address
                    regexCompile = re.compile(regexPattern)
                    m = regexCompile.match(HWaddr)
                    if (m):
                        UtilLogger.verboseLogger.info("%s: MAC Address: %s" %(fileName, HWaddr))
                        cmdPassOrFail = True
                    else:
                        UtilLogger.verboseLogger.error("%s: invalid MACAddr format - %s" %(fileName, HWaddr))

                   # FIXME - Compare value to EEPROM

        if (not HWaddr):
            UtilLogger.verboseLogger.error("%s: failed to find MACAddr in response" %(fileName))
    except Exception, e:
            UtilLogger.verboseLogger.error("%s: test failed. Exception: %s" %(fileName, str(e)))

    return cmdPassOrFail


# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global cmdPassOrFail

    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))

    return cmdPassOrFail
