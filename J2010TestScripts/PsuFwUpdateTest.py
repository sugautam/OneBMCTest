"""
PyTestUtil

Copyright (c) Microsoft Corporation

All rights reserved.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"),
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
from Helpers.Connection import Connection
from J2010TestScripts import ConfigJ2010
import Psu
import time
import os


# Setup Function
def Setup(interfaceParams):
    return True


# Function will update the FW
def Execute(interfaceParams):

    connection = Connection()
    cmd_pass_or_fail = True
    exec_pass_or_fail = True
    psu_fw_id = None
    current_fw_file = None
    current_local_dir = None

    for test_set in ConfigJ2010.PSU_TEST_SET:
        if test_set == "update":
            current_local_dir = "{}next/".format(ConfigJ2010.PSU_LOCAL_FILE_PATH)
        elif test_set == "downgrade":
            current_local_dir = "{}prev/".format(ConfigJ2010.PSU_LOCAL_FILE_PATH)
        else:
            UtilLogger.verboseLogger.error("Failed: An invalid action type has been passed. Cannot perform the action "
                                           "{}".format(test_set))
            return False
        current_fw_file = _get_firmware_image(current_local_dir)
        psu_set = ConfigJ2010.PSU_TEST_SET.get(test_set)
        for psu in psu_set:
            # Verify that the PSU is present
            current_psu = Psu.PSU(psu)
            if current_psu.state == "N/A":
                UtilLogger.verboseLogger.error("PSU was not available for FW upgrade")
                cmd_pass_or_fail = False
                break

            for psu_fw in psu_set.get(psu):
                if psu_fw == 1:
                    psu_fw_id = 'primary'
                elif psu_fw == 2:
                    psu_fw_id = 'secondary'
                else:
                    UtilLogger.verboseLogger.error("Failed: Invalid PSU FW value of '{}'".format(psu_fw))

                # Check to see if PSU is ready to be updated
                if cmd_pass_or_fail:
                    exec_pass_or_fail = RedFish.is_psu_ready(current_psu)
                    cmd_pass_or_fail &= exec_pass_or_fail

                # Pushing the file to the staging location
                if cmd_pass_or_fail:
                    UtilLogger.verboseLogger.info(
                        "Starting the push of the PSU FW update on PSU {0} for the {1} FW using hex file: \n\t {2}\n"
                        .format(psu, psu_fw_id, current_fw_file))
                    exec_pass_or_fail = RedFish.push_fw_for_staging(current_fw_file, current_local_dir)
                    if exec_pass_or_fail:
                        UtilLogger.verboseLogger.info("Image was successfully pushed")
                    else:
                        UtilLogger.verboseLogger.error("Failed: Image was not successfully pushed")
                        cmd_pass_or_fail = False

                # Initiating the update
                if cmd_pass_or_fail:
                    start_time = time.time()
                    payload = {'ImageURI': 'file://{0}?component=psu{1}&partition={2}&force={3}'
                               .format(current_fw_file, psu, psu_fw_id, ConfigJ2010.PSU_FORCE_UPDATE),
                               'TransferProtocol': 'OEM'}
                    exec_pass_or_fail = RedFish.initiate_fw_update(connection, payload, psu)

                # Check to see if it has completed. Checking to see if the state is Enabled and then monitoring the
                # Updating state for completion of the update.
                timeout = time.time() + 5
                while current_psu.state == "Enabled" and time.time() < timeout:
                    current_psu = Psu.PSU(psu)

                timeout = time.time() + ConfigJ2010.PSU_UPDATE_TIMEOUT
                while current_psu.state == "Updating" and time.time() < timeout:
                    current_psu = Psu.PSU(psu)

                UtilLogger.verboseLogger.info("FW update took {} seconds to complete".format(time.time() - start_time))

                if current_psu.state == "Enabled":
                    if cmd_pass_or_fail and test_set == 'update':
                        if current_psu.firmwareversion != ConfigJ2010.PSU_NEW_FW_VERSION:
                            cmd_pass_or_fail = False
                    elif cmd_pass_or_fail and test_set == 'downgrade':
                        if current_psu.firmwareversion != ConfigJ2010.PSU_OLD_FW_VERSION:
                            cmd_pass_or_fail = False
                    else:
                        UtilLogger.verboseLogger.error("Failed: The firmware didn't change to the expected version")
                else:
                    UtilLogger.verboseLogger.error("Failed: The FW did not complete in time")
                    cmd_pass_or_fail = False

                cmd_pass_or_fail &= exec_pass_or_fail

    return cmd_pass_or_fail

# Prototype Cleanup Function
def Cleanup(interfaceParams):
    return True


def _get_firmware_image(psu_file_path):
    """
    Searches the directory provided for a hex file and then returns the entire path
    :param psu_file_path: The directory where the hex file is located.
    :return: Will return either the entire path of where the hex file is including the hex file name, or if none
    could be found, then it will return False and log an error.
    """

    file_in_dir = None
    try:
        directory_files = os.listdir(psu_file_path)
    except Exception as e:
        directory_files = []
    for file_in_dir in directory_files:
        if file_in_dir[len(file_in_dir) - 3:] == 'hex':
            return file_in_dir
    if file_in_dir is None:
        UtilLogger.verboseLogger.error("Error: No binary image found in {}".format(psu_file_path))
        return False
