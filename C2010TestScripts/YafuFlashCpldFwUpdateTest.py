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

import os
import time
import Config
import Helper
import IpmiUtil
import UtilLogger
import FwFlash

# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info("YafuFlashCpldFwUpdateTest.py: running Setup fxn")

    return True

# Function will test CPLD FW Update using
# Yafuflash for either KCS or IPMI over LAN+
def Execute(interfaceParams):

    # Define Test variables
    testName = 'YafuFlashCpldFwUpdateTest'
    
    # Check if CPLD FW filepath exists
    # If not, do not run
    if not os.path.isfile(Config.cpldNextBinFilePath):
        UtilLogger.verboseLogger.error(testName + \
            ": CPLD FW binary with filepath " + \
            Config.cpldNextBinFilePath + \
            " does not exist. Will not run. ")
        return False

    # Flash BMC FW
    flashPassOrFail = FwFlash.YafuFlashCpldFw(\
        Config.cpldNextBinFilePath,\
        Config.bmcIpAddress,\
        Config.bmcUser,\
        Config.bmcPassword)

    # Verify flash successful
    if flashPassOrFail:
        UtilLogger.verboseLogger.info(testName + \
            ": CPLD FW flash test passed.")
    else:
        UtilLogger.verboseLogger.error(testName + \
            ": CPLD FW flash test failed.")

    return flashPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    # Detect and Remove BMC Hang
    return Helper.DetectAndRemoveBmcHang(interfaceParams)