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

import XmlParser
import Config
import RedFish
import UtilLogger
import Ssh
import os

# Global variables
fileName = os.path.basename(__file__)
xmlParseObj = None
testPassOrFail = True
# Setup Function
def Setup(interfaceParams):
    global fileName
    UtilLogger.verboseLogger.info("%s: running Setup fxn" %(fileName))

    return True

# Function will test completion code for GPIO Registers
def Execute(interfaceParams):
    global testPassOrFail, fileName
    # Parse Get Gpio List xml file

    try:
        xmlParserObj = XmlParser.XmlParser(Config.J2010getGpioListFilePath)
        if not xmlParserObj.root:
            UtilLogger.verboseLogger.error(("%s: failed to parse Xml file. Will not execute test." %(fileName)))
            return False
    
        testPassOrFail = True     
    
        # Verify Get GPIO for each GPIO number listed in XML
        for gpioInfo in xmlParserObj.root:    
            testPassOrFail &= True
            signal = gpioInfo.attrib['signal']
            theDirection = []
            theDirection = gpioInfo.attrib['direction'].split(',')
            expectedDirection = theDirection[0]

            UtilLogger.verboseLogger.info("%s: running Execute for Signal %s" %(fileName, signal))

            execCmds = ['\n']                      
            execCmds.append("gpioutil -n %s\n" %(signal))

            # Get GPIO Pin Direction
            regexPattern = r"DIRECTION: (\w+)"
            (execPassOrFail, sshOutputs, parsedCmdOutputs) = Ssh.sshExecuteCommand( execCmds, username=Config.bmcUser, password=Config.bmcPassword, expectedOutput = expectedDirection, regExpPattern = regexPattern )
            testPassOrFail &= execPassOrFail

            if (execPassOrFail):            
                actualDirection = parsedCmdOutputs                
                if not actualDirection:
                    UtilLogger.verboseLogger.error("%s: Signal Direction failed: Actual Direction was returned an empty string" %(fileName))
                    testPassOrFail = False
                    continue                                                          
                # Note:  pinDirection may contain several directions, seperated by
                #        a comma (i.e. "in,falling")
                pinDirections = expectedDirection.split(',')                                
                
                for pinDirection in pinDirections:
                    # Validate GPIO pin direction                                       
                    if pinDirection.strip() == actualDirection:
                        UtilLogger.verboseLogger.info("%s: Signal Direction successful: '%s'; Direction: %s" %(fileName, signal, actualDirection))                        
                        break
                    if pinDirection == pinDirections[-1]:
                        UtilLogger.verboseLogger.error("%s: Signal Direction failed : '%s'; Actual Direction: %s; Expected Direction(s): %s" %(fileName, signal, actualDirection, ','.join(pinDirections)))
                        testPassOrFail = False
            else:
                UtilLogger.verboseLogger.error("%s: failed to find '%s' in response" %(fileName, signal))
                testPassOrFail = False

    except Exception, e:
            UtilLogger.verboseLogger.error( fileName + ": Test failed with exception - " + str(e))
            testPassOrFail = False
            
    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global fileName
    UtilLogger.verboseLogger.info("%s: running Cleanup fxn" %(fileName))    
    return testPassOrFail

