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


"""
Process all data in Verbose log file generated from running OneBMCTest tool to execute
a list of test scripts in a batch file ('-t b' option).
"""


# Built-in python modules.
import xlsxwriter
import types
import datetime
import os
import sys
import re


# Global (module-scope) variable.
InvCycNum = "Invalid Cycle Number!"

reload(sys)  # In order to restore deleted attribute 'setdefaultencoding'
sys.setdefaultencoding('utf_8')  # Set character encoding to UTF-8.


"""
Method that processes verbose test results log and writes the output to
an Excel file in a more readable format.
The verbose log file is generated by running PyTestToolUtil to execute
a list of test scripts inside a batch file ('-t b' option).

Input Parameters:
    verbFilePath:
        Verbose complete file name including full directory path, file name
        and extension.
    outputFilePath:
        Output Excel complete file name including full directory path, file
        name and extension.
"""
def ProcessResults(verbFilePath, outputFilePath):
    
    # Validate input parameters.
    assert(verbFilePath != None)
    assert(outputFilePath != None)
    assert(os.path.isfile(verbFilePath))
    
    # Declare global (module-scope) variable.
    global InvCycNum

    # From Verbose log file.
    verbCycles = None  # Dictionay: key = cycle #; value = List: [cycle start time in seconds, isCycleOK],
                       #                                   where isCycleOk is a boolean indicating that cycle
                       #                                   is ok (True), or cycle has some errors (False).
    verbTests = None  # List: List Element = tuple (TestName, ResultList) \
                      # ResultList: [i'th list element = tuple (Pass/Fail during cycle i, 
                      #              list of log messages for test)].
   
    # Parse Verbose log file.
    try:
        verbCycles, verbTests = ParseVerbLog(verbFilePath)
    except AssertionError, ex:
        print("ProcessResults() - Exception Caught: Invalid input argument for function ParseVerbLog")
        print("Exception Message: {}\n".format(ex))
        raise
    except InvCycNum, ex:
        print("ProcessResults() - Exception Caught: " + InvCycNum)
        print("Cycle Number: {}\n".format(ex))
        raise
    except BaseException, ex:
        print("ProcessResults() - Caught an exception while parsing the input verbose log file")
        print("Exception Message: {}\n".format(ex))
        raise

    # Write final data processed to output .xlsx Excel file.
    try:
        WriteOutputToExcel(verbCycles, verbTests, outputFilePath)
    except AssertionError, ex:
        print("ProcessResults() - Exception Caught: Invalid input argument(s) for function WriteOutputToExcel")
        print("Exception Message: {}\n".format(ex))
        raise
    except BaseException, ex:
        print("ProcessResults() - Caught an exception while writing output result to output Excel file")
        print("Exception Message: {}\n".format(ex))
        raise


"""
Parse Verbose log file and store data in convenient data structures.
The verbose log file is generated by running PyTestToolUtil to execute
a list of test scripts inside a batch file ('-t b' option).

Input Parameters:
    verbFilePath: Complete path (directory + file name) of log file.
                  The log file could have the new format (each line
                  in the file starts with a time stamp) or the old
                  format (lines don't start with a time stamp).
Return Values:
    verbCycles:   Dictionay: key = cycle #; value = List: [cycle start time in seconds, isCycleOK],
                                            where isCycleOk is a boolean indicating that cycle
                                            is ok (True), or cycle has some errors (False).
    verbTests:    List: List Element = tuple (TestName, ResultList) \
                        ResultList = List: [i'th list element = tuple (Pass/Fail during cycle i,
                                     list of log messages for test)].
Assumption:
                  The first line in all log files with old format either is a blank line,
                  or it starts with character '-'.
                  The first line in all log files with new format starts with a time stamp.
"""
def ParseVerbLog(verbFilePath):

    # Validate input parameter.
    assert(verbFilePath != None)
    assert(type(verbFilePath) is types.StringType)

    # Declare global (module-scope) variable.
    global InvCycNum

    verbCycles = {}
    verbTests = []

    cycleNum = None  # Cycle number we are processsing.
    testNum = None  # Test number we are processing within a cycle.

    with open(verbFilePath, 'r') as verbFile:  # Verbose log file object.

        # Loop through all lines in file.
        logText = []  # List of log messages for one test execution.
        lineNum = 0  # Current line number in input verbose file being read.
        newFileFormat = True  # Flag indicating whether the input file has the
                              # new format (True) or the old one (False).
        for line in verbFile:

            lineNum += 1
            line2 = line.strip('\n')  # Remove newline character at end.

            if (lineNum == 1):  # First line in input log file.
                if (line.isspace() or line.startswith("-")):
                    newFileFormat = False

            # If input file has new format, each line contains extra strings because of
            # the time stamp at the beginning of the line (compared to lines in files
            # with old format).
            extra = 3  # 3 is the number of additional strings (non blank) at the beginning
                       # of all lines in input files with new format (compared to lines in
                       # input files with old format).
            if not newFileFormat:
                extra = 0
                
            # Is this a start of a new cycle?
            if ('Starting Test List Cycle' in line):
                # Start of a new cycle.
                testNum = 0  # Number of test execution result to be processed next in this cycle.
                logText = []  # Log text for next test execution result to be processed in this cycle.
                wordList = line.split()
                    
                cycleNum = int(wordList[4 + extra].strip('.'))
                
                # Get the time stamp for the cycle.
                if ('day' in line):  # date/time stamp does contain 'days'.
                    days = int(wordList[7 + extra])  # Number of days.
                    timeStamp = wordList[9 + extra]  # Time stamp.
                    # Parse time stamp.
                    wordList = timeStamp.split(':')
                    hours = int(wordList[0])
                    minutes = int(wordList[1])
                    seconds = float(wordList[2])                    
                else:  # date/time stamp does not contain 'days'.
                    days = 0
                    timeStamp = wordList[7 + extra]  # Time stamp.
                    # Parse time stamp.
                    wordList = timeStamp.split(':')
                    hours = int(wordList[0])
                    minutes = int(wordList[1])
                    seconds = float(wordList[2])
                # Time stamp for the cycle.
                timeInSecs = (days*24*60*60) + (hours*60*60) + (minutes*60) + seconds

                # Update verbCycles dictionary.
                if cycleNum not in verbCycles:
                    verbCycles[cycleNum] = [timeInSecs, True]
                else:  # Invalid cycle number.
                    raise InvCycNum, cycleNum

            # Is this the end of a test execution result?            
            elif (line2.endswith('PASSED') or line2.endswith('FAILED')):
                # End of a test execution result.

                # Get test name and test result (Pass/Fail).
                wordList = line.split()
                testName = wordList[0 + extra]
                testResult = wordList[1 + extra]

                # Update verbTests list.
                if (cycleNum == 0):  # First cycle.                    
                    resultList = [(testResult,logText)]
                    couple = (testName, resultList)
                    verbTests.append(couple)
                else:  # Not first cycle.
                    # sumTests already has all test executions for at least 1 cycle. 
                    # Add another result for this test execution for this cycle.
                    testCount = len(verbTests)  # Total number of test executions per cycle.
                    if (testNum < testCount):
                        expectedTestName = verbTests[testNum][0]  # Expected test name for this
                                                                  # test execution.
                    # Do some validations.
                    if (testNum >= testCount):  # Invalid test number.
                        verbCycles[cycleNum][1] = False  # Mark this cycle as erroneous.
                        print("ParseVerbLog(): Invalid number of test executions for cycle {}\n".format(cycleNum))
                    elif (testName != expectedTestName):  # Wrong test script name.
                        verbCycles[cycleNum][1] = False  # Mark this cycle as erroneous.
                        verbTests[testNum][1].append(("Error", ""))  # No test result or log text for this test execution.
                                                                     # Hence add a dummy test result and log text for this test execution.
                        print("ParseVerbLog(): Invalid test name for cycle number {}".format(cycleNum))
                        print("Actual test name: {}. Expected test name: {}\n".format(testName, expectedTestName))
                    else:
                        verbTests[testNum][1].append((testResult,logText))

                testNum += 1  # Number of test execution result (if any) to be processed next in this cycle.
                logText = []  # Reset log text for next test execution result to be processed in this cycle.
                
            else:  # This is a test execution result (either start, or during, but not end of result).
                # Update log text for this execution.
                logText.append(line)

    return verbCycles, verbTests


"""
Write final data processed to the output excel file.

Input Parameters:
    verbCycles: Dictionary containing information regarding execution cycles.
                Dictionay: key = cycle #; value = List: [cycle start time in seconds, isCycleOK],
                                          where isCycleOk is a boolean indicating that cycle
                                          is ok (True), or cycle has some errors (False).
    verbTests = List containing information regarding test execution results.
                List: List Element = tuple (TestName, ResultList)
                      ResultList: [i'th list element = tuple (Pass/Fail during cycle i,
                                   list of log messages for test)].
"""
def WriteOutputToExcel(verbCycles, verbTests, outputFilePath):

    # Validate input parameters.
    assert ((verbCycles != None) and (verbTests != None) and (outputFilePath != None))
    assert(type(verbCycles) is types.DictionaryType)
    assert(type(verbTests) is types.ListType)
    assert (type(outputFilePath) is types.StringType)

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(outputFilePath)
    worksheet = workbook.add_worksheet()

    # Create format objects.
    headerFormat = workbook.add_format({'bold': True})
    headerItalicFormat = workbook.add_format({'bold': True, 'italic': True})
    passFormat = workbook.add_format({'font_color': 'green', 'bg_color': '#98FB98'})
    failFormat = workbook.add_format({'font_color': 'red', 'bg_color': '#FFC8CB'})
    errorFormat = workbook.add_format({'font_color': 'black', 'bg_color': '#FF8000'})

    rowNum = 0  # Current row number.

    # Write the Cycles row header.
    colNum = 0  # current column number.
    worksheet.write(rowNum, colNum, '')
    colNum += 1
    for key in verbCycles:
        worksheet.write(rowNum, colNum, "Cycle {}".format(key), headerItalicFormat)
        colNum += 1
    rowNum += 1

    # Write the time duration header row.
    colNum = 0  # current column number.
    worksheet.write(rowNum, colNum, 'Time Duration', headerFormat)
    colNum += 1
    cyclesCount = len(verbCycles)
    for i in range(0, cyclesCount):
        if (i < cyclesCount-1):
            duration = verbCycles[i+1][0]-verbCycles[i][0]  # In seconds.
            timeStamp = datetime.timedelta(seconds=duration)
            worksheet.write(rowNum, colNum, timeStamp, headerFormat)
        else:
            worksheet.write(rowNum, colNum, "???", headerFormat)
        colNum += 1
    rowNum += 1

    # Write test execution results to output Excel file.
    for test in verbTests:
        # Write a test execution result row.
        # Add test name in row.
        colNum = 0  # current column number.
        worksheet.write(rowNum, colNum, test[0])
        colNum += 1
        resultList = test[1]
        # Add test results to row.
        # If a test execution contains a failure, we need to write
        # the log message corresponding to that failure as a comment
        # for the corresponding cell that contains 'FAILED'.
        # Note that the log message is filtered so that only lines 
        # that contain the substring 'failed' are kept (in case none
        # of the lines contain substring 'failed', in which case the
        # filtered log message becomes empty, then we do not do the
        # filtering.
        cycleNum = -1  # Initialize current cycle number.
        for testResult in resultList:
            cycleNum += 1  # Current cycle number.
            # Check for erroneous cycle.
            if (not verbCycles[cycleNum][1]):  # Erroneous cycle.
                worksheet.write(rowNum, colNum, 'ERROR', errorFormat)
                colNum += 1
                continue  # Skip to next test execution result.
            passFail = testResult[0]
            if (passFail == 'PASSED'):
                worksheet.write(rowNum, colNum, passFail, passFormat)
            else:  # 'FAILED'
                worksheet.write(rowNum, colNum, passFail, failFormat)

                # Add comment to cell.
                logMsg = testResult[1]
                try:
                    filtLogMsg = FilterLogMsg(logMsg, 'failed').strip()  # Filtered log message.
                except AssertionError, ex:
                    print("WriteOutputToExcel() - Exception Caught: Invalid input argument(s) for function FilterLogMsg")
                    print("Exception Message: {}\n".format(ex))
                    return
                except BaseException, ex:
                    print("WriteOutputToExcel() - Caught an exception while filtering a log message")
                    print("Exception Message: {}\n".format(ex))
                    return
                if (filtLogMsg != ''):  # Filtered log message is not empty.
                    msg = filtLogMsg  # Hence use it.
                else:  # Filtered log message is empty.
                    try:
                        msg = FilterLogMsg(logMsg, '\n')  # Hence use original log message (converted
                                                          # from list of strings to a string).
                    except AssertionError, ex:
                        print("WriteOutputToExcel() - Exception Caught: Invalid input argument(s) for function FilterLogMsg")
                        print("Exception Message: {}\n".format(ex))
                        return
                    except BaseException, ex:
                        print("WriteOutputToExcel() - Caught an exception while filtering a log message")
                        print("Exception Message: {}\n".format(ex))
                        return
                # Comments written to cells in Excel files are actually written to an XML file under
                # the hood. Hence we need to remove all characters that are illegal in XML from
                # the comment to be written to the cell.
                try:
                    filMsg = RemoveIllegalChars(msg)
                except AssertionError, ex:
                    print("WriteOutputToExcel() - Exception Caught: Invalid input argument(s) for function RemoveIllegalChars")
                    print("Exception Message: {}\n".format(ex))
                    return
                except BaseException, ex:
                    print("WriteOutputToExcel() - Caught an exception while removing illegal characters from comment")
                    print("Exception Message: {}\n".format(ex))
                    return
                worksheet.write_comment(rowNum, colNum, filMsg, \
                                        {'x_scale': 15, 'y_scale': 15})
            colNum += 1

        rowNum += 1

    workbook.close()


"""
Input Parameters:
    logMsgsList: A list of lines (strings ending with newline (\n)).
    keepString: a string.
Return Value:
    A text string consisting of all lines in logMsgList that contain the substring
    keepString, concatenated (in their order in logMsgList).
"""
def FilterLogMsg(logMsgsList, keepString):
    
    # Validate inputs.
    assert((logMsgsList != None) and (keepString != None))
    assert(type(logMsgsList) is types.ListType)
    assert(type(keepString) is types.StringType)

    textLog = ''
    for line in logMsgsList:
        if (keepString in line):
            textLog += line

    return textLog


"""
Given an input string, this method removes all characters that are illegal in XML
from the string, and replaces them with the substring 'REMOVED-ILLEGAL-CHAR'.
The resulting string is returned.

Input Parameters:
    text: the input string to clean up from illegal characters.
"""
def RemoveIllegalChars(text):

    # Validate input.
    assert(text != None)
    assert(type(text) is types.StringType)

    charsToRemove = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
    filteredText = charsToRemove.sub(' REMOVED-ILLEGAL-CHAR ', text)

    return filteredText