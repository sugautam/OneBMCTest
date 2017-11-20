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

"""
These are global constants for the J2010 product. 
"""

import Config

SERVICE_ROOT = 'redfish/v1/'
SERVICES = [{'api': 'GET', 'url': '$metadata', 'maxtime': 20},
            {'api': 'GET', 'url': 'UpdateService', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System/Sensors', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System/FRU', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System/Thermal#/Redundancy', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System/Thermal#/Fans/1', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System/Power', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System/Power#/PowerSupplies/1', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/Power#/Redundancy', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System/MainBoard', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System/StorageEnclosure/1', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System/StorageEnclosure/1/Storage', 'maxtime': 20},
            {'api': 'GET', 'url': 'Chassis/System/StorageEnclosure/1/Drives/1', 'maxtime': 20},
            {'api': 'GET', 'url': 'Managers/System', 'maxtime': 20},
            {'api': 'PATCH', 'url': 'Managers/System', 'body': {'Oem': 'Microsoft/NTP'}, 'maxtime': 20},
            {'api': 'GET', 'url': 'Managers/System/NetworkProtocol', 'maxtime': 20},
            {'api': 'GET', 'url': 'Managers/System/EthernetInterfaces', 'maxtime': 20},
            {'api': 'GET', 'url': 'Managers/System/EthernetInterfaces/1', 'maxtime': 20},
            {'api': 'GET', 'url': 'Managers/System/SerialInterfaces', 'maxtime': 20},
            {'api': 'GET', 'url': 'Managers/System/SerialInterfaces/1', 'maxtime': 20},
            {'api': 'GET', 'url': 'Managers/System/LogServices', 'maxtime': 120},
            {'api': 'GET', 'url': 'Managers/System/LogServices/Log', 'maxtime': 120},
            {'api': 'GET', 'url': 'Managers/System/LogServices/Log/Entries', 'maxtime': 120},
            {'api': 'GET', 'url': 'Managers/System/LogServices/Log/Entries/1', 'maxtime': 120}]

# For the update list, the expected possible values ore "primary" or "secondary" for the primary or secondary modules,
# and "change" or "same" to either change the FW version to the other version or apply the same one that's already there
FW_UPDATE_LIST = [["primary", ["change", "same", "change", "same"]], ["secondary", ["change", "same", "change",
                                                                                    "same"]]]

# FW_VERSIONS is an optional list. It must either be None or have 2 different string values like "v2.02.00", "v2.01.00"
BMC_FW_VERSIONS = ["v2.04.00", "v2.03.00"]

# FRU FW update section
FRU_RW_TEST_API_PATH = 'redfish/v1/Chassis/System/FRU'
FRU_RW_TEST_FIELDS = ['ChassisPartNumber', 'ChassisSerialNumber', 'PDAssetTag', 'PDSerialNumber', 'PDCustomField2']
# The following tests need to be pass to be successful (positive tests)
FRU_RW_PASS_SCENARIOS = {"Single character": "a", "Two characters": "te", "Multiple characters": "aoeu",
                       "Max characters": "Aoeuidhtnspyfgcrlqjkxbmwvz Aoeuidhtnspyfgcrlqjkxbmwvz Aoeuidhtn"}
# The following tests need to fail to be successful (negative tests)
FRU_RW_FAIL_SCENARIOS = {"Over max characters": "Aoeuidhtnspyfgcrlqjkxbmwvz Aoeuidhtnspyfgcrlqjkxbmwvz Aoeuidhtno"}
FRU_RW_MIN_CHARS = 2
FRU_RW_MAX_CHARS = 63

# PSU FW update section
PSU_FLASH_FILE_PATH = '/var/wcs/home/'
PSU_LOCAL_FILE_PATH = './FirmwareBin/PSUFirmware/'
PSU_OLD_FW_VERSION = '111Y0000'
PSU_NEW_FW_VERSION = '111Y0000'
PSU_OLD_FW_FILE = None
PSU_UPDATE_TIMEOUT = 840
PSU_FORCE_UPDATE = "yes"

# PSU_TEST_SET uses either "update" or "downgrade" for the action, and then you specify the PSU number with a set of
# the BIOS chips you want to change. This will probably change when we have more than 1 FW version to test with
PSU_TEST_SET = {"update": {1: [1, 2], 2: [1, 2]}, "downgrade": {1: [1, 2], 2: [1, 2]}}
FW_RESOURCE_URL = "redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate"

# Sensor Stress Test section
SENSOR_STRESS_SAMPLES = 20
