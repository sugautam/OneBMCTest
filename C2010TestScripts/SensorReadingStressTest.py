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
Test Description:
        Given an XML file containing a list of sensors to monitor.
        Each entry in the XML file consists of information about 1 sensor: sensor name, nominal
        value of the sensor and a tolerance.
        The nominal value is the expected value of the sensor.
        The tolerance is a +/- percentage value used to determine the range of acceptable values of
        the sensor. For instance if the tolerance is 10, then the range of acceptable values is
        [(<nominal value> - 10% <nominal value>) To (<nominal value> + 10% <nominal value>)].

        This test monitors each sensor listed in the XML file to verify whether it is within the
        acceptable range of values for that sensor.
        We monitor the sensors for a configurable duration of time (Config.sensorReadingTestDuration).

        For each sensor, we get the minimum, maximum and average of all sensor readings during the 
        test duration. We also get the number of times the sensor reading passed (i.e. within
        acceptable range of values) and the number of times the sensor reading failed.

        The test passes if and only if ALL sensor readings for all sensors pass (i.e. within
        acceptable range of values).
"""


# Built-in Modules.
import os
import time

# Project Modules.
import Config
import IpmiUtil
import UtilLogger
import XmlParser


# Global variables.
sensorList = []  # List containing information about each sensor to monitor.
                 # Each element in the list is a tuple =
                 # (sensorName, sensorId, nominalValue, tolerance),
                 # where sensorName and sensorId are strings, and
                 # nominalValue and tolerance are floats.


# Setup function.
def Setup(interfaceParams):

    # Declare global (module-scope) variables.
    global sensorList

    # Parse the XML file to get the information regarding the sensors to test.
    # Validate file containing sensors to monitor.
    sensorListFile = Config.sensorListXmlFile  # File containing list of sensors to monitor.
    if (not os.path.isfile(sensorListFile)):
        UtilLogger.verboseLogger.error("SensorReadingStressTest.py: File path " + sensorListFile + " is invalid.")
        return False

    xmlParserObj = XmlParser.XmlParser(sensorListFile)
    if not xmlParserObj.root:
        UtilLogger.verboseLogger.error("SensorReadingStressTest.py - XmlParser: " + \
                                       "failed to parse sensor list XML file.")
        return False

    # Store info regarding all sensors to be monitored in sensorList.
    for sensorEntry in xmlParserObj.root:
        sensorName = sensorEntry.attrib["name"]
        nominalValue = sensorEntry.attrib["nominal"]
        tolerance = sensorEntry.attrib["tolerance"]
        gotSensorIdSuccess, sensorId = IpmiUtil.GetIpmiUtilSensorId(interfaceParams, sensorName)
        if (not gotSensorIdSuccess):
            UtilLogger.verboseLogger.error("SensorReadingStressTest.py - Setup(): " + \
                                       "Failed to get sensor ID for sensor '%s'." % sensorName)
            return False
        sensorList.append((sensorName, sensorId, float(nominalValue), float(tolerance)))

    return True


# Test script execution.
def Execute(interfaceParams):

    # Declare global (module-scope) variables.
    global sensorList

    # Define/Initialize test variables.
    testPassOrFail = True  # Indicates whether test passed (True) or failed (False).
    testDuration = Config.sensorReadingTestDuration
    sensorStatisticsDict = {}  # Dictionary storing statistics regarding 1 sensor.
                               # Key = sensorName, Value = List = [min, max, sum,
                               # passCount, failCount, readSuccess], where:
                               # min = minimum sensor reading value for this sensor,
                               # max = maximum sensor reading value for this sensor,
                               # sum = Summation of all sensor reading values for this sensor,
                               # passCount = number of times sensor reading passes for this sensor,
                               # failCount = number of times sensor reading fails for this sensor,
                               # readSucess = boolean, False if we failed to get a reading for this
                               # sensor at anytime, and True otherwise (i.e. we never failed to get
                               # any reading for this sensor).

    # Initialize sensorStatisticsDict.
    for sensorInfo in sensorList:
        sensorName = sensorInfo[0]
        tmpList = [float("inf"), -float("inf"), 0, 0, 0, True]
        sensorStatisticsDict[sensorName] = tmpList        

    startTime = time.time()  # Start time of sensor readings.
    endTime = startTime + testDuration  # End time of sensor readings.

    # Start sensor readings.
    readingsCount = 0  # Total number of times we got the readins for the sensors (i.e. total number of values read
                       # for each sensor.
    while (time.time() < endTime):

        # Do 1 reading for each sensor in the list.
        readingsCount += 1  # Update number of readings.
        for sensorInfo in sensorList:

            # Get reading for this sensor.
            sensorName = sensorInfo[0]
            sensorId = sensorInfo[1]
            nominalValue = sensorInfo[2]
            tolerance = sensorInfo[3]
            validRangeLow = nominalValue - (float(tolerance)/100) * nominalValue  # Lower bound of valid range.
            validRangeHigh = nominalValue + (float(tolerance)/100) * nominalValue  # Upper bound of valid range.
            sensorReadSuccess, sensorReading = IpmiUtil.GetIpmiUtilSensorReading(interfaceParams, sensorId, sensorName)  # Get 1 sensor reading.
            if (not sensorReadSuccess):
                UtilLogger.verboseLogger.error("SensorReadingStressTest.py - Execute(): " + \
                                       "Failed to get sensor reading for sensor '%s'." % sensorName)
                testPassOrFail = False
                sensorStatisticsDict[sensorName][5] = False
                continue
            sensorStatisticsDict[sensorName][5] = True  #  Got reading for this sensor successfully.
            valid = ((sensorReading >= validRangeLow) and (sensorReading <= validRangeHigh))  # Valid sensor reading?

            # Get current statistics for this sensor.
            curMin = sensorStatisticsDict[sensorName][0]  # Minimum reading value so far.
            curMax = sensorStatisticsDict[sensorName][1]  # Maximum reading value so far.
            curSum = sensorStatisticsDict[sensorName][2]  # Summation of all reading values for far.
            passCount = sensorStatisticsDict[sensorName][3]  # Total number of passed reading values so far.
            failCount = sensorStatisticsDict[sensorName][4]  # Total number of failed reading values so far.

            # Update the statistics for this sensor.
            sensorStatisticsDict[sensorName][0] = min(curMin, sensorReading)
            sensorStatisticsDict[sensorName][1] = max(curMax, sensorReading)
            sensorStatisticsDict[sensorName][2] = curSum + sensorReading
            if (valid):  # Sensor reading within valid range.
                sensorStatisticsDict[sensorName][3] = passCount + 1
            else:  # Sensor reading not within valid range.
                sensorStatisticsDict[sensorName][4] = failCount + 1
                testPassOrFail = False

    # All sensors reading is done and sensor statistics are ready.

    # Log all sensor statistics for each sensor in the list.
    for sensorInfo in sensorStatisticsDict.items():

        # Get sensor statistics for this sensor.
        sensorName = sensorInfo[0]
        sensorStats = sensorInfo[1]  # List of statistics for this sensor.
        readSuccess = sensorStats[5]
        if (not readSuccess):  # Failed to get a reading for this sensor.
            # Log failure for this sensor.
            UtilLogger.verboseLogger.info("")
            UtilLogger.verboseLogger.info("Statistics for Sensor '%s':" % sensorName)
            UtilLogger.verboseLogger.info("Failed to get reading for this sensor")
            continue
        # All readings for this sensor were obtained successfully.
        minReading = sensorStats[0]  # Min value.
        maxReading = sensorStats[1]  # Max value.
        sumReading = sensorStats[2]  # Sum of all reading values.
        passCount = sensorStats[3]  # Total number of passed reading values.
        failCount = sensorStats[4]  # Total number of failed reading values.

        # Log sensor statistics for this sensor.
        UtilLogger.verboseLogger.info("")
        UtilLogger.verboseLogger.info("Statistics for Sensor '%s':" % sensorName)
        UtilLogger.verboseLogger.info("Minimum Value: {}".format(minReading))
        UtilLogger.verboseLogger.info("Maximum Value: {}".format(maxReading))
        UtilLogger.verboseLogger.info("Average Value: {}".format(float(sumReading)/readingsCount))
        UtilLogger.verboseLogger.info("Total number of values within valid range : {}".format(passCount))
        UtilLogger.verboseLogger.info("Total number of values outside valid range : {}".format(failCount))

    UtilLogger.verboseLogger.info("")

    return testPassOrFail


# Cleanup Function.
def Cleanup(interfaceParams):

    return True