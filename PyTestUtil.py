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

import CliParser
import Program
import ResultProcessor
import UtilLogger
import Program
import signal
import inspect
import sys


def signalHandler(signum, frame):
    """
    Trap Aborts
    """

    funcName = inspect.stack()[0][3]
    UtilLogger.verboseLogger.info("\n%s: Signal: %d Caught\r" 
                                  %(funcName, signum))

    # Process the verbose log file to write the test execution results to an
    # Excel file in a more readable format if need be.
    processResults()

    sys.exit("SIGINT")


def processResults():

    # Process the verbose log file to write the test execution results to an
    # Excel file in a more readable format if need be.
    # We only generate an output Excel file if we are executing test scripts inside
    # a batch file ('-t b' option).
    if (Program.generateOutputExcelFile):
        try:
            ResultProcessor.ProcessResults(UtilLogger.verboseCompleteFileName, \
                                           Program.outputCompleteFileName)
        except AssertionError, ex:
            print("main() - Exception Caught: Invalid input argument for function ProcessResults")
            print("Exception Message: {}\n".format(ex))
        except BaseException, ex:
            print("main() - Caught an exception while processing the test execution results in the log file")
            print("Exception Message: {}\n".format(ex))
        else:
            print
            print("Excel Output File is under: {}".format(Program.outputCompleteFileName))


def main():

    # Trap on SIGINTs
    signal.signal(signal.SIGINT, signalHandler)

    # parse arguments
    parser = CliParser.initParser()

    # run program
    Program.Run(parser)

    # Process the verbose log file to write the test execution results to an
    # Excel file in a more readable format if need be.
    processResults()

    return

if __name__ == '__main__':main()
