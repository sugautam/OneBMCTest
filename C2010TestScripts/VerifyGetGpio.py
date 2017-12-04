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
import IpmiUtil
import XmlParser
import UtilLogger

# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifyGetGpio.py: running Setup fxn")

    return True

# Function will test completion code for Get Gpio
# and also validate the GPIO direction and value for each
# GPIO number specified in the Get Gpio List XML File
def Execute(interfaceParams):

    # Define Test variables
    cmdPassOrFail = True
    respData = None

    # Define GetGpio variables
    cmdName = 'GetGpio'
    cmdNum = Config.cmdGetGpio
    netFn = Config.netFnOem30

    # Parse Get Gpio List xml file
    xmlParserObj = XmlParser.XmlParser(Config.C2010getGpioListFilePath)
    if not xmlParserObj.root:
        UtilLogger.verboseLogger.error("VerifyGetGpio: failed to parse Xml file." \
            + " Will not execute test.")
        return False

    # Verify Get GPIO for each GPIO number listed in XML
    for gpioInfo in xmlParserObj.root:

        # Define local variables
        gpioNum = gpioInfo.attrib["number"]
        gpioDir = gpioInfo.attrib["direction"]
        gpioDirIdx = 0
        gpioVal = gpioInfo.attrib["value"]
        gpioValIdx = 1

        # Define get gpio request raw byte as GPIO pin number
        rawBytesList = [ gpioNum ]

        # Send raw bytes via IpmiUtil
        gpioPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
            netFn, cmdNum, rawBytesList)

        # If completion code not success,
        # fail GPIO and move to next GPIO
        if not gpioPassOrFail:
            UtilLogger.verboseLogger.error(cmdName + \
                ": Command failed for GPIO pin number 0x" + gpioNum + \
                ". Completion Code: " + str(respData))
            cmdPassOrFail = False
            continue

        # Validate GPIO pin direction and GPIO pin value
        # Note: if GPIO pin value is set to 'x', GPIO pin value
        # will not be validated
        gpioPassOrFail = gpioDir == respData[gpioDirIdx] and \
            ((gpioVal == respData[gpioValIdx]) or (gpioVal == 'x'))
        if gpioPassOrFail:
            if gpioVal == 'x':
                UtilLogger.verboseLogger.info(cmdName + \
                ": Command passed for GPIO pin number 0x" + gpioNum + \
                ". Pin Direction: 0x" + respData[gpioDirIdx] + \
                " Pin Value ignored")
            else:
                UtilLogger.verboseLogger.info(cmdName + \
                ": Command passed for GPIO pin number 0x" + gpioNum + \
                ". Pin Direction: 0x" + respData[gpioDirIdx] + \
                " Pin Value: 0x" + respData[gpioValIdx])
        else:
            if gpioVal == 'x':
                UtilLogger.verboseLogger.info(cmdName + \
                    ": Command failed for GPIO pin number 0x" + gpioNum + \
                    ". Expected Pin Direction: 0x" + gpioDir + \
                    " Actual Pin Direction: 0x" + respData[gpioDirIdx] + \
                    ". Pin Value ignored")
            else:
                UtilLogger.verboseLogger.info(cmdName + \
                    ": Command failed for GPIO pin number 0x" + gpioNum + \
                    ". Expected Pin Direction: 0x" + gpioDir + \
                    " Actual Pin Direction: 0x" + respData[gpioDirIdx] + \
                    ". Expected Pin Value: 0x" + gpioVal + \
                    " Actual Pin Value: 0x" + respData[gpioValIdx])

        cmdPassOrFail &= gpioPassOrFail

    # Verify response
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info(cmdName + \
            ": Command passed.")
    else:
        UtilLogger.verboseLogger.error(cmdName + \
            ": Command failed.")

    return cmdPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifyGetGpio.py: running Cleanup fxn")

    return True
