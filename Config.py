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

# region Constants
utilVersion = '2.00'

# region General Network Function Codes (NetFn; in hex string)
netFnChassis = '00'
netFnSensor = '04'
netFnApp = '06'
netFnStorage = '0A'
netFnTransport = '0C'
netFnDcmi = '2C'
netFnOem2E = '2E'
netFnOem30 = '30'
netFnOem32 = '32'
netFnOem38 = '38'
# endregion

# region BladeAPI Command Numbers (Cmd; in hex string)
cmdGetDeviceId = '01'
cmdColdReset = '02'
cmdGetSystemGuid = '37'
cmdGetChannelAuthenticationCapabilities = '38'
cmdGetSessionChallenge = '39'
cmdActivateSession = '3A'
cmdSetSessionPrivilegeLevel = '3B'
cmdCloseSession = '3C'
cmdGetSessionInfo = '3D'
cmdSetUserName = '45'
cmdGetUserName = '46'
cmdSetUserPassword = '47'
cmdSetChannelSecurityKeys = '56'
cmdGetMessage = '33'
cmdSendMessage = '34'
cmdMasterWriteRead = '52'
cmdGetChassisStatus = '01'
cmdChassisControl = '02'
cmdChassisIdentify = '04' 
cmdSetPowerRestorePolicy = '06' 
cmdSetPowerCycleInterval = '0B' 
cmdSetSystemBootOptions = '08' 
cmdGetSystemBootOptions = '09' 
cmdGetSensorReadingFactors = '23' 
cmdSetSensorThresholds = '26'
cmdGetSensorThresholds = '27'
cmdGetSensorReading = '2D' 
cmdGetSensorType = '2F'
cmdReadFruData = '11' 
cmdWriteFruData = '12' 
cmdReserveSdrRepository = '22' 
cmdGetSdr = '23' 
cmdReserveSel = '42' 
cmdGetSelEntry = '43' 
cmdAddSelEntry = '44'
cmdClearSel = '47' 	
cmdGetSelTime = '48'
cmdSetSelTime = '49'
cmdSetLanConfigurationParameters = '01'
cmdGetLanConfigurationParameters = '02'
cmdGetPowerReading = '02'
cmdGetPowerLimit = '03'
cmdSetPowerLimit = '04'
cmdActivatePowerLimit = '05'
cmdSetProcessorInfo = 'F0'
cmdGetProcessorInfo = '1B'
cmdSetMemoryInfo = 'F1'
cmdGetMemoryInfo = '1D'
cmdSetPcieInfo = 'F2'
cmdGetPcieInfo = '1A'
cmdSetNicInfo = 'F3'
cmdGetNicInfo = '19'
cmdSetEnergyStorage = '22'
cmdGetEnergyStorage = '23'
cmdActivateDeactivatePsuAlert = '24'
cmdSetDefaultPowerLimit = '25'
cmdGetDefaultPowerLimit = '26'
cmdSetPsuAlert = '27'
cmdGetPsuAlert = '28'
cmdSetNvDimmTrigger = '29'
cmdGetNvDimmTrigger = '2A'
cmdGetBiosCode = '73'
cmdMasterMuxedWriteRead = '53'
cmdSetBiosConfig = '74'
cmdGetBiosConfig = '75'
cmdSetBiosConfigInfo = '76'
cmdGetGpio = 'E1'
cmdSetGpio = 'E0'
cmdSetBiosVersion = 'F4'
cmdGetFirmwareVersion = '0B'
cmdGetPwmProfile = '78'
cmdSetPwmProfile = '79'
cmdProgramJtagDevice = '80'
cmdGetJtagProgramStatus = '81'
cmdGetTpmPhysicalPresence = '82'
cmdSetTpmPhysicalPresence = '83'
cmdConfigureFirmwareUpdate = '84'
cmdSetStorageMapping = '85'
cmdGetStorageMapping = '86'
cmdSetServiceConfiguration = '87'
cmdGetDiskStatus = 'C4'
cmdGetDiskInfo = 'C5'
cmdGetDiskErrorCount = 'C6'
cmdGetExpanderLog = 'C7'
cmdGetJbodDiagnostic = 'C8'
# endregion


# region File Paths
summaryLogPath = './'
summaryLogFileName = 'summary'
summaryLogFileExtension = '.log'

verboseLogPath = './'
verboseLogFileName = 'verbose'
verboseLogFileExtension = '.log'

# For processing test results and output to Excel file
outputDirectoryPath = "./"  # Directory path of output .xlsx Excel file.
defaultOutputExcelFile = "Output"  # Output .xlsx Excel file name.
outputExcelFileExtension = ".xlsx"  # Output Excel file name extension.

ipmiUtilFilePath = './ipmiutil-3.0.1-wcs/ipmiutil.exe'
ipmiUtilLinuxFilePath = './ipmiutil-3.0.1-wcs/Linux/ipmiutil'
socFlashFilePath = './socflash/socflash_x64.exe'
yafuFlashFilePath = './yafuflash/Yafuflash.exe'
yafuFlashLinuxFilePath = './yafuflash/Linux/Yafuflash'

biosTestFilePath = './WcsFileScripts/BIOSTEST.txt'
biosTestResultsPath = './WcsFileResults/BIOSTESTResults.txt'
C2010getGpioListFilePath = './C2010TestScripts/XmlFiles/getgpiolist.xml'
J2010getGpioListFilePath = './J2010TestScripts/XmlFiles/getgpiolist.xml'
J2010getGpioSlotIDFilePath = './J2010TestScripts/XmlFiles/getgpioslotid.xml'
J2010sensorListXmlFile = "./J2010TestScripts/XmlFiles/sensorlistxmlfile.xml"
G50getGpioListFilePath = './G50TestScripts/XmlFiles/getgpiolist.xml'
G50sensorListXmlFile = "./G50TestScripts/XmlFiles/sensorlistxmlfile.xml"

bmcNextBinFilePath = './FirmwareBin/Next/'
bmcPrevBinFilePath = './FirmwareBin/Prev/'
bmcFlashFilePath1 = "/var/wcs/home/image-bmc"
bmcFlashFilePath2 = "/var/wcs/home/image-bmc2"
expanderBinFilePath = './ExpanderFirmwareBin/'
expanderFlashFilePath = '/var/wcs/home/image-expander.fw'

cpldNextBinFilePath = './FirmwareBin/Next/'
cpldPrevBinFilePath = './FirmwareBin/Prev/'

psuFwImgANextBinFilePath = './FirmwareBin/Next/'
psuFwImgAPrevBinFilePath = './FirmwareBin/Prev/'
psuFwImgBNextBinFilePath = './FirmwareBin/Next/'
psuFwImgBPrevBinFilePath = './FirmwareBin/Prev/'

bmcStorNextBinFilePath = './FirmwareBin/Next/'
bmcStorPrevBinFilePath = './FirmwareBin/Prev/'

sftpUploadFilePath = '/var/wcs/home/'

# endregion

# region IPMI Constants

bmcBusId = '00'
bmcSlaveAddr = '20'
ipmbChannel = '06'
meSlaveAddr = '2C'
meLun = '00'
ipmiPort = 623

# endregion

# region BMC Platform constants

bmcPlatformC2010Value = 'C2010'
bmcPlatformJ2010Value = 'J2010'
bmcPlatformG50Value = 'G50'

# endregion

# region IpmiUtil constants

# region IpmiUtil switches and values

ipmiUtilInterfaceSwitch = '-F'
ipmiUtilInterfaceLanPlusValue = 'lan2'
ipmiUtilIpAddressSwitch = '-N'
ipmiUtilUserNameSwitch = '-U'
ipmiUtilPasswordSwitch = '-P'
ipmiUtilPrivilegeSwitch = '-V'
ipmiUtilPrivilegeAdminValue = '4'

ipmiUtilSendMsgMaxRetries = 5

# endregion

# region VerifyGetNicInfo constants

maxNicIndex = 1

# allow 0xCC completion code for the specified NIC index
getNicInfoAllowCC = [False, True]
# endregion

# region FwFlash variables

# region SocFlash switches and values
socFlashCSSwitch = 'cs='
socFlashBinPathSwitch = 'if='
socFlashOptionSwitch = 'option='
socFlashOptionValue = 'lr'
socFlashFlashTypeSwitch = 'flashtype='
socFlashFlashTypeBmcValue = '2'
socFlashLpcPortSwitch = 'lpcport='
socFlashLpcPortValue = '0x2e'
# endregion

# region YafuFlash switches and values
yafuFlashKcsSwitch = '-kcs'
yafuFlashLanSwitch = '-nw'
yafuFlashForceFlashSwitch = '-fb'
yafuFlashNetfnSwitch = '-netfn'
yafuFlashNetfnBmcValue = '0x34'
yafuFlashNetfnCpldValue = '0x34'
yafuFlashChipSelectSwitch = '-mse'
yafuFlashChipSelectDefaultValue = '1'
yafuFlashChipSelect0Value = '1'
yafuFlashChipSelect1Value = '2'
yafuFlashPeripheralSwitch = '-d'
yafuFlashPeripheralCpldValue = '4'
yafuFlashIpAddressSwitch = '-ip'
yafuFlashUserSwitch = '-U'
yafuFlashPasswordSwitch = '-P'
# endregion

# region Configure Firmware Update variables
biosFwUpdateTimeLimit = 120  # in seconds
psuFwUpdateTimeLimit = 3600  # in seconds
psuFwUpdatePollStatusInterval = 30  # in seconds
# endregion

# region AcPowerIpSwitch Constants
acPowerIpSwitchSsnEn = False
acPowerIpSwitchIpAddress = ''
acPowerIpSwitchPort = '80'
acPowerIpSwitchUserName = 'admin'
acPowerIpSwitchPassword = 'admin'
acPowerIpSwitchOutlet = 1
# endregion

# region Ssh Constants
sshPort = 22
httpRedfishPort = 443
sshRedfishResponseLimit = 180  # this is default value for J2010. For G50 test should pass the timeout value to the method
applyFirmwareResponseLimit = 1800  # in seconds
J2010sshPorts = [2200, 2201, 2202, 2203]
J2010seId = 1
J2010driveID = 1
PCIeDeviceID = 1
J2010allSeIDs = [1, 2, 3, 4]
sshResponseLimit = 10 
sshTimeout = 60
httpTimeout = 180
# endregion

# region Helper Constants
bmcHangRetryCount = 3
getChassisStatusLimitInSeconds = 10
# endregion

# region BMC Constants
BmcSslEn = True
BmcVerifyCert = False
# endregion

# region C2010 TestScripts Constants

# region FirmwareDecompressionTest constants
fwDecompressionTestLimit = 120  # in seconds
# endregion

# region VerifyDefaultGetBiosConfig constants
defaultCurrentBiosConfiguration = 0  # Wcs flavor [3:0], configuration 1 [6:4]
defaultChosenBiosConfiguration = 0  # Wcs flavor [3:0], configuration 1 [6:4]
# endregion

# region VerifyDefaultGetDefaultPowerLimit constants
defaultDefaultPowerLimit = 250  # in Watts
defaultDelayInterval = 20  # in milliseconds
defaultBmcAction = 0
defaultAutoRemoveDpcDelay = 0
# endregion

# region VerifyDefaultGetPowerLimit constants
defaultPowerLimitExceptionAction = 0
defaultPowerLimit = 500  # in Watts
defaultPowerLimitCorrectionTime = 6000  # in milliseconds
defaultPowerLimitSamplingPeriod = 1  # in seconds
# endregion

# region VerifyDefaultGetEnergy constants
defaultGetEnergyStoragePresence = 0
defaultGetEnergyStorageEnergyState = 0
defaultGetEnergyStorageScalingFactor = 10  # in Joules
defaultGetEnergyStorageBackupEnergyBlade = 0
defaultGetEnergyStorageBackupEnergyNvdimm = 0
defaultGetEnergyStorageRollingCounter = 0
# endregion

# region VerifyDefaultGetNvDimmTrigger constants
defaultGetNvDimmTriggerAdrTriggerStatus = 0
defaultGetNvDimmTriggerAdrCompletePowerOffDelay = 5  # in seconds
defaultGetNvDimmTriggerNvDimmPresentPowerOffDelay = 160  # in seconds
# endregion

# region VerifyDefaultGetPsuAlert constants
defaultPsu1ThrottleNStatus = 0  # [6]
defaultRmThrottleEnNStatus = 0  # RM_THROTTLE_EN_N [6]
defaultBmcForceNmThrottleNStatus = 0  # BMC_FORCE_NM_THROTTLE_N [3:0]
# endregion

# region VerifyDefaultSetPowerRestorePolicy
defaultPowerRestorePolicySupport = 4  # chassis supports AC/mains returns [2]
# endregion

# region IpmiOverLanConcurrentStressTest constants
ipmiOverLanConcurrentThreadCount = 10
ipmiOverLanConcurrentThreadDuration = 300  # in seconds
# endregion

# region MixedTrafficStressTest constants
mixedTrafficStressHostFilePath = '/var/wcs/home/<InsertSFTPFileName>'
mixedTrafficStressLocalFilePath = '<InsertSFTPFilePath>'

J2010MixedTrafficStressHostFilePath = '/var/wcs/home/'
J2010MixedTrafficStressLocalFilePath = ''

G50MixedTrafficStressHostFilePath = '/var/wcs/home/'
G50MixedTrafficStressLocalFilePath = ''

mixedTrafficStressTestThreadDuration = 300  # in seconds
# endregion

# region TemperatureAndPowerStabilityStressTest constants
temperatureAndPowerStabilityErrorMargin = 10  # +/- error margin in percent

temperatureAndPowerStabilityTestThreadDuration = 300  # in secondsS
# endregion

# region AcPowerCycleStressTest constants
acPowerCycleStressTestTotalTime = 1  # in hours
acPowerCycleDecompressionLimit = 120  # in seconds
acPowerCycleStressTestExpectedSelsXmlFilePath = './C2010TestScripts/XmlFiles/accyclesellist.xml'
# Swtich Power On/Off method, set 0 for default method
#       0 - Using AC Power IP Switch
#       1 - Using Rack Manager
acPowerCycleStressTestPowerSwitchMethod = 0
# endregion

# region DcPowerCycleStressTest constants
dcPowerCycleStressTestTotalTime = 1  # in hours
dcPowerCycleStressTestExpectedSelsXmlFilePath = './C2010TestScripts/XmlFiles/dccyclesellist.xml'
# endregion

# region BmcResetStressTest constants
bmcResetStressTestTotalTime = 1  # in hours
bmcResetStressTestExpectedSelsXmlFilePath = './C2010TestScripts/XmlFiles/bmccoldresetsellist.xml'
# endregion

# region AddSelClearSelStressTest constants
addSelClearSelStressTestTotalTime = 0.5  # in hours
addSelClearSelStressTestEntriesLimit = 2048

#endregion

#region BmcMeStressTest constants

bmcMeStressTestTotalTime = 1 # in hours

#endregion

#region BmcDcmiStressTest constants

bmcDcmiStressTestTotalTime = 1 # in hours

bmcDcmiStressTestPollTime = 1 # in seconds

#endregion

#region ConcurrentStressTest constants

# endregion

# region BmcMeStressTest constants
bmcMeStressTestTotalTime = 1  # in hours
# endregion

# region ConcurrentStressTest constants
concurrentStressTestTotalTime = 1  # in hours
# endregion

# region IpmiOverLanOrKcsStressTest constants
ipmiOverLanOrKcsStressTestTotalTime = 1  # in hours
ipmiOverLanOrKcsStressTestSoftCycleSleepInSeconds = 30
# endregion

# region SensorReadingStressTest Constants.
# XML File that contains the list of all sensors to test.
# The directory path (absolute or relative) of the file may be included (if not included,
# it is assumed that the file is in the current directory.
# The file name must contain the file extension.
sensorListXmlFile = "./C2010TestScripts/XmlFiles/sensorlistxmlfile.xml"

# Duration of the sensor reading test (in seconds).
sensorReadingTestDuration = 300  # In seconds.
# endregion

# region SensorThresholdStressTest Constants
# XML File that contains the list of all sensors to test sensor thresholds.
# The directory path (absolute or relative) of the file may be included (if not included,
# it is assumed that the file is in the current directory.
# The file name must contain the file extension.
thresholdSensorListXmlFile = "./C2010TestScripts/XmlFiles/thresholdsensorlistxmlfile.xml"

# Duration of the sensor threhsold stress test (in seconds)

sensorThresholdStressTest = 300 # In seconds

#endregion

#region AcCycleAddSelClearSelStressTest Constants

acCycleAddSelClearSelStressTestTotalTime = 1 # in hours

acCycleAddSelClearSelStressTestBootProcessTimeout = 360 # in seconds

# Variable provides range for random sleep generator (in seconds)
# between AddSelClearSel starting and running Ac power cycle process
acCycleAddSelClearSelStressTestRandRange = [ 60, 240 ]

#endregion

#endregion

#region TestScripts Constants

sensorThresholdStressTest = 300  # In seconds

# endregion

# region TestScripts Constants
testThreadCount = 10
testThreadDuration = 300  # in seconds
# endregion

# region Shared Variables
bmcPlatform = None
debugEn = False
timestampEn = False
bmcIpAddress = ''
bmcUser = ''
bmcPassword = ''
currentOs = ''
bmcPrompt = ''
# endregion

# region Miscellaneous Variables
bmcFwDecompressionInSeconds = 20
acPowerOnSleepInSeconds = 120
acPowerOffSleepInSeconds = 10
bmcResetSleepInSeconds = 110
meResetSleepInSeconds = 20
dcPowerCycleSleepInSeconds = 30
bootToBiosStartScreenLimitInSeconds = 300
bootToBMCStartScreenLimitInSeconds = 300
bootToOsSleepInSeconds = 600
resetFirmwareToSleepInSeconds = 5
waitForFirmwareUpdate = 420
applyFirmwareToSleepInSeconds = 5
sftpCopyFileTimeout = 180
sftpDelayAfterTheCopy = 30
restAPICallTimeout = 180
sftpSleepTimeout = 600
ExpanderDiskStateChangeTime = 60            # Add for VerifyReadingExpanderEventLog.py
maxNumberOfSels = 2045 

osNameWindows = 'nt'
osNameLinux = 'posix'
folderThresholdPercent = 90  # Usage in percent
foldersToMonitor = [
    "/run/initramfs/rw",
    "/dev",
    "/run",
    "/dev/shm",
    "/sys/fs/cgroup",
    "/tmp",
    "/var/volatile",
    "/var/wcs/home",
]
# endregion


# J2010 constants
REDFISH_BASE_ADDRESS = 'redfish/v1'
SAMPLE_ITERATIONS = 2  # Used for the sample size of averaging URI response timing
FAILED_URI_RETRIES = 5  # Used for retrying a failed URI request

# region Rack Manager Configuration
RackManagerIPAddress = ''
RackManagerUsername = ''
RackManagerPassword = ''
BMCSlotIDOnRM = 0
# endregion
