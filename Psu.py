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

import Config
import IpmiUtil
import UtilLogger
import RedFish
from Helpers.Connection import Connection

class PsuFwInfo:

    # General Static Variables
    pmbReadFwInfoRespLen = 9

    # Define PSU FW Image Type Field Constants
    psuImageTypeFwBootloader = 0
    psuImageTypeFwImageA = 1
    psuImageTypeFwImageB = 2

    # Define PSU FW Version Field Constants
    psuFwMajorVersionName = 'Major Version'
    psuFwMinorVersionName = 'Minor Version'
    psuFwMasterBetaVersionName = 'Master Beta Version'
    psuFwUcdBetaVersionName = 'UCD Beta Version'
    psuFwIvsBetaVersionName = 'IVS Beta Version'
    psuFwBbuBetaVersionName = 'BBU Beta Version'

    # Dictionary of key (int): value (string list) pairs that define arguments for
    # Configure Firmware Update response Operation Result
    # ie { <imageTypeInt> : [ <imageTypeString>, <imageTypeHexInPmbus> ] }
    imageTypeDict = { \
        psuImageTypeFwBootloader : [ 'FW Bootloader', '00' ], \
        psuImageTypeFwImageA : [ 'FW Image A', '0A' ], \
        psuImageTypeFwImageB : [ 'FW Image B', '0B' ] \
        }

    # Dictionary of key (int): value (string list) pairs that enumerates
    # comparison values
    # ie { <imageTypeInt> : [ <imageTypeString>, <imageTypeHexInPmbus> ] }
    compareOutDict = { \
        1 : 'newer than', \
        0 : 'equal to', \
        -1 : 'older than' \
        }

    # Dictionary of key (string): value (int list) pairs that define
    # [ field index, field length ]
    psuFwVersionFormatDict = { \
        psuFwMajorVersionName : [ 0, 2 ], \
        psuFwMinorVersionName : [ 2, 2 ], \
        psuFwMasterBetaVersionName : [ 4, 1], \
        psuFwUcdBetaVersionName : [5, 1], \
        psuFwIvsBetaVersionName : [6, 1], \
        psuFwBbuBetaVersionName : [7, 1] \
        }

    # Constructor
    def __init__(self):

        self.imageType = None # int

        self.activeOrInactive = None # bool
        self.psuFwVersion = None # string
        self.majorVersion = None # int
        self.minorVersion = None # int
        self.masterVersion = None # int
        self.ucdVersion = None # int
        self.ivsVersion = None # int
        self.bbuVersion = None # int

        return

    
    # Function will update PsuFwInfo object
    # Outputs:
    #   updatePassOrFail (bool): successfully updated PSU FW Version (True) or not (False)
    def UpdatePsuFwInfo(self, interfaceParams, imageType):

        # Initialize variables
        updatePassOrFail = False
        self.imageType = imageType
        
        # Get Psu Version Info
        getPassOrFail, self.activeOrInactive, rawPsuVersion = self.GetPsuFwVersionInfo(interfaceParams, \
            imageType)
        if getPassOrFail: 
            if Config.debugEn:
                UtilLogger.verboseLogger.info('PsuFwInfo.UpdatePsuFwVersion: ' + \
                    ' successfully received PsuFwVersionInfo. Image Type: ' + \
                    self.imageTypeDict[imageType][0] + '.' + \
                    ' Image Active: ' + str(self.activeOrInactive) + '.' + \
                    ' Raw Psu Version: ' + str(rawPsuVersion))
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error('PsuFwInfo.UpdatePsuFwVersion: ' + \
                    ' failed to receive PsuFwVersionInfo. Image Type: ' + \
                    self.imageTypeDict[imageType][0] + '.' + \
                    ' Image Active: ' + str(self.activeOrInactive) + '.' + \
                    ' Raw Psu Version: ' + str(rawPsuVersion))
            return updatePassOrFail
        
        # Update PSU FW Version
        updatePassOrFail = self.UpdatePsuFwVersion(rawPsuVersion)
        if updatePassOrFail:
            if Config.debugEn:
                UtilLogger.verboseLogger.info('PsuFwInfo.UpdatePsuFwVersion: ' + \
                    ' successfully updated PSU FW Version.')
        else:
            if Config.debugEn:
                UtilLogger.verboseLogger.error('PsuFwInfo.UpdatePsuFwVersion: ' + \
                    ' failed to update PSU FW Version.')

        return updatePassOrFail

    # Function will update PSU FW Version in PsuFwInfo object
    # using raw byte list response of PSU FW version via PMBus command Read_FW_Info
    def UpdatePsuFwVersion(self, rawPsuFwVersion):

        # Initialize variables
        updatePassOrFail = False

        try:

            # Update PSU FW Major Version
            rawMajIntString = ''
            startingOffset = self.psuFwVersionFormatDict[self.psuFwMajorVersionName][0]
            fieldLength = self.psuFwVersionFormatDict[self.psuFwMajorVersionName][1]
            rawMajAsciiList = rawPsuFwVersion[\
                startingOffset : startingOffset + fieldLength]
            for rawMajChar in rawMajAsciiList:
                rawMajIntString += str(unichr(int(rawMajChar, 16)))
            self.majorVersion = int(rawMajIntString)

            # Update PSU FW Minor Version
            rawMinIntString = ''
            startingOffset = self.psuFwVersionFormatDict[self.psuFwMinorVersionName][0]
            fieldLength = self.psuFwVersionFormatDict[self.psuFwMinorVersionName][1]
            rawMinAsciiList = rawPsuFwVersion[\
                startingOffset : startingOffset + fieldLength]
            for rawMinChar in rawMinAsciiList:
                rawMinIntString += str(unichr(int(rawMinChar, 16)))
            self.minorVersion = int(rawMinIntString)

            # Update PSU FW Master Beta Version
            rawMstrHexString = ''
            startingOffset = self.psuFwVersionFormatDict[self.psuFwMasterBetaVersionName][0]
            fieldLength = self.psuFwVersionFormatDict[self.psuFwMasterBetaVersionName][1]
            rawMstrHexList = rawPsuFwVersion[\
                startingOffset : startingOffset + fieldLength]
            for rawMstrHex in rawMstrHexList:
                rawMstrHexString += rawMstrHex
            self.masterVersion = int(rawMstrHexString, 16)

            # Update PSU FW UCD Beta Version
            rawUcdHexString = ''
            startingOffset = self.psuFwVersionFormatDict[self.psuFwUcdBetaVersionName][0]
            fieldLength = self.psuFwVersionFormatDict[self.psuFwUcdBetaVersionName][1]
            rawUcdHexList = rawPsuFwVersion[\
                startingOffset : startingOffset + fieldLength]
            for rawUcdHex in rawUcdHexList:
                rawUcdHexString += rawUcdHex
            self.ucdVersion = int(rawUcdHexString, 16)

            # Update PSU FW IVS Beta Version
            rawIvsHexString = ''
            startingOffset = self.psuFwVersionFormatDict[self.psuFwIvsBetaVersionName][0]
            fieldLength = self.psuFwVersionFormatDict[self.psuFwIvsBetaVersionName][1]
            rawIvsHexList = rawPsuFwVersion[\
                startingOffset : startingOffset + fieldLength]
            for rawIvsHex in rawIvsHexList:
                rawIvsHexString += rawIvsHex
            self.ivsVersion = int(rawIvsHexString, 16)

            # Update PSU FW BBU Beta Version
            rawBbuHexString = ''
            startingOffset = self.psuFwVersionFormatDict[self.psuFwBbuBetaVersionName][0]
            fieldLength = self.psuFwVersionFormatDict[self.psuFwBbuBetaVersionName][1]
            rawBbuHexList = rawPsuFwVersion[\
                startingOffset : startingOffset + fieldLength]
            for rawBbuHex in rawBbuHexList:
                rawBbuHexString += rawBbuHex
            self.bbuVersion = int(rawBbuHexString, 16)

            # Generate PSU FW Version String
            self.psuFwVersion = str(rawMajIntString) + '.' + str(rawMinIntString) + '.' + \
                '0x' + rawMstrHexString + rawUcdHexString + rawIvsHexString + \
                rawBbuHexString

            updatePassOrFail = True

        except Exception, e:
            UtilLogger.verboseLogger.error('PsuFwInfo.UpdatePsuFwVersion:' + \
                ' failed to update PSU FW Version with exception: ' + str(e))
            updatePassOrFail = False

        return updatePassOrFail

    # Function will return whether image is active or inactive and PSU version
    # Inputs:
    #   interfaceParams (list of strings): base parameters used to interface with IpmiUtil
    #   imageType (int): FW Bootloader (0) or FW Image A (1) or FW Image B (2)
    # Outputs:
    #   getPassOrFail (bool): get successful
    #   activeOrInactive (bool): image is active (True) or inactive (False)
    #   psuVersion (list of strings): PSU FW Image (default value: empty list) 
    def GetPsuFwVersionInfo(self, interfaceParams, imageType):

        # Initialize variables
        getPassOrFail = False
        activeOrInactive = False
        psuVersion = []

        # Check if FW Image is active via Read_FW_Info
        # BMC will get PSU active image status using READ_FW_INFO PSU commadn via PMBus
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, Config.netFnApp, \
            Config.cmdMasterWriteRead, [ '03', 'B0', '0A', 'EF', '01', \
            self.imageTypeDict[imageType][1]])
        if cmdPassOrFail and \
            int(respData[0], 16) == self.pmbReadFwInfoRespLen \
            and len(respData[1:]) == self.pmbReadFwInfoRespLen:

            # Check whether image is active or inactive
            if respData[1] == '01': # image is active
                getPassOrFail = True
                activeOrInactive = True
                psuVersion = respData[2:]
                UtilLogger.verboseLogger.info('PsuFwInfo.GetPsuFwVersionInfo ' + \
                    '(READ_FW_INFO): command passed.' + \
                    ' PSU ' + self.imageTypeDict[imageType][0] + ' is active image.' + \
                    ' PSU FW Version: ' + str(psuVersion))
            elif respData[1] == '00': # image is inactive
                getPassOrFail = True
                psuVersion = respData[2:]
                UtilLogger.verboseLogger.info('PsuFwInfo.GetPsuFwVersionInfo ' + \
                    '(READ_FW_INFO): command passed.' + \
                    ' PSU ' + self.imageTypeDict[imageType][0] + ' is inactive image.' + \
                    ' PSU FW Version: ' + str(psuVersion))
            elif cmdPassOrFail:
                UtilLogger.verboseLogger.error('PsuFwInfo.GetPsuFwVersionInfo ' + \
                    '(READ_FW_INFO): command failed. Success completion code but ' + \
                    'unexpected response data: ' + \
                    str(respData))
            else:
                UtilLogger.verboseLogger.error('PsuFwInfo.GetPsuFwVersionInfo ' + \
                    '(READ_FW_INFO): command failed. Completion Code: ' + str(respData))

        return getPassOrFail, activeOrInactive, psuVersion

    # Function will return which image type is currently active
    # using PSU PMBus command Read_FW_Info
    def GetPsuActiveImageType(self, interfaceParams):

        # Initialize variables
        getPassOrFail = False
        imageType = None
        psuVersion = None

        # Check if FW Bootloader is active via Read_FW_Info
        # BMC will get PSU active image status using READ_FW_INFO PSU commadn via PMBus
        getImgBootPassOrFail,imgBootActiveOrInactive, psuVersion = \
            self.GetPsuFwVersionInfo(interfaceParams, self.psuImageTypeFwBootloader)
        
        # Check if FW Image A is active via Read_FW_Info
        # BMC will get PSU active image status using READ_FW_INFO PSU commadn via PMBus
        getImgAPassOrFail,imgAActiveOrInactive, psuVersion = \
            self.GetPsuFwVersionInfo(interfaceParams, self.psuImageTypeFwImageA)

        # Check if FW Image A is active via Read_FW_Info
        # BMC will get PSU active image status using READ_FW_INFO PSU commadn via PMBus
        getImgBPassOrFail, imgBActiveOrInactive, psuVersion = \
            self.GetPsuFwVersionInfo(interfaceParams, self.psuImageTypeFwImageB)

        if getImgBootPassOrFail and imgBootActiveOrInactive:
            getPassOrFail = True
            imageType = self.psuImageTypeFwBootloader
        if getImgAPassOrFail and imgAActiveOrInactive: # currently if, not elif
            getPassOrFail = True
            imageType = self.psuImageTypeFwImageA
        elif getImgBPassOrFail and imgBActiveOrInactive:
            getPassOrFail = True
            imageType = self.psuImageTypeFwImageB

        if getPassOrFail:
            UtilLogger.verboseLogger.info('PsuFwInfo.GetPsuActiveImageType:' + \
                'successfully determined active PSU image. Active PSU Image: ' + \
                self.imageTypeDict[imageType][0])
        else:
            UtilLogger.verboseLogger.error('PsuFwInfo.GetPsuActiveImageType:' + \
                'failed to determine active PSU image.')

        return getPassOrFail, imageType

    # Function will compare PSU FW version
    # and state which is newer
    # Inputs: 
    #   psuFw1 (PsuFwInfo object): PSU FW Info object
    #   psuFw2 (PsuFwInfo object): PSU FW Info object
    # Output:
    #   comparePassOrFail (bool): successfully compared FW versions (True) or not (False)
    #   compareOut:
    #       1: psuFw1 is newer (greater) than psuFw2
    #       0: psuFw1 and psuFw2 are equal
    #      -1: psuFw1 is older (less) than psuFw2
    def ComparePsuFwVersion(self, psuFw1, psuFw2):

        # Initialize Variables
        comparePassOrFail = False
        compareOut = 0
        psuFw1Obj = PsuFwInfo()
        psuFw1Obj = psuFw1
        psuFw2Obj = PsuFwInfo()
        psuFw2Obj = psuFw2

        # Verify PSU FW Versions are compareable (ie valid versions provided)
        if psuFw1Obj.majorVersion is None or \
            psuFw2Obj.majorVersion is None:
            UtilLogger.verboseLogger.error('PsuFwInfo.ComparePsuFwVersion:' + \
                ' psuFw1 or psuFw2 have invalid inputs. Will not compare.')

        # Check if both PSU FW Versions are equal
        if psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion == psuFw2Obj.minorVersion and \
            psuFw1Obj.masterVersion == psuFw2Obj.masterVersion and \
            psuFw1Obj.ucdVersion == psuFw2Obj.ucdVersion and \
            psuFw1Obj.ivsVersion == psuFw2Obj.ivsVersion and \
            psuFw1Obj.bbuVersion == psuFw2Obj.bbuVersion:
            comparePassOrFail = True
        # Check if psuFw1 newer (greater) than psuFw2
        elif psuFw1Obj.majorVersion > psuFw2Obj.majorVersion or \
            (psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion > psuFw2Obj.minorVersion) or \
            (psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion == psuFw2Obj.minorVersion and \
            psuFw1Obj.masterVersion > psuFw2Obj.masterVersion) or \
            (psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion == psuFw2Obj.minorVersion and \
            psuFw1Obj.masterVersion == psuFw2Obj.masterVersion and \
            psuFw1Obj.ucdVersion > psuFw2Obj.ucdVersion) or \
            (psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion == psuFw2Obj.minorVersion and \
            psuFw1Obj.masterVersion == psuFw2Obj.masterVersion and \
            psuFw1Obj.ucdVersion == psuFw2Obj.ucdVersion and \
            psuFw1Obj.ivsVersion > psuFw2Obj.ivsVersion) or \
            (psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion == psuFw2Obj.minorVersion and \
            psuFw1Obj.masterVersion == psuFw2Obj.masterVersion and \
            psuFw1Obj.ucdVersion == psuFw2Obj.ucdVersion and \
            psuFw1Obj.ivsVersion == psuFw2Obj.ivsVersion and \
            psuFw1Obj.bbuVersion > psuFw2Obj.bbuVersion):
            comparePassOrFail = True
            compareOut = 1
        # Check if psuFw1 older (less) than psuFw2
        elif psuFw1Obj.majorVersion < psuFw2Obj.majorVersion or \
            (psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion < psuFw2Obj.minorVersion) or \
            (psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion == psuFw2Obj.minorVersion and \
            psuFw1Obj.masterVersion < psuFw2Obj.masterVersion) or \
            (psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion == psuFw2Obj.minorVersion and \
            psuFw1Obj.masterVersion == psuFw2Obj.masterVersion and \
            psuFw1Obj.ucdVersion < psuFw2Obj.ucdVersion) or \
            (psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion == psuFw2Obj.minorVersion and \
            psuFw1Obj.masterVersion == psuFw2Obj.masterVersion and \
            psuFw1Obj.ucdVersion == psuFw2Obj.ucdVersion and \
            psuFw1Obj.ivsVersion < psuFw2Obj.ivsVersion) or \
            (psuFw1Obj.majorVersion == psuFw2Obj.majorVersion and \
            psuFw1Obj.minorVersion == psuFw2Obj.minorVersion and \
            psuFw1Obj.masterVersion == psuFw2Obj.masterVersion and \
            psuFw1Obj.ucdVersion == psuFw2Obj.ucdVersion and \
            psuFw1Obj.ivsVersion == psuFw2Obj.ivsVersion and \
            psuFw1Obj.bbuVersion < psuFw2Obj.bbuVersion):
            comparePassOrFail = True
            compareOut = -1
        else: # otherwise, failed to compare PSU FW versions
            comparePassOrFail = False

        return comparePassOrFail, compareOut


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
            self.actions_target = self.all_data.get("PowerSupplies")[psu_index].get("Actions").get("Oem") \
                .get("OcsBmc.v1_0_0##PowerSupply.ClearFaults").get("target")
            self.firmwareversion = self.all_data.get("PowerSupplies")[psu_index].get("FirmwareVersion")
            self.manufacturer = self.all_data.get("PowerSupplies")[psu_index].get("Manufacturer")
            self.memberid = self.all_data.get("PowerSupplies")[psu_index].get("MemberId")
            self.model = self.all_data.get("PowerSupplies")[psu_index].get("Model")
            self.name = self.all_data.get("PowerSupplies")[psu_index].get("Name")
            self.partnumber = self.all_data.get("PowerSupplies")[psu_index].get("PartNumber")
            self.powercapacitywatts = self.all_data.get("PowerSupplies")[psu_index].get("PowerCapacityWatts")
            self.relateditem_odata_id = self.all_data.get("PowerSupplies")[psu_index].get("RelatedItem")[0].get(
                "@odata.id")
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
