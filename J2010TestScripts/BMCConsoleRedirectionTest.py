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

    username = Config.bmcUser
    password = Config.bmcPassword     
    # Define Test variables
    response = None

    execCmds = ['\n']                       # 
    execCmds.append('\nhelp\n')             # Help command
    execCmdsResponse = "GNU bash"

    UtilLogger.verboseLogger.info("%s: running Execute" %(fileName))
    UtilLogger.verboseLogger.info("SSH executing commands %s with username %s and password %s" %( execCmds, username, password ))
    (execPassOrFail, sshOutputs, parsedCmdOutputs) = Ssh.sshExecuteCommand( execCmds, username, password )
    cmdPassOrFail &= execPassOrFail

    if (execPassOrFail):
        for sshOutput in sshOutputs:
            if execCmdsResponse in sshOutput:
                UtilLogger.verboseLogger.info("%s: successfully found '%s' in response" %(fileName, execCmdsResponse) )
                cmdPassOrFail = True

    if (not execPassOrFail):
        UtilLogger.verboseLogger.error("%s: failed to find '%s' in response" %(fileName, execCmdsResponse) )

    return cmdPassOrFail


# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global fileName, cmdPassOrFail
    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))    
    return cmdPassOrFail
