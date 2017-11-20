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

from Helpers.Connection import Connection
import RedFish
import Config

class PSUMain(object):

    def __init__(self):

        self.all_data = get_psu_details()
        self.odatacontext = self.all_data.get("@odata.context")
        self.odataid = self.all_data.get("@odata.id")
        self.odatatype = self.all_data.get("@odata.id")
        self.id = self.all_data.get("Id")
        self.name = self.all_data.get("Name")


class PSU(object):

    def __init__(self, psu_id):

        psu_index = psu_id - 1

        self.all_data = get_psu_details()
        self.state = self.all_data.get("PowerSupplies")[psu_index].get("Status").get("State")
        if self.state != "N/A":
            self.odataid = self.all_data.get("PowerSupplies")[psu_index].get("@odata.id")
            self.actions_target = self.all_data.get("PowerSupplies")[psu_index].get("Actions").get("Oem")\
                .get("OcsBmc.v1_0_0##PowerSupply.ClearFaults").get("target")
            self.firmwareversion = self.all_data.get("PowerSupplies")[psu_index].get("FirmwareVersion")
            self.manufacturer = self.all_data.get("PowerSupplies")[psu_index].get("Manufacturer")
            self.memberid = self.all_data.get("PowerSupplies")[psu_index].get("MemberId")
            self.model = self.all_data.get("PowerSupplies")[psu_index].get("Model")
            self.name = self.all_data.get("PowerSupplies")[psu_index].get("Name")
            self.partnumber = self.all_data.get("PowerSupplies")[psu_index].get("PartNumber")
            self.powercapacitywatts = self.all_data.get("PowerSupplies")[psu_index].get("PowerCapacityWatts")
            self.relateditem_odata_id = self.all_data.get("PowerSupplies")[psu_index].get("RelatedItem")[0].get("@odata.id")
            self.serialnumber = self.all_data.get("PowerSupplies")[psu_index].get("SerialNumber")
            self.ActiveImage = self.all_data.get("PowerSupplies")[psu_index].get("ActiveImage")


class Redundancy(object):

    def __init__(self):

        self.all_data = get_psu_details()
        self.maxnumsupported = self.all_data.get("PowerSupplies")[2].get("Redundancy").get("MaxNumSupported")
        self.minnumneeded = self.all_data.get("PowerSupplies")[2].get("Redundancy").get("MinNumNeeded")
        self.mode = self.all_data.get("PowerSupplies")[2].get("Redundancy").get("Mode")
        self.redundancyset = self.all_data.get("PowerSupplies")[2].get("Redundancy").get("RedundancySet")


def get_psu_details():
    """
    Gets all of the details about the connected PSUs
    :return: A JSON representation of the returned results for easier consumption
    """

    connection = Connection()
    timeout = 10
    response = None
    cmd_pass_or_fail = True

    psu_url = '{0}/Chassis/System/Power'.format(Config.REDFISH_BASE_ADDRESS)

    cmd_pass_or_fail, response = RedFish.SendRestRequest(psu_url, connection.auth, connection.port, data=None,
                                                 restRequestMethod="GET", timeout=timeout)
    response_json = response.json()

    return response_json
