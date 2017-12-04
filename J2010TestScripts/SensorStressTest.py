"""
PyTestUtil

Copyright (c) Microsoft Corporation

All rights reserved.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the ""Software""),
to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import RedFish
import UtilLogger
from J2010TestScripts import ConfigJ2010
from Helpers.Connection import Connection
from math import sqrt
from math import pow


# Setup Function
def Setup(interfaceparams):
    return True


# Function will test URI response times and report the average time for each one
def Execute(interfaceparams):

    cmd_pass_or_fail = True
    connection = Connection()
    list_of_sensors = {}
    iteration = 1
    while iteration <= ConfigJ2010.SENSOR_STRESS_SAMPLES:
        cmd_pass_or_fail, response = RedFish.RestApiCall(connection.session, connection.host,
                                                         'redfish/v1/Chassis/System/Sensors', 'GET',
                                                         auth=connection.auth, port=connection.port,
                                                         headers=connection.headers)
        response_json = response.json()
        sensors = response_json.get("Sensors")
        for sensor in sensors:
            sensor_name = sensor.get('Name')
            if sensor.get('Reading') is not None:
                reading = float(str(sensor.get('Reading')))
            else:
                reading = sensor.get('Reading')
            if sensor.get("Name") not in list_of_sensors:
                list_of_sensors[sensor.get("Name")] = [reading]
            else:
                list_of_sensors.get(sensor_name).append(reading)
            if "MaxReadingRange" in sensor:
                max_reading = float(sensor.get('MaxReadingRange'))
                if reading > max_reading:
                    UtilLogger.verboseLogger.error("Failed: Sensor {} has a reading over the max allowed."
                                                   "\n\tMaximum is {} and got {}.".format(sensor_name, max_reading,
                                                                                          reading))
                    cmd_pass_or_fail = False
            if "MinReadingRange" in sensor:
                min_reading = float(sensor.get('MinReadingRange'))
                if reading < min_reading:
                    UtilLogger.verboseLogger.error("Failed: Sensor {} has a reading under the min allowed."
                                                   "\n\tMinimum is {} and got {}.".format(sensor_name, min_reading,
                                                                                          reading))
                    cmd_pass_or_fail = False
            if None in list_of_sensors.get(sensor.get('Name')) and sensor.get('Reading') is not None:
                UtilLogger.verboseLogger.error("The sensor reading for sensor {} captured a reading after having not "
                                               "read something earlier. This may be a problem worth looking into."
                                               .format(sensor_name))
        iteration += 1

    for sensor_results in list_of_sensors:
        total = 0
        average = 0
        deviation_distance = 0
        std_deviation = 0
        results_list = list_of_sensors.get(sensor_results)
        test = results_list.count(None)
        if None in results_list and results_list.count(None) < ConfigJ2010.SENSOR_STRESS_SAMPLES:
            UtilLogger.verboseLogger.error("Sensor {} had some inconsistent results where one or more of the readings "
                                           "had None as the result. The results were:\n\t{}"
                                           .format(sensor_results, results_list))
            cmd_pass_or_fail = False
        elif None in results_list and results_list.count(None) == ConfigJ2010.SENSOR_STRESS_SAMPLES:
            UtilLogger.verboseLogger.info("Sensor {} did not have any results returned for any of the passes"
                                          .format(sensor_results))
        else:
            for result in results_list:
                total += result
            average = total / ConfigJ2010.SENSOR_STRESS_SAMPLES
            # Calculate sum of distances for standard deviation calculation
            for result in results_list:
                deviation_distance += result - average
            std_deviation = sqrt(pow(deviation_distance, 2)/ConfigJ2010.SENSOR_STRESS_SAMPLES)

            UtilLogger.verboseLogger.info("Sensor {} averaged {} with a high of {} and a low of {}. Standard deviation "
                                          "is {}."
                                          .format(sensor_results, average, max(results_list), min(results_list),
                                                  std_deviation))

    return cmd_pass_or_fail


# Prototype Cleanup Function
def Cleanup(interfaceparams):
    return True
