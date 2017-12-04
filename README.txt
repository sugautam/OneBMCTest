----- OneBMCTest v2.00 -----

---- Getting Started ----

1- Copy utility to OS with Python 2.7 installed
  - Python 2.7.9 install package for Windows 64-bit provided 
    (Located in folder ./install as "python-2.7.9.amd64.msi")
  - NOTE: on Windows, add the installed Python directory
    to the PATH environment variable
2- If running OneBMCTest via KCS, the following package needs to be
   installed:
  - Visual C++ Redistributable for Visual Studio 2013 (32-bit)
    (Located in folder ./install as "vcredist_x86.exe")
3- The python module XlsxWriter is required.
  - To install the XlsxWriter module:
    - Module included in "PyTestModules" folder (XlsxWriter-0.9.3-py2.py3-none-any.whl)
	  - To install: 
	    - cd to PyTestModules folder
		- run: pip install XlsxWriter-0.9.3-py2.py3-none-any.whl
    - $ sudo pip install XlsxWriter
      (For Windows, 'sudo' is omitted)
4- In order to run J2010 or AC power cycling tests, the "requests"
   module for Python needs to be installed:
   (http://docs.python-requests.org/en/master/user/install/#install)
5- In order to run SSH or SFTP tests, the "paramiko"
   module for Python needs to be installed:
   (http://www.paramiko.org/installing.html)
6- Open command prompt and cd to OneBMCTest root directory
7- Run for usage help: python OneBMCTest.py -h

---- Example: Running tests via IPMI over LAN+ ----

1- Copy OneBMCTest to a machine that will remotely test 
   compute server blade via IPMI over LAN+
  - NOTE: Python 2.7 must be installed as instructed in 
    "Getting Started" section
2- Use 1 Gbps ethernet switch to connect network between 
   remote machine and compute blade with BMC
3- Connect Ethernet cable to BMC ethernet port and to 
   a USB network adapter
4- Use IPMI command "Set LAN Configuration Parameters" 
   to configure BMC to DHCP
5- Set dynamic IP address in BMC by resetting BMC
6- Verify BMC dynamic IP address is set by using IPMI command
   "Get LAN Configuration Parameters" and by pinging from machine
   that will run IpmiUtil ("ping <IpAddress>")
7- Note the BMC username (<BmcUser>) and BMC password (<BmcPassword>)
   that can be used to run IPMI over LAN+ commands on BMC
8- Open command prompt and cd to OneBMCTest folder
9- Run all functional tests: 
   python OneBMCTest.py -conn eth -ip <IpAddress> -user <BmcUser> -pwd <BmcPassword> -test a

---- Example: Running tests via KCS ----

1- Copy OneBMCTest to compute server blade
  - NOTE: Python 2.7 must be installed as instructed in 
    "Getting Started" section
2- Open command pormpt and cd to OneBMCTest folder
3- Run all functional tests:
   python OneBmcTest.py -conn kcs -test a

---- Example: Running tests via REST for J2010 ----

1- Copy OneBMCTest to a machine that will remotely test 
   compute server blade via REST API
  - NOTE: Python 2.7 must be installed as instructed in 
    "Getting Started" section
2- Use 1 Gbps ethernet switch to connect network between 
   remote machine and compute blade with BMC
3- Connect Ethernet cable to BMC ethernet port and to 
   a USB network adapter
4- Configure BMC to DHCP
5- Set dynamic IP address in BMC by resetting BMC
6- Verify BMC dynamic IP address is set by pinging from machine
   that will run OneBMCTest ("ping <IpAddress>")
7- Note the BMC username (<BmcUser>) and BMC password (<BmcPassword>)
   that can be used to run REST commands on J2010 BMC
8- Open command prompt and cd to OneBMCTest folder
9- Run all J2010 tests: 
   python OneBMCTest.py -plt J2010 -conn eth -ip <IpAddress> -user <BmcUser> -pwd <BmcPassword> -test a

---- Revision History ----

OneBMCTest v2.00 (11/20/2017)

1- Modified all files to remove references for PyTestUtil and 
   only include references of OneBMCTest
2- Renamed PyTestUtil.py to OneBMCTest.py
3- Renamed PyTestModules to PythonModules
4- Renamed and modified PyTestUtil documentation (docx file) so 
   that it only references OneBMCTest

PyTestUtil v1.13 (7/21/2017)

1- Added the following J2010 Test Scripts:
  - Get Channel Authentication Capabilities Test
2- Added the following G50 Test Scripts:
  - BMC FW Update Test
  - Get Channel Authentication Capabilities Test
  - REST Concurrent Stress Test
  - FRU Read/Write Test
  - REST Functional Test
3- Fixes made to the following J2010 Test Scripts:
  - GPIO Test
  - Mixed Traffic Stress Test
4- Fixes made to the following G50 Test Scripts:
  - Mixed Traffic Stress Test
5- Removed Slot ID usage in Redfish commands
6- Renamed J2010.py to Redfish.py since shared library between G50 and J2010
  - Made appropriate changes throughout utility

PyTestUtil v1.12 (6/16/2017)

1- Added support for G50 platform (ie can use switch '-plt G50')
2- Added the following G50 Test Scripts:
  - AC Power Cycle Stress Test
  - BMC Console Redirection Test
  - BMC Decompression Time Test
  - Check Folder Size Test
  - Get MAC Address Test
  - GPIO Test
  - Mixed Traffic Stress Test
3- Fixes made to the following J2010 Test Scripts:
  - Bmc FW Update Test
  - Expander Board Power Control
  - Expander Console Redirection Test
  - FRU Read Write Test
  - GPIO Test (also updated getpgiolist.xml)
  - Check Folder Size
4- J2010.py: POST/PATCH conversion fixes; JSON payload fixes; Redfish timeout changes
5- Ssh.py: SSH connection timeout fixes and fixes for parsing SSH output
6- Helper.py: added function for parsing regular expressions 
7- CliParser.py: added value 'G50' for '-plt' switch

PyTestUtil v1.11 (5/25/2017)

1- Added the following J2010 Test Scripts
  - Check Folder Size Test
  - Expander Console Redirection Test
2- Fixed J2010 Test Scripts
  - In Ssh.py file: Fixed the code bug by passing the port number to the calling methods.
  - In J2010.py file: Fixed code bugs. Port, username, password and  the JSON bodies in REST API POST and PATCH calls.
  - Update Redfish calls to use username/password instead of login
  - Added timeout parameter to HTTP calls
  - Increased timeout for BMC FW apply command to 1800 seconds
  - BmcFwUpdateTest: added logging
  - ExpanderConsoleRedirectionTest: added test for all 4 expanders
3- Updated C2010TestScripts/XmlFiles XML files
4- Corrected default value for VerifyDefaultGetPowerLimit

PyTestUtil v1.10 (4/4/2017)

1- Added the following J2010 Test Scripts:
  - BMC Console Redirection Test
  - BMC Expander Board Power Control Test
  - BMC Firmware Update Test
  - BMC Decompression Time Test
  - Event Logging Test
  - FRU Read/Write Test
  - Get MAC Address Test
  - GPIO Test
2- Added the following C2010 Test Scripts:
  - PSU Firmware Update Test
  - DC Power Up/Down Status Stress Test
  - DCMI Stress Test
3- Added several helper APIs in J2010.py
4- Added helper API to Helper.py to check BMC decompression time by
   getting Get Device Id response
5- Fixed GPIO list in getgpiolist.xml in C2010TestScripts
6- Added ConfigureFwUpdate class to IpmiUtil.py to provide APIs and variables
   for using IPMI command Configure Firmware Update
7- Added Psu.py to include helper APIs and variables for Gen 6 PSU
8- Added PsuFwInfo class to Psu.py to include 
   APIs for getting and parsing PSU FW version
9- Update Yafuflash binaries to v4.109

PyTestUtil v1.09 (1/17/2017):

1- Added the following J2010 Stress Scripts:
  - AC Power Cycle Stress Test
  - Mixed Traffic Stress Test
  - J2010 REST Concurrent Stress Test
2- Updated YafuFlash to v4.91
3- Updated IpmiUtil to latest v3.0.1
4- Modified IpmiUtil Send Message command so that in KCS there is a 100 ms delay 
   between Send Message and Get Message
5- Added SdrInfo class to IpmiUtil.py to parse Get SDR response, calculate sensor thresholds,
   and provide helper functions to calculate acceptable threshold range
6- Added retries to sending any Send Message commands so that PyTestUtil will retry 
   Send Message any time Node Busy 0xC0 completion code is received up to a limited number of retries.
7- Modified SshFunctionalTest script to first check for SAC prompt and then try executing command in blade
8- Modified BmcResetStressTest to allow for running in KCS.
9- Added stress test SensorThresholdStressTest that checks all sensors from a given XML file and
   continuosly verifies whether the sensor readings are within an acceptable thershold range.
10- Modified VerifyThresholdSensors function to validate against acceptable threshold range
	instead of nominal value.
11- Added folder "PyTestModules", which includes optional/required Python modules so that modules
    can be installed offline.
12- Added weekend run XML files "ipmioverlanscriptslist_weekendrun.xml" (IPMI over LAN+) and
    "kcsscriptslist_weekendrun.xml" (KCS)

PyTestUtil v1.08 (12/13/2016):

1- Added sensor reading stress test that validates
   all sensors located in specified XML file for being
   within an expected +/-% tolerance of a specified nominal value.
2- Added the following XML files in C2010TestScripts/XmlFiles:
  - sensorlistxmlfile.xml (sensor reading stress test XML file)
  - accyclesellist.xml (expected/optional SELs validated after AC power cycle)
  - dccyclesellist.xml (expected/optional SELs validated after DC power cycle)
  - bmcresetsellist.xml (expected/optional SELs validated after BMC Reset)
3- Modified the following XML files in C2010TestScripts/XmlFiles:
  - getgpiolist.xml (modified as fix for TFS Bug 62606)
4- Added CLI switch '-platform' to indicate whether current platform being
   tested is either 'C2010' or 'J2010'.
5- Created 'J2010TestScripts' folder and moved all previous test scripts/XML files
   to new 'C2010TestScripts' folder. Test scripts will be running from one of these
   folders based on the new '-platform' CLI switch.
6- Created the following J2010 test scripts (located in J2010TestScripts folder):
  - J2010RestFunctionTest
7- Created the following functions in IpmiUtil.py:
  - VerifyThresholdSensors(): function to verify sensor readings within +/-% tolerance
    specified in input XML file
  - VerifyGetNicInfo(): function to verify IPMI GetNicInfo completion code
8- Modified several C2010 test scripts to incorporate IpmiUtil.VerifyGetNicInfo() command
9- Added J2010TestScripts.xml as XML batch file for running J2010 test scripts

PyTestUtil v1.07 (10/19/2016):

1- Implemented feature to summarize verbose files and output to Excel
  - This feature is automatically run at the end of every test run, 
    and outputs a default Excel summary file.
  - This feature can be run independent of test runs:
    - use "-xli" and "-xlo" switches for independent Excel summary generation
2- Fixed issue with running FW Flash in Linux via LAN+
3- Updated getgpiolist.xml
4- Provided raw .py files instead of bytecode for all source files

PyTestUtil v1.06 (9/22/2016):

1- FirmwareDecompressionTest.py:
  - Fixed incorrect AC Power Cycle API calls
  - Removed usage of while loop
2- TemperatureAndPowerStabilityStressTest.py:
  - Removed reliance on SDR ID to get sensor reading
  - Added functions to IpmiUtil.py to help in getting SDR ID for a given sensor name
3- YafuFlashBmcFwUpdateTest.py:
  - Removed BMC FW file path verification as this was causing test to not run past Setup
4- Helper.py:
  - Removed verification of BMC SSH connection, which required checking of the "default route" string
5- Update Yafuflash to v4.84 and Socflash to v1.14

PyTestUtil v1.05 (9/15/2016):

1- Fixed successive iterations failing for:
  - DC Power Cycle Stress Test
  - AC Power Cycle Stress Test
  - BMC Reset Stress Test
2- Added retries for Bmc-Me Completion Code Smoke Test
3- Fixed issues with statistics logging
4- Fixed issues with test list duration
5- Fixed issues with detecting BIOS boot-up

PyTestUtil v1.04 (9/9/2016):

1- Added Functional Tests for:
  - Firmware Decompression
  - Bmc MAC Address verification
2- Added Stress Tests for:
  - Temperature and Power Stability
  - IPMI Over LAN+ Or KCS Concurrent Stress Test via Parallel Threads
3- Added Default Verification Tests for:
  - Get BIOS Config
  - Get Enery Storage
  - Get NVDIMM Trigger
  - Get Power Limit
  - Get PSU Alert
  - Set Power Restore Policy
4- Added Test Script DetectAndRemoveBmcHang to detect and remove
   BMC hang (added to testscriptslist.xml)
5- Added Helper.py to provide helpful general functions such as:
  - Detect and Remove BMC Hang
  - Ping and Check Response (gets time taken until successful ping)
  - Logging FW Decompression results (min, max and average)
  - SSH Boot to BIOS Start Screen and returning the duration
6- Modified all stress test scripts and certain functional test scripts
   to include Detect And Remove BMC Hang function in CleanUp function in 
   case the BMC hangs during test
7- Modified AC Power Cycle and BMC Reset scripts to check for 
   FW Decompression time
8- Modified AC/DC Power Cycle stress scripts to check for BIOS start screen
   and log the duration taken
9- Logging: summary and verbose logs will now be appended with timestamp 
   so that multiple instances of PyTestUtil can be run
10- Added switch '-verbosename' to change the name of verbose log file
	as <verbosename>_<timestamp>.log
11- Added switch '-timestamp' to enable printing timestamp on all verboselogger
    statements
12- Modified RunFwFlash function in FwFlash.py so that FW Flash tool outputs 
	(ie SocFlash or YafuFlash) are done in real-time when using '-debug' switch
13- Added defaulttestscriptslist.xml for scripts that are to be run to verify
	BMC Blade API default values
14- Fixed issue for RunFwFlash function in FwFlash.py where current working directory
	is set to root directory instead of the Fw Flash directory when running Fw Flash tool
15- Updated YafuFlash to version 4.71 and included UCOREW64.sys file
16- Updated gpiolist.xml to include all current GPIO pins
17- Added license headers to all source files and license.txt and thirdpartynotices.txt

PyTestUtil v1.03 (6/27/2016):

1- Added Functional Tests for:
  - SSH (including SAC verification) functional test
  - Extended BMC FW Update via Yafuflash 
    - Test now does: prev -> next, next -> next, next -> prev, prev -> prev
  - Added BMC FW Update via SocFlash for KCS
    - Test does: prev -> next, next -> next, next -> prev, prev -> prev
  - Read Sensor and Sels consecutively
  - Verify Backup BMC FW Update via Primary Image
  - BMC-ME Completion Code Smoke Test
2- Added Stress Tests for:
  - AC Power Cycle
  - BMC-ME interface
  - BMC Reset
  - DC Power Cycle
  - Mixed Traffic (SFTP/Ipmi over LAN+ concurrent stress)
3- Added APIs for updating BMC via SocFlash and comparing BMC FW versions
4- Added APIs for running console redirection commands via SSH
5- Changed GetMessage test script so that it only runs for KCS
6- Fixed test scripts so that send message has correct bytes for certain commands
7- Created install folder, which includes the following setup packages:
  - VC++ Redistributable for Visual Studio 2013 32-bit setup package 
  - Python 2.7.9 Windows 64-bit setup package
8- Made changes for README and PyTestUtil documentation to reflect changes
   in setup requirements
9- Added socflash and yafuflash (Windows x64 and Linux x64) binaries
10- Added XML file for running BMC-ME smoke tests (BmcMeSmokeTestScripts.xml)
11- Added ipmiutil for Linux x64 and made changes to automatically detect and run
    this version

PyTestUtil v1.02 (6/3/2016):

1- Added Functional Tests for:
  - BMC FW Update via YafuFlash for both LAN+ and KCS
  - CPLD FW Update via YafuFlash for both LAN+ and KCS
2- Added Stress test for adding and clearing BMC SELs from Flash
3- Added file YafuFlash.py for all APIs relating to running YafuFlash
4- Fixed IpmiUtil parsing issue as certain commands returning non-Success
   completion code was still seen as Success
5- Added FirmwareBin folder to house N ("Prev" folder) and N+1 ("Next" folder)
   firmware binaries
6- Replaced IpmiUtil-2.9.8 binaries wtih IpmiUtil-2.9.9 (located in ipmiutil-2.9.9-wcs folder)
  - Binaries contain fixes for Send Message and OEM Microsoft extension for running oem file scripts
7- Added HttpRequests.py to include functions for sending and getting Http requests/responses
8- Added AcPowerIpSwitch.py for functions that involve powering on/off the Ac Power IP Switch
   using HTTP GET requests
9- Added fwupdatetestsscriptslist.xml for all tests that involve testing fw update

PyTestUtil v1.01 (5/17/2016):

1- Added default value check test for Get Default Power Limit
2- Added instructions for installing VC++ package when 
   interfacing via KCS
3- Added the following stress tests:
  - IpmiOverLanOrKcsStressTest
  - ConcurrentStressTest
4- Added stress tests batch file stresstestscriptslist.xml
5- Added support for new xml attributes:
	- TestList.duration: duration of test cycle
	- TestList.iterations: number of test cycles
	- test.delay: number of seconds to delay running test script
6- Utility documentation: updated to include documentation on
   Xml Elements and attributes, and description for RunIpmiUtil function.

PyTestUtil v1.00 (5/10/2016):

1- Modified test script VerifyGetNicInfo to check for max Nic index
2- Added PyTestUtil documentation to package

PyTestUtil v0.09 (5/2/2016):

1- Added email support so that results can be sent out to a specified email/distribution address
   using the following added CLI parameters:
   - email: email address to send results to
   - sender: email address of sender
   - senderpwd: password for sender of email
   - server: SMTP server to use for sending email
   - port: SMTP port to use for sending email
2- Added summary log file that summarizes results and provides the number of tests passed,
   number of tests failed, and the tests that failed and number of times it failed
3- Added bmc version CLI parameter that can be used to indicate what BMC version is running the results
4- Added two additional loggers so that now each of the loggers do the following:
   - consoleLogger: outputs only to console
   - summaryLogger: outputs, console, summary.log, and verbose.log
   - verboseLogger: outputs only to verbose.log

PyTestUtil v0.08 (4/27/2016):

1- Added completion code tests for:
  - GetGpio
  - SetGpio
  - GetPwmProfile
  - GetChannelAuthenticationCapabilities
  - GetSessionChallenge
  - ActivateSession
  - SetSessionPrivilegeLevel
2- Implemented -xmlfilepath (-f) CLI parameter
   to specify which batch file to use for selecting 
   scripts to run from TestScripts folder
3- Added getgpiolist.xml, which is an XML file used
   by VerifyGetGpio.py test script to validate each specified
   GPIO pin number against GetGpio response
4- Added KCS support back to utility
5- Added shorthand switches for CLI interface (ie '-t' can be used for '-test')

PyTestUtil v0.07 (4/22/2016):

1- Added completion code tests for:
  - GetSelEntry
  - AddSelEntry
  - ClearSel
  - GetSelTime
  - SetSelTime
2- Implemented XML batch (testscriptslist.xml) for 
   Test Scripts using Ipmi over LAN+ interface
3- Added '-V 4' input parameter to LAN+ interface
   to fix privilege level issues
4- Moved all tests in FunctionalTests class to separate
   scripts in TestScripts folder
5- Removed support for running tests in FunctionalTests class
   via IPMI over LAN+ and KCS

PyTestUtil v0.06 (4/20/2016):

1- Added completion code tests for:
  - GetSensorThresholds
  - GetSensorReading
  - GetSensorType
  - ReadFruData
  - GetSdr
2- Implemented feature where test scripts can be added
   to TestScripts folder and will be automatically run
   when using the '-test as' input parameter.
   The scripts need to be structured to include a Setup,
   Execute, and Cleanup function, where each function will be automatically
   run.
3- Added completion code test for GetSdr to TestScripts folder as 
   example test that can be run using this feature.
4- Added TestScripts folder.

PyTestUtil v0.05 (4/15/2016):

1- Added completion code tests for:
  - GetChassisStatus
  - ChassisControl
  - ChassisIdentify
  - SetPowerCycleInterval
  - GetSystemBootOptions
2- Added IpmiUtil.py function to send raw packet to ME
   using the -m SendMessage IpmiUtil parameter
3- Added IpmiUtil.py function to invoke Wcs File extension
   command in IpmiUtil for executing commands stored in a text file
4- Removed IpmiUtil binaries from solution and instead added ipmiutil-2.9.8
   binaries, which include Wcs OEM extension
5- Added Bmc-BIOS communication test (ie BiosBmcFunctionalTest) 
   that invokes Wcs File OEM Extensions
6- Added WcsFileScripts folder to store all text files to be run using Wcs File extension
7- Added WcsFileResults folder to store output result text files 
   from running Wcs File IpmiUtil extension

PyTestUtil v0.04 (4/12/2016):

1- Added completion code tests for:
  - GetTpmPhysicalPresence
  - SetTpmPhysicalPresence
  - GetSystemGuid
  - GetMessage
  - SendMessage
  - MasterWriteRead
2- Modified SendRawCmd function
   to account for netFn being empty

PyTestUtil v0.03 (4/7/2016):

1- Added completion code tests for:
  - GetBiosCode
  - MasterMuxedWriteRead
  - SetBiosConfig
  - GetBiosConfig
  - SetBiosConfigInfo
  - SetBiosVersion
  - GetFirmwareVersion
2- Added all command numbers and 
   Network Function codes to Config.py 

PyTestUtil v0.02 (4/5/2016):

1- Added completion code tests for:
  - Get Memory Info
  - Set Memory Info
  - Get Processor Info
  - Set Processor Info
  - Get Pcie Info
  - Set Pcie Info
  - Get Nic Info
  - Set Nic Info
2- Changed '-cmd' CLI parameter to '-test'
3- Fixed IpmiUtil.py as there was an issue if command 
   does not provide response bytes but has 00 completion code
4- added config file to contain constants need by any other Python modules

PyTestUtil v0.01 (4/4/2016):

1- Initial Release
2- PyTestUtil.py: main functions and starting point of program
3- BladeAPI.py: classes for each BMC Blade API to act as interface when invoking request and response packets
4- CliParser.py: configures the CLI parsing that the utility uses (all CLI parameters are added here)
5- FunctionalTests.py: set of classes and functions that define each functional test that can be run by the utility. 
6- IpmiUtil.py: set of functions to use to invoke IpmiUtil commands (also parses IpmiUtil responses)
7- Program.py: invokes different functions based on the CLI parameters
8- testlist.xml: xml file that can be used to run certain functional/stress tests
9- UtilLogger.py: configures logging for utility
10- XmlParser: class that initializes Xml parsing for any xml file.