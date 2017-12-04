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

import os
import pkgutil
import time
import datetime

import Config
import Email
import IpmiUtil
import UtilLogger
import XmlParser
import ResultProcessor

bmcVersion=None
bmcPlatform=None
email=None
sender=None
senderPwd=None
server=None
port=None

# Output Excel complete file name including full directory path, file name and extension.
outputCompleteFileName = None

# Flag indicating whether to generate the output Excel file (True) or not (False).
# We only generate an output Excel file if we are executing test scripts inside
# a batch file ('-t b' option).
generateOutputExcelFile = False

# Function determines program
# action based on CLI arguments
def Run(parser):

    # Declare module-scope variables
    global bmcPlatform
    global bmcVersion
    global email
    global sender
    global senderPwd
    global server
    global port
    global outputCompleteFileName
    global generateOutputExcelFile

    # parse CLI arguments
    parsedArgs = parser.parse_args()

     # Get output Excel file name.
    if (parsedArgs.excelOutput != None):  # User provided output Excel file name as a
                                          # command line argument.
        outputFileName = parsedArgs.excelOutput  # Use name provided by user.
    else:  # No output Excel file name was provided.
        outputFileName = Config.defaultOutputExcelFile  # Use default name.

    outputCompleteFileName = Config.outputDirectoryPath + outputFileName \
                             + Config.outputExcelFileExtension

    # If a verbose input log file name was provided as a command line argument,
    # then all we do is process the log file to generate the output Excel file.
    if (parsedArgs.excelInput):  # Input verbose log file was provided as a
                                 # command line argument.
        try:
            ResultProcessor.ProcessResults(parsedArgs.excelInput, \
                                           outputCompleteFileName)
        except AssertionError, ex:
            print("Run() - Exception Caught: Invalid input argument for function ProcessResults")
            print("Exception Message: {}\n".format(ex))
        except BaseException, ex:
            print("Run() - Caught an exception while processing the test execution results in the log file")
            print("Exception Message: {}\n".format(ex))
        else:
            print
            print("Excel Output File is under: {}".format(outputCompleteFileName))

        return  # No need to do anything other than process input verbose log file and
                # generate the output Excel file.

    # Get and format timestamp
    timeInSecs = time.time()
    timeStamp = datetime.datetime.fromtimestamp(timeInSecs).strftime(\
        '%Y-%m-%d %I:%M:%S')

    # Check for BMC Platform
    if parsedArgs.platform == Config.bmcPlatformC2010Value:
        import C2010TestScripts as bmcPlatform
        Config.bmcPlatform = Config.bmcPlatformC2010Value
    elif parsedArgs.platform == Config.bmcPlatformJ2010Value:
        import J2010TestScripts as bmcPlatform
        Config.bmcPlatform = Config.bmcPlatformJ2010Value
    elif parsedArgs.platform == Config.bmcPlatformG50Value:
        import G50TestScripts as bmcPlatform
        Config.bmcPlatform = Config.bmcPlatformG50Value
    else: # default
        import C2010TestScripts as bmcPlatform
        Config.bmcPlatform = Config.bmcPlatformC2010Value

    # Check for renaming verbose log file
    if parsedArgs.verbosename:
        Config.verboseLogFileName = str(parsedArgs.verbosename)

    # Check for Timestamp switch
    if parsedArgs.timestamp:
        Config.timestampEn = True

    # Initialize Logging
    UtilLogger.InitLogging(timeInSecs)

    # Update the output Excel file name to include the time stamp, in order
    # to be consistent with the verbose log file naming.
    outputCompleteFileName = Config.outputDirectoryPath + outputFileName \
                             + UtilLogger.fileTimeStamp + \
                             Config.outputExcelFileExtension

    # log and print header
    UtilLogger.summaryLogger.info('')
    UtilLogger.summaryLogger.info('-------------- OneBMCTest Utility v' + Config.utilVersion + ' --------------')
    UtilLogger.summaryLogger.info('---------------- ' + timeStamp + ' -----------------')
    UtilLogger.summaryLogger.info('')

    # Set the current OS
    Config.currentOs = os.name

    # Check for enabling verboseLogger to output to console
    if parsedArgs.showverbose:
        UtilLogger.EnableShowVerbose()

    # Check for bmc version CLI parameter
    if parsedArgs.version is not None:
        UtilLogger.summaryLogger.info("BMC version being tested is " + parsedArgs.version)
        bmcVersion = parsedArgs.version
        UtilLogger.summaryLogger.info("")

    # Check for Email parameter
    if parsedArgs.email is not None and \
        parsedArgs.sender is not None and \
        parsedArgs.senderpwd is not None and \
        parsedArgs.server is not None and \
        parsedArgs.port is not None:
        UtilLogger.consoleLogger.info("Results will be emailed to: " + parsedArgs.email)
        email = parsedArgs.email
        sender = parsedArgs.sender
        senderPwd = parsedArgs.senderpwd
        server = parsedArgs.server
        port = parsedArgs.port
        UtilLogger.summaryLogger.info("")

    # Check for Debug switch
    if parsedArgs.debug:
        Config.debugEn = True

    # Check for running tests
    # using IPMI over LAN
    if parsedArgs.conn == 'eth' and \
        parsedArgs.ip and parsedArgs.user and \
        parsedArgs.pwd:
            
        # Update config file shared variables
        Config.bmcIpAddress = parsedArgs.ip
        Config.bmcUser = parsedArgs.user
        Config.bmcPassword = parsedArgs.pwd
        Config.acPowerIpSwitchIpAddress = parsedArgs.switch        

        # Concatenate input arguments for IpmiUtil
        # that are needed for using the IPMI over LAN+ interface
        interfaceParams = \
            [ Config.ipmiUtilPrivilegeSwitch, \
            Config.ipmiUtilPrivilegeAdminValue, \
            Config.ipmiUtilInterfaceSwitch, \
            Config.ipmiUtilInterfaceLanPlusValue, \
            Config.ipmiUtilIpAddressSwitch, \
            Config.bmcIpAddress, \
            Config.ipmiUtilUserNameSwitch, \
            Config.bmcUser, \
            Config.ipmiUtilPasswordSwitch, \
            Config.bmcPassword]

        # Run all test scripts in <bmcPlatform>TestScripts folder
        if parsedArgs.test == 'a':
            UtilLogger.summaryLogger.info("Running all test scripts using " + "IPMI over LAN+")
            RunAllTestScripts(interfaceParams)

        # Run all tests from test scripts XML file
        # using iterations >= 1 using
        # IPMI over LAN+
        elif parsedArgs.test == 'b' and \
            parsedArgs.xmlfilepath is not None:
            UtilLogger.summaryLogger.info("Running test scripts specified in " + \
                parsedArgs.xmlfilepath + " using IPMI over LAN+")
            generateOutputExcelFile = True
            RunXmlTestScripts(interfaceParams, parsedArgs.xmlfilepath)

        # Check if <testValue> in -test <testValue>
        # is a test script.
        # If so, execute test script
        elif parsedArgs.test is not None and \
            parsedArgs.test != 'a' and \
            parsedArgs.test != 'b':
            UtilLogger.summaryLogger.info("Running test script " + \
                parsedArgs.test + " using IPMI over LAN+")
            RunSingleTestScript(interfaceParams, parsedArgs.test)

        # Print help usage if incorrect arguments passed
        else:
            parser.print_help()

    # Check for running tests
    # in-band in compute server
    elif parsedArgs.conn == 'kcs':

        # Run all test scripts in <bmcPlatform>TestScripts folder
        if parsedArgs.test == 'a':
            UtilLogger.summaryLogger.info("Running all test scripts using " + \
                "KCS")
            RunAllTestScripts([])

        # Run all tests from test scripts XML file
        # with iterations >= 0 using
        # IPMI over LAN+
        elif parsedArgs.test == 'b' and \
            parsedArgs.xmlfilepath is not None:
            UtilLogger.summaryLogger.info("Running test scripts specified in " + \
                parsedArgs.xmlfilepath + " KCS")
            RunXmlTestScripts([], parsedArgs.xmlfilepath)
            generateOutputExcelFile = True

        # Check if <testValue> in -test <testValue>
        # is a test script.
        # If so, execute test script
        elif parsedArgs.test is not None and \
            parsedArgs.test != 'a' and \
            parsedArgs.test != 'b' and \
            parsedArgs.xmlfilepath is None:
            UtilLogger.summaryLogger.info("Running test script " + \
                parsedArgs.test + " using KCS")
            RunSingleTestScript([], parsedArgs.test)

        # Print help usage if incorrect arguments passed
        else:
            parser.print_help()

    # Print help usage if no arguments passed
    else:
        parser.print_help()

    return

# Function checks if specified module in <bmcPlatform>TestScripts package
# exists, and if so, runs the Setup, Execute, and Cleanup 
# functions for the module usnig IPMI over LAN+ or KCS interface
def RunSingleTestScript(interfaceParams, testName):

    # Initialize variables for statistics and summary logging
    totalRun = 0
    totalPassed = 0
    totalFailed = 0
    testScriptExists = False
    startTime = time.time()
        
    # Strip any file extension fromm the testName (i.e. .py)
    (testName, testNameExt) = os.path.splitext(testName)

    # Initialize dictionary of tests that fail
    # and number of iterations where they failed
    statDict = { 'init' : 0 }    
    # Get all modules and look for specified test script         
    for modLoader, modName, isPkg in pkgutil.iter_modules(bmcPlatform.__path__):
        
        # Test failed by default
        testPassOrFail = False           
         
        if modName == testName and not isPkg:             

            testScriptExists = True

            # Use modLoader to find and import module
            module = modLoader.find_module(modName).load_module(modName)
        
            # Add new line to logging
            UtilLogger.verboseLogger.info("")

            # Run Setup Function in TestScript module
            UtilLogger.verboseLogger.info("Running Setup for test " + str(modName))
            testPassOrFail = module.Setup(interfaceParams)

            # Run Execute Function in TestScript module
            if testPassOrFail:
                UtilLogger.verboseLogger.info("Running Execute for test " + \
                    str(modName))
                testPassOrFail &= module.Execute(interfaceParams)

            # Run Cleanup Function in TestScript module
            UtilLogger.verboseLogger.info("Running Cleanup for test " + \
                str(modName))
            module.Cleanup(interfaceParams)

            # Increment statistics and log if test passed or failed
            if testPassOrFail:
                UtilLogger.summaryLogger.info(str(modName) + " PASSED")
                totalPassed += 1
            else:
                UtilLogger.summaryLogger.info(str(modName) + " FAILED")
                totalFailed += 1

                # Append failed test to statDict
                statDict[str(modName)] = 1
            
            totalRun += 1
            break

    # Check if test script was found and run
    if not testScriptExists:
        UtilLogger.summaryLogger.error("Test Script " + \
            testName + " could not be loaded and was not run.")

    # Log Summary and Statistics
    testDuration = datetime.timedelta(seconds=time.time() - startTime)
    LogSummaryStatistics(totalRun, totalPassed, totalFailed, statDict, testDuration)

    # Email Results
    if email is not None:
        UtilLogger.consoleLogger.info("Emailing results to " + email)
        
        # Generate email message body
        emailBody = \
            'Hi,\n\n' + \
            'The below results summarizes the test run on BMC ' + \
            bmcVersion + \
            ' using Python Test Utility v' + Config.utilVersion + '.\n\n' + \
            'Full results can be viewed in the attached verbose logs file.\n\n'

        # Append summary results to 
        fp = open(\
            Config.summaryLogPath + \
            Config.summaryLogFileName + \
            Config.summaryLogFileExtension, 'rb')
        summaryResults = fp.read()
        fp.close()
        emailBody += summaryResults

        if EmailResults(email, sender, senderPwd, server, \
            port, bmcVersion, emailBody):
            UtilLogger.consoleLogger.info("Successfully emailed results")
        else:
            UtilLogger.summaryLogger.info("Failed to email results")
        UtilLogger.summaryLogger.info("")

    return

# Function finds all modules in <bmcPlatform>TestScripts package and
# runs the Setup, Execute, and Cleanup functions for 
# every module using IPMI over LAN+ or KCS interface
def RunAllTestScripts(interfaceParams):

    # Initialize variables for statistics and summary logging
    totalRun = 0
    totalPassed = 0
    totalFailed = 0
    startTime = time.time()

    # Initialize dictionary of tests that fail
    # and number of iterations where they failed
    statDict = { 'init' : 0 }

    # Get all modules and iterate through each
    for modLoader, modName, isPkg in pkgutil.iter_modules(bmcPlatform.__path__):

        # Verify module is not package
        if not isPkg:

            # Test failed by default
            testPassOrFail = False

            # Use modLoader to find and import module
            module = modLoader.find_module(modName).load_module(modName)
        
            # Add new line to logging
            UtilLogger.verboseLogger.info("")

            # Run Setup Function in TestScript module
            UtilLogger.verboseLogger.info("Running Setup for test " + str(modName))
            testPassOrFail = module.Setup(interfaceParams)

            # Run Execute Function in TestScript module
            if testPassOrFail:
                UtilLogger.verboseLogger.info("Running Execute for test " + \
                    str(modName))
                testPassOrFail &= module.Execute(interfaceParams)

            # Run Cleanup Function in TestScript module
            UtilLogger.verboseLogger.info("Running Cleanup for test " + \
                str(modName))
            module.Cleanup(interfaceParams)

            # Increment statistics and log if test passed or failed
            if testPassOrFail:
                UtilLogger.summaryLogger.info(str(modName) + " PASSED")
                totalPassed += 1
            else:
                UtilLogger.summaryLogger.info(str(modName) + " FAILED")
                totalFailed += 1

                # Append failed test to statDict
                statDict[str(modName)] = 1
            totalRun += 1

    # Log Summary and Statistics
    testDuration = datetime.timedelta(seconds=time.time() - startTime)
    LogSummaryStatistics(totalRun, totalPassed, totalFailed, statDict, testDuration)

    # Email Results
    if email is not None:
        UtilLogger.consoleLogger.info("Emailing results to " + email)
        
        # Generate email message body
        emailBody = \
            'Hi,\n\n' + \
            'The below results summarizes the test run on BMC ' + \
            bmcVersion + \
            ' using Python Test Utility v' + Config.utilVersion + '.\n\n' + \
            'Full results can be viewed in the attached verbose logs file.\n\n'

        # Append summary results to 
        fp = open(\
            Config.summaryLogPath + \
            Config.summaryLogFileName + \
            Config.summaryLogFileExtension, 'rb')
        summaryResults = fp.read()
        fp.close()
        emailBody += summaryResults

        if EmailResults(email, sender, senderPwd, server, \
            port, bmcVersion, emailBody):
            UtilLogger.consoleLogger.info("Successfully emailed results")
        else:
            UtilLogger.summaryLogger.info("Failed to email results")
        UtilLogger.summaryLogger.info("")

    return

# Function will run all functional tests
# with iterations >= 1 in test scripts XML file
# using IPMI over LAN+ or KCS interface
def RunXmlTestScripts(interfaceParams, xmlFilePath):

    # Get all modules in <bmcPlatform>TestScripts folder and append to dictionary
    modDict = { 'init' : [ True, True ] }
    modLoaderIdx = 0
    isPkgIdx = 1
    for modLoader, modName, isPkg in pkgutil.iter_modules(bmcPlatform.__path__):
        modDict[str(modName)] = [ modLoader, isPkg ]

    # Initialize variables for statistics and summary logging
    totalRun = 0
    totalPassed = 0
    totalFailed = 0

    # Initialize dictionary of tests that fail
    # and number of iterations where they failed
    statDict = { 'init' : 0 }

    # Instantiate Xml Parser class
    xmlParserObj = XmlParser.XmlParser(xmlFilePath)
    if not xmlParserObj.root:
        UtilLogger.verboseLogger.error("RunXmlTestScripts: failed to parse Xml file." \
            + " Will not execute test scripts.")
        return

    # Convert duration attribute in Xml testlist element
    # to seconds
    totalSeconds = ConvertDuration2Seconds(\
        xmlParserObj.root.attrib["duration"])

    # Loop testlist until either totalSeconds or
    # testListIterations has elapsed
    startTime = time.time()
    totalTestTime = startTime + totalSeconds
    testListCycles = xmlParserObj.root.attrib["iterations"]
    if not testListCycles.isdigit():
        testListCycles = 1
    elif testListCycles < 0:
        testListCycles = 1
    else:
        testListCycles = int(testListCycles)
    stopOnAnyTestFail = False
    try:
        stopOnAnyTestFail = \
            True if int(xmlParserObj.root.attrib["stopOnFail"]) == 1 else False
    except Exception, stopOnFailXmLException:
        UtilLogger.verboseLogger.error(\
            "RunXmlTestScripts: failed to parse stopOnFail " + \
            " element in XML. Setting to False. Exception: " + \
            str(stopOnFailXmLException))

    # Loop testlist
    testListCurrCycle = 0
    stopTest = False
    while time.time() < totalTestTime or \
        testListCurrCycle < testListCycles:

        # Determine if program stopping test execution
        # Due to stopOnFail
        if stopTest:
            break

        # Initialize variables for summary
        # and statistics logging 
        cycleStartTime = time.time()
        totalRunInCycle = 0
        totalPassedInCycle = 0
        totalFailedInCycle = 0
        statDictInCycle = { 'init' : 0 }

        # Insert Test List cycle and duration
        UtilLogger.summaryLogger.info("")
        UtilLogger.summaryLogger.info(\
            "Starting Test List Cycle " + \
            str(testListCurrCycle) + \
            ". Elapsed time: " + \
            str(datetime.timedelta(\
            seconds=time.time() - startTime)))

        # Parse xml file and for each element,
        # check if test module should be executed.
        # If so, find and load module
        # and execute Setup, Execute, Cleanup functions
        for test in xmlParserObj.root:
            testName = test.attrib["name"]

            # Determine if program stopping test execution
            # Due to stopOnFail
            if stopTest:
                break

            try:

                # Get number of iterations
                iterationCount = int(test.attrib["iterations"])
                if iterationCount < 0:
                    iterationCount = 0
                stopOnTestFail = False
                try:
                    stopOnTestFail = \
                        True if int(test.attrib["stopOnFail"]) == 1 else False
                except Exception, stopOnFailXmLException:
                    UtilLogger.verboseLogger.error(\
                        "RunXmlTestScripts: failed to parse stopOnFail " \
                        + " element in XML. Setting to False. Exception: " \
                        + str(stopOnFailXmLException))
                
                # Check if package
                if not modDict[testName][isPkgIdx]:

                    # Call module functions iterationCount times
                    for i in range(0,iterationCount): 

                        # Test failed by default
                        testPassOrFail = False

                        # Find and Load module
                        module = modDict[testName][modLoaderIdx]\
                            .find_module(testName).load_module(testName)

                        # Add new line to logging
                        UtilLogger.verboseLogger.info("")

                        # Delay test execution based on delay
                        # xml test element
                        testDelay = test.attrib["delay"]
                        if testDelay.isdigit() and \
                            int(testDelay) > 0:
                            UtilLogger.verboseLogger.info("Delaying test " + \
                                "execution for " + str(int(testDelay)) + " seconds..")
                            time.sleep(int(testDelay))

                        # Run Setup Function in TestScript module
                        UtilLogger.verboseLogger.info("Running Setup for test " \
                            + str(testName))
                        testPassOrFail = module.Setup(interfaceParams)

                        # Run Execute Function in TestScript module
                        if testPassOrFail:
                            UtilLogger.verboseLogger.info("Running Execute for test " \
                                + str(testName))
                            testPassOrFail &= module.Execute(interfaceParams)

                        # Determine if to stop testing based on Execute() failure
                        # Feature enabled if stopOnTestFail or stopOnAnyTestFail is true
                        if not testPassOrFail and (stopOnAnyTestFail or stopOnTestFail):
                            UtilLogger.verboseLogger.error(\
                                "Stopping Test Execution. Execute " + \
                                " for test " + str(testName) + " failed.")
                            stopTest = True
                            break

                        # Run Cleanup Function in TestScript module                          
                        UtilLogger.verboseLogger.info("Running Cleanup for test " \
                            + str(testName))
                        module.Cleanup(interfaceParams)

                        # Increment statistics and log if test passed or failed
                        if testPassOrFail:
                            UtilLogger.summaryLogger.info(str(testName) + " PASSED")
                            totalPassed += 1
                            totalPassedInCycle += 1
                        else:
                            UtilLogger.summaryLogger.info(str(testName) + " FAILED")
                            totalFailed += 1
                            totalFailedInCycle += 1

                            # Check if failed test already exists in dictionary
                            if str(testName) in statDict:
                                statDict[str(testName)] += 1
                            # Else, append failed test to dictionary
                            else:
                                statDict[str(testName)] = 1

                            # Check if failed test already exists in cycle dictionary
                            if str(testName) in statDictInCycle:
                                statDictInCycle[str(testName)] += 1
                            # Else, append failed test to cycle dictionary
                            else:
                                statDictInCycle[str(testName)] = 1

                        # Increment total tests run
                        totalRunInCycle = totalPassedInCycle + totalFailedInCycle
                        totalRun = totalPassed + totalFailed

            except Exception, e:
                UtilLogger.verboseLogger.error("RunXmlTestScripts: test " \
                    + testName + " failed with exception: " + str(e))

        # Log Summary and Statistics for Cycle
        testCycleDuration = datetime.timedelta(seconds=time.time() - cycleStartTime)
        LogCycleSummaryStatistics(testListCurrCycle, totalRunInCycle, \
            totalPassedInCycle, totalFailedInCycle, statDictInCycle, \
            testCycleDuration)

        # Increment test cycle index
        testListCurrCycle += 1

    # Log Summary and Statistics
    testDuration = datetime.timedelta(seconds=time.time() - startTime)
    LogSummaryStatistics(totalRun, totalPassed, totalFailed, statDict, testDuration)

    # Email Results
    if email is not None:
        UtilLogger.consoleLogger.info("Emailing results to " + email)
        
        # Generate email message body
        emailBody = \
            'Hi,\n\n' + \
            'The below results summarize the tests run on BMC ' + \
            bmcVersion + \
            ' using Python Test Utility v' + Config.utilVersion + '.\n\n' + \
            'Full results can be viewed in the attached verbose logs file.\n\n'

        # Append summary results to 
        fp = open(\
            Config.summaryLogPath + \
            Config.summaryLogFileName + \
            Config.summaryLogFileExtension, 'rb')
        summaryResults = fp.read()
        fp.close()
        emailBody += summaryResults

        if EmailResults(email, sender, senderPwd, server, \
            port, bmcVersion, emailBody):
            UtilLogger.consoleLogger.info("Successfully emailed results")
        else:
            UtilLogger.summaryLogger.info("Failed to email results")
        UtilLogger.summaryLogger.info("")

    return

# Function will log summary statistics for a single test cycle
def LogCycleSummaryStatistics(cycleIdx, totalRun, totalPassed, totalFailed, \
    statDict, duration):

    UtilLogger.summaryLogger.info("")

    #  Log summary
    UtilLogger.summaryLogger.info("SUMMARY for Test Cycle " + \
       str(cycleIdx) + " - Total Passed: " + \
        str(totalPassed) + \
        " Total Failed: " + str(totalFailed) + \
        " Total Run: " + str(totalRun) + \
        " Test Duration: " + str(duration))

    # Log tests that failed
    if totalFailed > 0:
        UtilLogger.summaryLogger.info(\
            "===========================================")
        for failedTest, failedCount in statDict.iteritems():
            if failedTest is not 'init':
                UtilLogger.summaryLogger.info(failedTest + ": Failed " + \
                    str(failedCount) + " times")

    UtilLogger.summaryLogger.info("")

    return

# Function will log summary statistics
def LogSummaryStatistics(totalRun, totalPassed, totalFailed, statDict, duration):

    UtilLogger.summaryLogger.info("")
    UtilLogger.summaryLogger.info("")

    #  Log summary
    UtilLogger.summaryLogger.info("SUMMARY - Total Passed: " + \
        str(totalPassed) + \
        " Total Failed: " + str(totalFailed) + \
        " Total Run: " + str(totalRun) + \
        " Test Duration: " + str(duration))

    # Log tests that failed
    if totalFailed > 0:
        UtilLogger.summaryLogger.info(\
            "===========================================")
        for failedTest, failedCount in statDict.iteritems():
            if failedTest is not 'init':
                UtilLogger.summaryLogger.info(failedTest + ": Failed " + \
                    str(failedCount) + " times")

    UtilLogger.consoleLogger.info("")
    UtilLogger.consoleLogger.info("View summary results at " + \
        Config.summaryLogPath + Config.summaryLogFileName + \
        Config.summaryLogFileExtension)
    UtilLogger.consoleLogger.info("View full results at " + \
        Config.verboseLogPath + Config.verboseLogFileName + \
        Config.verboseLogFileExtension)
    UtilLogger.consoleLogger.info("")

    return

# Function will attempt to email results
def EmailResults(email, sender, senderPwd, server, port, bmcVersion='', emailBody=''):

    sendPassOrFail = Email.send_mail(sender, senderPwd, [ email ], \
        'OneBMCTest BMC ' + bmcVersion + ' Results', emailBody, [ \
        Config.verboseLogPath + Config.verboseLogFileName + \
        Config.verboseLogFileExtension ], server, int(port))

    return sendPassOrFail

# Parse test list duration and convert to seconds
def ConvertDuration2Seconds(duration):

    # Initialize variables
    totalSeconds = -1

    # Convert duration to hours:minutes:seconds
    # then compute totalseconds
    try:
        # Duration syntax - hours:minutes:seconds
        splitDuration = duration.split(":")
        hours = int(splitDuration[0])
        minutes = int(splitDuration[1])
        seconds = int(splitDuration[2])
        totalSeconds = hours*60*60 + minutes*60 + seconds
    # Duration is not a valid value, use default value (-1)
    except Exception:
        totalSeconds = -1

    return totalSeconds
