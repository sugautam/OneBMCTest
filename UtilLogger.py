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
import logging
import Config

consoleLogger = None
summaryLogger = None
verboseLogger = None

# Verbose complete file name including full directory path, file name and extension.
verboseCompleteFileName = None

# Time stamp to be included in output file names.
fileTimeStamp = None

# Configure logger
def InitLogging(startTime):
    
    # Declare module-scope variables
    global consoleLogger
    global summaryLogger
    global verboseLogger
    global verboseCompleteFileName
    global fileTimeStamp

    # Format startTime
    fileTimeStamp = datetime.datetime.fromtimestamp(startTime).strftime('_%Y-%m-%d_%H-%M-%S')

    # Initialize summaryLogger
    summaryLogger = logging.getLogger('summaryLogger')
    summaryLogger.setLevel(logging.DEBUG) # logs all information

    # Initialize verboseLogger
    verboseLogger = logging.getLogger('verboseLogger')
    verboseLogger.setLevel(logging.DEBUG) # logs all information

    # Initialize consoleLogger
    consoleLogger = logging.getLogger('consoleLogger')
    consoleLogger.setLevel(logging.DEBUG) # logs all information

    # Define summary handler (logs to <summaryFileName>_<fileTimeStamp>.log)
    summaryHandler = logging.FileHandler(\
        Config.summaryLogPath + Config.summaryLogFileName + \
        fileTimeStamp + Config.summaryLogFileExtension, \
        mode='w')

    # Define verbose handler (logs to <verboseFileName>_<fileTimeStamp>.log)
    verboseCompleteFileName = Config.verboseLogPath + Config.verboseLogFileName \
                              + fileTimeStamp + Config.verboseLogFileExtension
    verboseHandler = logging.FileHandler(verboseCompleteFileName, mode='w')

    # Define console handler (output to console)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)

    # Add timestamp if switch enabled
    if Config.timestampEn:
        timestampFormatter = logging.Formatter('%(asctime)s - %(message)s')
        consoleHandler.setFormatter(timestampFormatter)
        summaryHandler.setFormatter(timestampFormatter)
        verboseHandler.setFormatter(timestampFormatter)

    # consoleLogger and summaryLogger prints 
    # output to console using consoleHandler configuration
    consoleLogger.addHandler(consoleHandler)
    summaryLogger.addHandler(consoleHandler) # summaryLogger also outputs to console

    # summaryLogger logs to both summary log and verbose log
    summaryLogger.addHandler(summaryHandler)
    summaryLogger.addHandler(verboseHandler)

    # verboseLogger only logs to verbose.log
    verboseLogger.addHandler(verboseHandler)

    return

def EnableShowVerbose():

    # Declare module-scope variables
    global verboseLogger

    # enable verboseLogger to also print output to console
    # using below configuration
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    verboseLogger.addHandler(console)

    return