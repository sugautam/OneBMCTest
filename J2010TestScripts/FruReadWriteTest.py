"""# PyTestUtil
#
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
import os
from Helpers import Connection
import json
from J2010TestScripts import ConfigJ2010


# Setup Function
def Setup(interfaceParams):

    file_name = os.path.splitext(os.path.basename(__file__))[0]
    UtilLogger.verboseLogger.info("\n===== running {} Test =====\n".format(file_name))
    return True


# Function will test FRU Read/Write tests
def Execute(interfaceParams):
    test_pass_or_fail = True
    payload = {}
    response = None
    current_fru = {}
    connection = Connection.Connection()
    result = True
    original_values = None

    try:
        # Read the current FRU values
        cmd_pass_or_fail, response = _read_fru_values(connection, ConfigJ2010.api_path)

        # Print the current FRU values
        if cmd_pass_or_fail:
            response_json = response.json()
            original_values = response_json
            main_board_fru = response_json.get('Oem').get('Microsoft').get('MainBoardFRU')
            for fru_field in ConfigJ2010.fru_fields:
                if fru_field in main_board_fru:
                    current_fru[fru_field] = main_board_fru.get(fru_field)
                    UtilLogger.verboseLogger.info("FRU Field: {0}; Current Value: {1}"
                                                  .format(fru_field,   main_board_fru.get(fru_field)))
        else:
            UtilLogger.verboseLogger.error("Failed: Can't read FRU fields")
            return cmd_pass_or_fail

        # Iterate through each field type and load it with different types of data
        for fru_field in ConfigJ2010.fru_fields:
            UtilLogger.verboseLogger.info("Testing the '{}' attribute".format(fru_field))
            # Iterate through each of the test scenarios for the current field
            for scenario in ConfigJ2010.test_scenarios_pass:
                result, current_fru = _run_test(connection, current_fru, fru_field, scenario,
                                                ConfigJ2010.test_scenarios_pass)
                test_pass_or_fail &= result
            for scenario in ConfigJ2010.test_scenarios_fail:
                result, current_fru = _run_test(connection, current_fru, fru_field, scenario,
                                                ConfigJ2010.test_scenarios_fail,
                                                switch_result=True)
                test_pass_or_fail &= result

    except Exception, e:
            UtilLogger.verboseLogger.error("Failed: test failed. Exception: {}".format(str(e)))
            test_pass_or_fail = False

    # Reset the environment back to where it was when we started
    cmd_pass_or_fail, response = _write_fru_values(connection, original_values, ConfigJ2010.api_path)
    if not cmd_pass_or_fail:
        UtilLogger.verboseLogger.error("Failed: Environment was not able to be reset to original values")
        test_pass_or_fail &= cmd_pass_or_fail

    return test_pass_or_fail


# Prototype Cleanup Function
def Cleanup(interfaceParams):

    file_name = os.path.splitext(os.path.basename(__file__))[0]
    UtilLogger.verboseLogger.info("\n===== Completed running {} Test =====\n".format(file_name))
    return True


def _run_test(connection, current_fru, fru_field, scenario, test_scenarios, switch_result=False):
    """
    Runs the tests for both positive and negative tests
    :param connection: The connection object to the J2010
    :param current_fru: The current dictionary values for each of the properties that are being tested
    :param fru_field: The current property field that's being tested and evaluated
    :param scenario: The test scenario being covered in this test pass
    :param test_scenarios: List of all of the test scenarios. This must be passed because it could be one of two lists
    :param switch_result: This determines if the result should expect a pass (True) or expect a fail (False) for the
    evaluation of the test
    :return: The pass/fail of the test and the new current_fru in case it needs to be modified from a test that breaks
    other tests
    """
    
    test_pass_or_fail = True
    test_name = scenario
    test_data = test_scenarios.get(scenario)
    UtilLogger.verboseLogger.info("Testing scenario '{}'".format(test_name))
    current_fru[fru_field] = test_data
    payload = {"Oem": {"Microsoft": {"MainBoardFRU": current_fru}}}
    payload = json.dumps(payload)
    loaded_payload = json.loads(payload)

    try:
        # Update the specified FRU field
        cmd_pass_or_fail, response = _write_fru_values(connection, loaded_payload, ConfigJ2010.api_path)

        # Get ALL messages for the FRU fields that were updated
        if cmd_pass_or_fail:
            success, response = _read_fru_values(connection, ConfigJ2010.api_path)
            response_json = response.json()
            updated_field = response_json.get("Oem").get("Microsoft").get("MainBoardFRU").get(fru_field)
            if updated_field == '' and (test_data is None or len(test_data) == 1):
                UtilLogger.verboseLogger.info("FRU field {0} with value 'None' was found".format(fru_field))
            elif updated_field == '' and len(test_data) >= ConfigJ2010.char_min:
                UtilLogger.verboseLogger.error("Failed: The FRU field {0} had the incorrect value. Expected "
                                               "'{1}' and got 'None'.".format(fru_field, test_data))
                test_pass_or_fail = False
            elif updated_field == test_data:
                if switch_result is False:
                    UtilLogger.verboseLogger.info("FRU field {0} with value '{1}' was found"
                                                  .format(fru_field, updated_field))
                else:
                    UtilLogger.verboseLogger.info("Failed: FRU field {0} with value '{1}' was found"
                                                  .format(fru_field, updated_field))
                    test_pass_or_fail = False
            else:
                if switch_result is False:
                    UtilLogger.verboseLogger.error("Failed: The FRU field {0} had the incorrect value. Expected "
                                                   "'{1}' and got '{2}1".format(fru_field, test_data,
                                                                                updated_field))
                    test_pass_or_fail = False
                else:
                    UtilLogger.verboseLogger.error("The FRU field had a different value. Got '{}'"
                                                   .format(updated_field))
        else:
            test_pass_or_fail = False
    except Exception, e:
        UtilLogger.verboseLogger.info("Failed: Can't write FRU fields with exception: {}".format(e))
        test_pass_or_fail = False

    # If the test value is out of the bounds for what is acceptable, then we need to reset it to something
    # within the bounds so that it doesn't mess up subsequent tests by having an illegal value in it.
    if 2 > len(test_data) or len(test_data) > ConfigJ2010.char_max:
        current_fru[fru_field] = "Default"

    return test_pass_or_fail, current_fru


def _read_fru_values(connection, api_path):
    """
    Reads the FRU values.
    :param api_path: The API path for the service call
    :return: The test success or failure and the response data.
    """

    cmd_pass_or_fail = True
    response = None
    body = None

    try:
        cmd_pass_or_fail, response = RedFish.RestApiCall(connection.session, connection.host, api_path,  "GET",
                                                         connection.auth, connection.port, body, connection.headers)
        # Send REST GET request
        # cmd_pass_or_fail, response = RedFish.GetResourceValues(api_path)

    except Exception, e:
        UtilLogger.verboseLogger.error("Failed: Test failed. Exception: {}".format(str(e)))
        cmd_pass_or_fail = False
    
    return cmd_pass_or_fail, response


def _write_fru_values(connection, payload, api_path):
    """
    Writes the FRU values
    :param data: The data to write to the FRU
    :param api_path: The relative API path for the service call
    :return: Either True or False for the success of the operation
    """

    cmd_pass_or_fail = True
    response = None
    
    try:
        # Send REST PATCH request and verify response
        # Send REST PATCH request        
        cmd_pass_or_fail, response = RedFish.RestApiCall(connection.session, connection.host, api_path, "PATCH",
                                                         connection.auth, connection.port, payload, connection.headers)

        if not cmd_pass_or_fail:
            UtilLogger.verboseLogger.error("Failed: The update failed. Response code was {}"
                                           .format(response.status_code))
            return cmd_pass_or_fail

        # Setting data to None since it's not needed for the next call
        data = None
        cmd_pass_or_fail, response = RedFish.RestApiCall(connection.session, connection.host, api_path,  "GET",
                                                         connection.auth, connection.port, data, connection.headers)
        if not cmd_pass_or_fail:
            UtilLogger.verboseLogger.error("Failed: The GET failed. Response code was {}"
                                           .format(response.status_code))

    except Exception, e:
        UtilLogger.verboseLogger.error("Failed: Test failed. Exception: {}".format(str(e)))
        cmd_pass_or_fail = False
        
    return cmd_pass_or_fail, response
