"""
OneBMCTest


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
import Config
import RedFish
import UtilLogger
from J2010TestScripts import ConfigJ2010
import paramiko


# Setup Function
def Setup(interfaceParams):

    file_name = os.path.splitext(os.path.basename(__file__))[0]
    UtilLogger.verboseLogger.info("\n===== Starting the {} tests =====\n".format(file_name))
    return True


# Function will update the FW
def Execute(interfaceParams):

    username = Config.bmcUser
    password = Config.bmcPassword
    auth = (Config.bmcUser, Config.bmcPassword)
    port = str(Config.httpRedfishPort)
    update_new_fw_version = False
    exec_pass_or_fail = True
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    timeout = 10

    UtilLogger.verboseLogger.info("{}: running Setup".format(file_name))
    firmware = Firmware()

    # Set FW versions
    firmware.set_bin_assignments('set')

    try:
        for bank, action_list in ConfigJ2010.FW_UPDATE_LIST:

            if bank == "secondary":
                _boot_to_secondary()

            stage_number = 1

            if stage_number == 1:
                # Verifying that there is FW present to start with
                exec_pass_or_fail, firmware.current_fw_version = RedFish.GetFirmwareVersion(auth)
                _log_pass_or_fail(stage_number, 'get', exec_pass_or_fail)
                if not exec_pass_or_fail:
                    return exec_pass_or_fail

                if firmware.current_fw_version == firmware.old_fw_version:
                    firmware.current_fw_bin = firmware.bmc_prev_bin_file
                    firmware.change_fw_bin = firmware.bmc_next_bin_file
                elif firmware.current_fw_version == firmware.new_fw_version:
                    firmware.current_fw_bin = firmware.bmc_next_bin_file
                    firmware.change_fw_bin = firmware.bmc_prev_bin_file
                else:
                    UtilLogger.verboseLogger.info("Warning: The starting version of the firmware is either not the "
                                                  "same as either the old or new firmwares that will be used for "
                                                  "testing, or you have specified the wrong expected versions for "
                                                  "configJ2010.FW_VERSIONS. This test will deploy the old firmware as "
                                                  "a starting point.")
                    exec_pass_or_fail, test_fw_version = RedFish.UpdateFW(firmware.bmc_prev_bin_file, auth, port,
                                                                          username, password, bank)
                    _log_pass_or_fail(stage_number, 'get', exec_pass_or_fail)

                    if not exec_pass_or_fail:
                        return exec_pass_or_fail
                    exec_pass_or_fail, firmware.current_fw_version = RedFish.GetFirmwareVersion(auth)

                    if firmware.current_fw_version != firmware.old_fw_version:
                        UtilLogger.verboseLogger.info("Warning: The firmware designated as the old version in "
                                                      "ConfigJ2010.FW_VERSIONS is not the same as the version of bin "
                                                      "file being used. Expected: {0} and got {1}. Testing will "
                                                      "continue, but the new value will be used as the old version "
                                                      "number.".format(firmware.old_fw_version,
                                                                       firmware.current_fw_version))
                        firmware.old_fw_version = firmware.current_fw_version
                        update_new_fw_version = True
                    firmware.current_fw_bin = firmware.bmc_prev_bin_file
                    firmware.change_fw_bin = firmware.bmc_next_bin_file

            for action in action_list:
                if action.lower() == "same":
                    exec_pass_or_fail, test_fw_version = RedFish.UpdateFW(firmware.current_fw_bin, auth, port, username,
                                                                          password, bank)

                    if bank == "secondary":
                        _boot_to_secondary()
                        test_fw_version = RedFish.GetFirmwareVersion(auth)

                    _log_pass_or_fail(stage_number, 'update', exec_pass_or_fail, test_fw_version)
                    if not exec_pass_or_fail:
                        return exec_pass_or_fail
                    if firmware.current_fw_version != test_fw_version:
                        UtilLogger.verboseLogger.error("Error: The firmware version wasn't the expected version. Was "
                                                       "expecting {0} and got {1}".format(firmware.current_fw_version,
                                                                                          test_fw_version))
                    stage_number += 1
                elif action.lower() == "change":
                    (exec_pass_or_fail, test_fw_version) = RedFish.UpdateFW(firmware.change_fw_bin, auth, port,
                                                                            username, password, bank)

                    if bank == "secondary":
                        _boot_to_secondary()
                        test_fw_version = RedFish.GetFirmwareVersion(auth)

                    _log_pass_or_fail(stage_number, 'update', exec_pass_or_fail, test_fw_version)

                    # If the expected firmware version for the new bin is not the same as what was expected and
                    # previously we had to adjust the old firmware version, then we'll update the version here to use
                    # for the rest of the test run.
                    if update_new_fw_version is True and firmware.new_fw_version != test_fw_version:
                        firmware.new_fw_version = test_fw_version
                        UtilLogger.verboseLogger.info("Warning: The firmware designated as the new version in "
                                                      "ConfigJ2010.FW_VERSIONS is not the same as the version of bin "
                                                      "file being used. Expected: {0} and got {1}. Testing will "
                                                      "continue, but the new value will be used as the new version "
                                                      "number.".format(firmware.old_fw_version,
                                                                       firmware.current_fw_version))
                        update_new_fw_version = False

                    if not exec_pass_or_fail or firmware.current_fw_version == test_fw_version:
                        return exec_pass_or_fail
                    if firmware.current_fw_version == test_fw_version:
                        UtilLogger.verboseLogger.error("Error: The firmware version wasn't the expected version. Was "
                                                       "expecting {0} and got the same version.")\
                            .format(firmware.current_fw_version)

                    firmware.set_bin_assignments('change')
                    stage_number += 1
                else:
                    UtilLogger.verboseLogger.error("Error: An invalid action type was used. The valid types are 'same' "
                                                   "or 'change'. The one used was {}".format(action))
                    return False

    except Exception, e:
            UtilLogger.verboseLogger.error("Exception Error: Test failed with exception - {}".format(e))
            exec_pass_or_fail = False

    return exec_pass_or_fail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    file_name = os.path.splitext(os.path.basename(__file__))[0]
    UtilLogger.verboseLogger.info("\n===== Completed the {} tests =====\n".format(file_name))
    return True


def _boot_to_secondary():
    """
    Reboots the BMC to the secondary partition
    :return: Nothing needs to be returned
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(Config.bmcIpAddress, username=Config.bmcUser, password=Config.bmcPassword)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("devmem 0x1E785024 32 0x002DC6C0")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("devmem 0x1E785028 32 0x00004755")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("devmem 0x1E78502C 32 0x00000093")

    # Wait for reboot to complete
    exec_pass_or_fail = RedFish.CheckForRunningRedfishServer()


def _log_pass_or_fail(stage_number, message_type, exec_pass_or_fail, data=None):
    """
    This is for performing and logging the comparePassOrFail status
    :param stage_number: The stage number in the test. It can be a string or number.
    :param message_type: The type or status of message to log. Things like getting firmware status, updating firmware,
    or comparing firmware details
    :return: Nothing needs to be returned from here since it's only for reporting
    """

    message_prefix = "stage {}: ".format(stage_number)

    if exec_pass_or_fail:
        pass_fail = "passed"
    else:
        pass_fail = "failed"

    if message_type.lower() == "get":
        message_text = "{0}GetFirmwareVersion {1}".format(message_prefix, pass_fail)
    elif message_type.lower() == "update":
        message_text = "{0}Update FW bmc_prev_bin_file {1}. \n\tFirmware updated to the versions of {2}"\
            .format(message_prefix, pass_fail, data)
    elif message_type.lower() == "compare":
        message_text = "{0}FWVersions {1}".format(message_prefix, pass_fail)
    else:
        message_text = "Error: '{0}' is an invalid message type sent for logging. Should be 'get', 'update', or" \
                       "'compare'.".format(message_type)

    UtilLogger.verboseLogger.info(message_text)

    return True


class Firmware:

    current_fw_version = None
    old_fw_version = None
    old_fw_bin = None
    new_fw_version = None
    new_fw_bin = None
    current_fw_bin = None
    change_fw_bin = None
    bmc_prev_bin_file = None
    bmc_next_bin_file = None

    def __init__(self):

        versions = ['New', 'Old']

        for version in versions:
            if version == 'New':
                self.bmc_next_bin_file = self._get_firmware_image_path(Config.bmcNextBinFilePath)
                UtilLogger.verboseLogger.info("New firmware image is {}".format(self.bmc_next_bin_file))
                if not self.bmc_next_bin_file:
                    UtilLogger.verboseLogger.error(
                        "Error: There was no bin file in the location '{}'.".format(Config.bmcNextBinFilePath))
            else:
                self.bmc_prev_bin_file = self._get_firmware_image_path(Config.bmcPrevBinFilePath)
                UtilLogger.verboseLogger.info("Old firmware image is {}".format(self.bmc_prev_bin_file))
                if not self.bmc_prev_bin_file:
                    UtilLogger.verboseLogger.error(
                        "Error: There was no bin file in the location '{}'.".format(self.bmc_prev_bin_file))

    def set_bin_assignments(self, action):
        """
        Setting the assignment of the bin file locations on the local system.
        :param action: This is where you specify the type of action for assignment either to initially 'set' the values
        or to change them for the next test.
        :return: Nothing needs to be returned since you're updating the object attributes
        """

        if action == 'set':
            if type(ConfigJ2010.FW_VERSIONS) is list and len(ConfigJ2010.FW_VERSIONS) == 2:
                if ConfigJ2010.FW_VERSIONS[0] > ConfigJ2010.FW_VERSIONS[1]:
                    self.old_fw_version = ConfigJ2010.FW_VERSIONS[1]
                    self.new_fw_version = ConfigJ2010.FW_VERSIONS[0]
                else:
                    self.old_fw_version = ConfigJ2010.FW_VERSIONS[0]
                    self.new_fw_version = ConfigJ2010.FW_VERSIONS[1]
        elif action == 'change':
            if self.current_fw_version == self.old_fw_version:
                self.current_fw_bin = self.bmc_prev_bin_file
                self.change_fw_bin = self.bmc_next_bin_file
            else:
                self.current_fw_bin = self.bmc_next_bin_file
                self.change_fw_bin = self.bmc_prev_bin_file
        else:
            UtilLogger.verboseLogger.error("An invalid action value was used to set the bin file assignment. The value "
                                           "{} was used.".format(action))

    @staticmethod
    def _get_firmware_image_path(bmc_bin_file_path):
        """
        Searches the bin directory provided for a bin file and then returns the entire path
        :param bmc_bin_file_path: The directory where the bin file is located.
        :return: Will return either the entire path of where the bin file is including the bin file name, or if none
        could be found, then it will return False and log an error.
        """

        file_in_dir = None
        try:
            directory_files = os.listdir(bmc_bin_file_path)
        except Exception as e:
            directory_files = []
        for file_in_dir in directory_files:
            if file_in_dir[len(file_in_dir) - 3:] == 'bin':
                return os.path.join(bmc_bin_file_path, file_in_dir)
        if file_in_dir is None:
            UtilLogger.verboseLogger.error("Error: No binary image found in {}".format(bmc_bin_file_path))
            return False
