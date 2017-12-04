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
import IpmiUtil
import UtilLogger
import socket
import binascii
import os
import XmlParser
import Config
import RedFish
import Ssh

fileName = os.path.basename(__file__)
testPassOrFail = True
gpioTestPassOrFail = True
xmlParseObj = None

PMDU_NODE_INCODE = {
    1: 0b000000, 2: 0b000001, 3: 0b000010, 4: 0b000011, 5: 0b000100, 6: 0b000101,
    7: 0b001000, 8: 0b001001, 9: 0b001010, 10: 0b001011, 11: 0b001100, 12: 0b001101,
    13: 0b010000, 14: 0b010001, 15: 0b010010, 16: 0b010011, 17: 0b010100, 18: 0b010101,
    19: 0b011000, 20: 0b011001, 21: 0b011010, 22: 0b011011, 23: 0b011100, 24: 0b011101,
    25: 0b100000, 26: 0b100001, 27: 0b100010, 28: 0b100011, 29: 0b100100, 30: 0b100101,
    31: 0b101000, 32: 0b101001, 33: 0b101010, 34: 0b101011, 35: 0b101100, 36: 0b101101,
    37: 0b110000, 38: 0b110001, 39: 0b110010, 40: 0b110011, 41: 0b110100, 42: 0b110101,
    43: 0b111000, 44: 0b111001, 45: 0b111010, 46: 0b111011, 47: 0b111100, 48: 0b111101,
}

# Prototype Setup Function
def Setup(interfaceParams):    
    UtilLogger.verboseLogger.info(\
        "VerifyGetChannelAuthenticationCapabilities.py: running Setup fxn")

    return True

# Function will test completion code for
# Get Channel Authentication Capabilities
def Execute(interfaceParams):
    global fileName, testPassOrFail
    
    # Define Test variables    
    respData = None    
    totalCount = 100
    try:
        for passCount in range( 1, totalCount+1 ):
            cmdPassOrFail = True        
            conn = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
            request = bytearray ([  0x06, 0x00, 0xff, 0x07,  # RMCP header
                                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x09, #IPMI session header
                                    0x20, 0x18, 0xc8, 0x81, 0x04, 0x38,  # IPMI header
                                    0x0e, 0x04, # Get Channel Authentication Capabilities command
                                    0x31    # Checksum
                                ])
        
            conn.sendto(request, (Config.bmcIpAddress, Config.ipmiPort) )
            conn.settimeout(2)
            response = conn.recvfrom (256)
            respData = bytearray(response[0])

            expectedData = [0x00, 0x01, 0x00, 0x18, 0x04, 0x37, 0x01, 0x00, 0x40]

            if( ValidateDataInResponse( respData, expectedData) == False ):
                UtilLogger.verboseLogger.error("%s: Received data is not a valid data" %(fileName))
                cmdPassOrFail = False
            
            if( ValidateGPIOslotID(respData[28]) == False ):
                UtilLogger.verboseLogger.error("%s: failed: (Slot ID) Received data is not a valid data" %(fileName))
                cmdPassOrFail = False

            if( respData != None ):        
                data = binascii.hexlify(respData)                
                UtilLogger.verboseLogger.info("%s: pass === %s ===\n data received:\n\t %s" %(fileName, passCount, data))

                # Verify response
                if cmdPassOrFail:
                    UtilLogger.verboseLogger.info("%s: Test passed" %(fileName))
                else:
                    UtilLogger.verboseLogger.error("%s: Test failed" %(fileName))
            else:
                 cmdPassOrFail = False                
            
            if( cmdPassOrFail == False ):
                UtilLogger.verboseLogger.error("%s: pass === %s === failed" %(fileName, passCount ))
    except Exception, e:
            UtilLogger.verboseLogger.error("VerifyGetChannelAuthenticationCapabilities: " + \
                " Test failed with exception - " + str(e))
            cmdPassOrFail = False

    testPassOrFail &= cmdPassOrFail

    return testPassOrFail

def ValidateDataInResponse( response, validList ):
    temp = response[20:28]    # bytes 20-28 are the response data. Checking if they are matching with the expected data
    try:
        for i in range(0,len(validList)-1):
            if(temp[i] != validList[i]):
                UtilLogger.verboseLogger.error("ERROR:  VerifyGetChannelAuthenticationCapabilities: Byte " + str(i+1) + " data is not correct: " )
                UtilLogger.verboseLogger.error( "ERROR: the data received is " + str(hex(temp[i])) + " and it is expecting to be " + str(hex(validList[i])) )
                return False
        if( ( (temp[7] & 0xc0 )) != validList[7] ):    # checking if the bits 6 -7 in the response are matching with the expected data ( the latest byte )
            return  False
    except Exception, e:
        UtilLogger.verboseLogger.error("VerifyGetChannelAuthenticationCapabilities: " + \
            " Test failed with exception - " + str(e))
        return False
    
    return True

def ValidateGPIOslotID(expectedData):
    global gpioTestPassOrFail, fileName
    global GPIOLen

    try:
        # remove two bits (bits [5:0] in the response)
        IPMISlotIDdataFilter = expectedData & 0x3f
        # incode to GPIO slot ID (PMDU_NODE_INCODE dictionary)
        SlotIdIncode = PMDU_NODE_INCODE.get(IPMISlotIDdataFilter)
        # GPIO slot ID binary bits
        GPIOSlotIDBin = "{0:06b}".format(SlotIdIncode)
        GPIOSlotID = list(GPIOSlotIDBin)
        # read slot id gpio definition from getgpioslotid.xml
        xmlParserObj = XmlParser.XmlParser(Config.J2010getGpioSlotIDFilePath)
        if not xmlParserObj.root:
            UtilLogger.verboseLogger.error(("[GPIOgetTest error]%s: failed to parse Xml file. Will not execute test." %(fileName)))
            return False

        gpioTestPassOrFail = True
        GPIOLen = len(GPIOSlotID)

        # Verify Get GPIO for each GPIO number listed in XML
        for gpioInfo in xmlParserObj.root:

            signal = gpioInfo.attrib['signal']
            gpio_pin = gpioInfo.attrib['gpio_pin']

            UtilLogger.verboseLogger.info("[GPIOgetTest info]%s: running Execute for Signal %s and gpio_pin %s" %(fileName, signal, gpio_pin))

            execCmds = ['\n']
            execCmds.append("gpioutil -p %s\n" %(gpio_pin))
            expectedSlotId = GPIOSlotID[GPIOLen-1]
            regexPattern = r'(\d)\s+j2010'

            (execPassOrFail, sshOutputs, parsedCmdOutputs) = Ssh.sshExecuteCommand( execCmds, username=Config.bmcUser, password=Config.bmcPassword, expectedOutput = expectedSlotId, regExpPattern = regexPattern )
            gpioTestPassOrFail &= execPassOrFail

            if (execPassOrFail): #timeout or channel not ready, it don't judge the result correct or not
                actualSlotId = parsedCmdOutputs
                if not actualSlotId:
                    UtilLogger.verboseLogger.error("%s: Signal Slot ID failed: Actual Slot Id was returned an empty string" %(fileName))
                    gpioTestPassOrFail = False

                if (actualSlotId == expectedSlotId):
                    UtilLogger.verboseLogger.info("%s: Signal Slot ID successful: '%s'; Slot ID value: %s" %(fileName, signal, parsedCmdOutputs))
                else:
                    UtilLogger.verboseLogger.error("%s: failed: %s slot ID is not correct " %(fileName, signal))
                    gpioTestPassOrFail = False
            else:
                UtilLogger.verboseLogger.error("%s: failed to find '%s' in response" %(fileName, signal))
                gpioTestPassOrFail = False

            GPIOLen = GPIOLen-1

    except Exception, e:
            UtilLogger.verboseLogger.error( fileName + ": Test failed with exception - " + str(e))
            gpioTestPassOrFail = False

    return gpioTestPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    global testPassOrFail
    UtilLogger.verboseLogger.info("VerifyGetChannelAuthenticationCapabilities.py: running Cleanup fxn")

    return testPassOrFail
