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

import Config
import IpmiUtil
import Ssh
import UtilLogger

# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info("SshFunctionalTest.py: running Setup fxn")

    return True

# Function will test SSH by opening an SSH session and 
# getting the date/time in SAC prompt
def Execute(interfaceParams):

    # Define Test variables
    testName = 'SshFunctionalTest'
    testPassOrFail = True
    respData = None
    
    try:
        # Soft-Power On blade to boot to OS
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis, Config.cmdChassisControl,\
            [ '01' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("ChassisControl.PowerUp: " + \
                "success completion code: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("ChassisControl.PowerUp: " + \
                "command failed with completion code: " + str(respData))
        testPassOrFail &= cmdPassOrFail

        # Sleep
        UtilLogger.verboseLogger.info("SshFunctionalTest: sleeping for " + \
            str(Config.bootToOsSleepInSeconds) + " seconds..")
        time.sleep(Config.bootToOsSleepInSeconds)

        # Execute commands to verify SSH is in SAC prompt
        
        # Enter newline until SAC prompt is reached
        
        # Initialize local variables
        execCmds = ['\n']
        sacPassOrFail = False
        retryCount = 3
        for i in range(retryCount):

            # Execute command
            sshPassOrFail, sshOutputs = Ssh.sshExecuteCommand(execCmds)
            if sshPassOrFail:
                # Check for expected response 'SAC' prompt
                for line in sshOutputs[0].split('\n'):
                    if "SAC" in line:
                        sacPassOrFail = True
                        break
        if sacPassOrFail:
            UtilLogger.verboseLogger.info("SshFunctionalTest: successfully " + \
                "verified SAC prompt via BMC SSH with response: " + str(sshOutputs[0]))
        else:
            UtilLogger.verboseLogger.error("SshFunctionalTest: BMC SSH SAC prompt " + \
                "verification failed after " + str(retryCount) + " retries. " + \
                "BMC SSH test provided " + \
                "unexpected response for command " + \
                str(execCmds[0]) + ": " + str(sshOutputs[0]))
            return False

        execCmds = ['\n', 's\n']
        sshPassOrFail, sshOutputs = Ssh.sshExecuteCommand(execCmds)
        if sshPassOrFail:

            # Check for expected response for SAC
            expectedResponse = False
            for line in sshOutputs[1].split('\n'):
                if "Date:" in line:
                    expectedResponse = True
                    break
            if expectedResponse:
                UtilLogger.verboseLogger.info("SshFunctionalTest: successfully " + \
                    "verified SAC prompt command execution via " + \
                    "BMC SSH with repsonse: " + str(sshOutputs[1]))
            else:
                UtilLogger.verboseLogger.error("SshFunctionalTest: BMC SSH " + \
                    "command execution failed. BMC SSH provided " + \
                    "unexpected response for command " + \
                    str(execCmds[1]) + ": " + str(sshOutputs[1]))
                testPassOrFail = False

        else:
            UtilLogger.verboseLogger.error("SshFunctionalTest: BMC SSH failed " + \
                "to execute commands " + str(execCmds))
            testPassOrFail = False
    except Exception, e:
        UtilLogger.verboseLogger.error("SshFunctionalTest.py: " + \
            "test failed with exception " + str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("SshFunctionalTest.py: running Cleanup fxn")

    return True