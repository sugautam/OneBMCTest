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

import os
import sys
import Config
import RedFish
import UtilLogger
import base64
import time

# Global variables
testpassorfail = True
elapsedservicetimes = []

# Using a local only config for testing J2010 instead of a global one
services = [{'api': 'GET', 'url': '', 'maxtime': 20},
            {'api': 'GET', 'url': '/$metadata', 'maxtime': 20},
            {'api': 'GET', 'url': '/UpdateService', 'maxtime': 20},
            {'api': 'GET', 'url': '/Chassis', 'maxtime': 20},
            {'api': 'GET', 'url': '/Chassis/System', 'maxtime': 20},
            {'api': 'GET', 'url': '/Chassis/System/Sensors', 'maxtime': 20},
            {'api': 'GET', 'url': '/Chassis/System/FRU', 'maxtime': 20},
            {'api': 'GET', 'url': '/Chassis/System/Thermal', 'maxtime': 20},
            {'api': 'GET', 'url': '/Chassis/System/Thermal/Fans/{}', 'maxtime': 20,
             'instances': [4]},
            {'api': 'GET', 'url': '/Chassis/System/Power', 'maxtime': 20},
            {'api': 'GET', 'url': '/Chassis/System/MainBoard', 'maxtime': 20},
            {'api': 'GET', 'url': '/Chassis/System/StorageEnclosure', 'maxtime': 20},
            {'api': 'GET', 'url': '/Chassis/System/StorageEnclosure/{}', 'maxtime': 20,
            'instances': [4]},
            {'api': 'GET', 'url': '/Chassis/System/StorageEnclosure/{}/Storage', 'maxtime': 20,
            'instances': [4]},
            {'api': 'GET', 'url': '/Chassis/System/StorageEnclosure/{0}/Drives/{1}', 'maxtime': 20,
            'instances': [4, 22]},
            {'api': 'GET', 'url': '/Managers/System', 'maxtime': 20},
            {'api': 'PATCH', 'url': '/Managers/System', 'body': {'Oem': 'Microsoft/NTP'}, 'maxtime': 20},
            {'api': 'GET', 'url': '/Managers/System/NetworkProtocol', 'maxtime': 20},
            {'api': 'GET', 'url': '/Managers/System/EthernetInterfaces', 'maxtime': 20},
            {'api': 'GET', 'url': '/Managers/System/EthernetInterfaces/1', 'maxtime': 20},
            {'api': 'GET', 'url': '/Managers/System/SerialInterfaces', 'maxtime': 20},
            {'api': 'GET', 'url': '/Managers/System/SerialInterfaces/1', 'maxtime': 20},
            {'api': 'GET', 'url': '/Managers/System/LogServices', 'maxtime': 120},
            {'api': 'GET', 'url': '/Managers/System/LogServices/Log', 'maxtime': 120},
            {'api': 'GET', 'url': '/Managers/System/LogServices/Log/Entries', 'maxtime': 120},
            {'api': 'GET', 'url': '/Managers/System/LogServices/Log/Entries/1', 'maxtime': 120}]

# Setup Function
def Setup(interfaceparams):
    return True


# Function will test URI response times and report the average time for each one
def Execute(interfaceparams):

    global testpassorfail
    element1 = 0
    element2 = 0
    cmdpassorfail = True
    filename = os.path.basename(__file__)

    try:
        # These iterations is to gather a relevant sample of service executions to average out. The value is set in the
        # Config.py file
        for iteration in range(Config.SAMPLE_ITERATIONS):
            UtilLogger.verboseLogger.info("\t=============== loop = {} ===============".format(iteration + 1))
            # Looping through each of the services entries
            for service in services:
                api = service.get('api')

                # This is only here because I separated the common root of the endpoints and yet still need to test
                # the root as a valid endpoint
                if service.get('url') is None:
                    url = Config.REDFISH_BASE_ADDRESS
                else:
                    url = "{0}{1}".format(Config.REDFISH_BASE_ADDRESS, service.get('url'))

                # This is for endpoints that have multiple iterations like with drives where we want to test all
                # of them and not just one. We don't have a separate entry for each of them in the services list so
                # we loop through them here.
                if 'instances' in service:
                    instances = service.get('instances')
                    element1 = instances[0]
                    if len(instances) == 2:
                        element2 = instances[1]
                        while element1 > 0 < element2:
                            serviceurl = url.format(element1, element2)
                            testpassorfail = _test_URI_Execution(service, serviceurl, iteration)
                            element2 -= 1
                            if element2 == 0 and element1 - 1 > 0:
                                element2 = instances[1]
                                element1 -= 1
                    else:
                        while element1 > 0:
                            serviceurl = url.format(element1)
                            testpassorfail = _test_URI_Execution(service, serviceurl, iteration)
                            element1 -= 1
                else:
                    testpassorfail = _test_URI_Execution(service, url, iteration)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        UtilLogger.verboseLogger.error("{0}: Test failed with exception - {1}".format(filename, e))
        UtilLogger.verboseLogger.error("\nException type: {0} \nLine number: {1}".format(exc_type, exc_tb.tb_lineno))
        testpassorfail = False

    # Get the average times and call out any outliers
    servicename = ''

    for serviceresult in elapsedservicetimes:
        servicename = serviceresult.get('service')
        maxtime = serviceresult.get('maxtime')
        servicetimes = serviceresult.get('elapsedtime')

        # Checking to see if we got the right number of successful results
        UtilLogger.verboseLogger.info("===== {} average response times results ====="
                                      .format(servicename))
        UtilLogger.verboseLogger.info("The raw results are: {}".format(servicetimes))
        if "Failed" in servicetimes:
            UtilLogger.verboseLogger.error("Failed to get enough successful iterations. Failed {} time(s).\n"
                                           .format(servicetimes.count('Failed')))
            testpassorfail = False
        else:
            successaverage = 0
            failedaverage = 0
            successtotaltime = 0
            failedtotaltime = 0
            failures = 0
            for timeresult in servicetimes:
                # We don't want to count a total failure in the average since it doesn't have a time
                if timeresult == "Failed":
                    failures += 1
                elif timeresult > maxtime:
                    failedtotaltime += timeresult
                    failures += 1
                else:
                    successtotaltime += timeresult
            # In case we got a failure we still want to see what our average was for those failed attempts
            if failures > 0:
                failedaverage = failedtotaltime / failures
            # This captures the average time of just the successful attempts
            if failures < Config.FAILED_URI_RETRIES:
                successaverage = successtotaltime / (Config.FAILED_URI_RETRIES - failures)
            # When the execution of the service is successful but they all failed to complete within the threshold
            if failures > 0 and failures == Config.FAILED_URI_RETRIES:
                UtilLogger.verboseLogger.error("The request was completed, but failed because it took too long to "
                                               "complete with an average time of {} seconds\n".format(failedaverage))
            # When there is a mix of successes that both are within and outside of the threshold
            elif 0 < failures < Config.FAILED_URI_RETRIES:
                UtilLogger.verboseLogger.error("There were too many failures to to pass, but the average of the "
                                               "attempts that did pass were {0} seconds and the average of the failed "
                                               "attempts was {1} seconds\n".format(successaverage, failedaverage))
            # When all of the attempts were within the threshold
            else:
                UtilLogger.verboseLogger.info("The request was completed successfully for all attempts with an average "
                                              "time of {} seconds\n".format(successaverage))

    return testpassorfail


# Prototype Cleanup Function
def Cleanup(interfaceparams):
    return True


def _test_URI_Execution(service, url, iteration):
    '''
    This private function handles the URI requests and logs the results.
    :param service: A dictionary of the service that is being tested.
    :param url: The URL endpoint that is being tested. This may be different from the one in the service dictionary
    since there may be additional parameters in the address for things like drive numbers.
    :param iteration: The iteration of the test. It's only used for the logging since it made more sense to put it here
    instead of in the area where this function was called from. This is because of the potential of having multiple
    iterations for a single endpoint like with testing the drives.
    :return: testpassorfail is the only thing returned. This function will be able to determine if a request has been
    successful or not and return the result back to the call.
    '''

    global elapsedservicetimes, testpassorfail
    username = Config.bmcUser
    password = Config.bmcPassword
    auth = (username, password)
    port = str(Config.httpRedfishPort)
    headers = {'Content-Type': 'application/json'}
    userpasswd = "{0}:{1}".format(username, password)
    encoded = "Basic {}".format(base64.b64encode(userpasswd))
    headers.update({"Authorization": encoded})
    session = None
    host = Config.bmcIpAddress
    elapsedservice = {}
    body = None

    UtilLogger.verboseLogger.info("\t=============== test = {0}:{1} ===============".format(service.get('api'), url))
    failedretrycounter = 0
    retryrequest = True

    # For the first iteration we'll need to create each of the service entries into the elapsedservicetimes list
    if iteration == 0:
        elapsedservicetimes.append({'service': "{0}:{1}".format(service.get('api'), url),
                                    'maxtime': service.get('maxtime'), 'elapsedtime': []})
        elapsedservice = elapsedservicetimes[len(elapsedservicetimes) - 1]
    # Once the entries have been entered, they now will now need to be recalled and appended to
    else:
        for elapsedservice in elapsedservicetimes:
            if elapsedservice.get('service') == "{0}:{1}".format(service.get('api'), url):
                break

    if "body" in service:
        body = service.get('body')
    else:
        body = None

    # We want to retry any failed requests a few times just in case it was a fluke. We record each attempt, though.
    # Even if we fail once, we still consider the test a failure. They should all pass the first time.
    while retryrequest is True and failedretrycounter <= Config.FAILED_URI_RETRIES:
        # Running service tests
        if failedretrycounter > 0:
            UtilLogger.verboseLogger.info("Retry number {} for a failed request".format(failedretrycounter))
        starttime = time.time()
        cmdpassorfail, response = RedFish.RestApiCall(session, host, url, service.get('api'), auth, port, body, headers)
        elapsedtime = time.time() - starttime
        status = response.status_code

        if status == 200:
            elapsedservice.get('elapsedtime').append(elapsedtime)
            retryrequest = False
        else:
            UtilLogger.verboseLogger.error("Failed service request with {} response code"
                                           .format(response.status_code))
            # For all but the last failure in this loop we increment the number of failed attempts
            if failedretrycounter < Config.FAILED_URI_RETRIES:
                failedretrycounter += 1
            # On the last attempt in the loop we give up and record a critical failure on the service attempt
            else:
                UtilLogger.verboseLogger.error("The service request failed too many times to be counted"
                                               " in the average.")
                elapsedservice.get('elapsedtime').append("Failed")
                testpassorfail = False
                break

    return testpassorfail
