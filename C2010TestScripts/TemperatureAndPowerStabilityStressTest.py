# PyTestUtil
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

import datetime
import os
import threading
import time

import Config
import Helper
import IpmiUtil
import Ssh
import UtilLogger

# Initialize global variables
threadLock = threading.Lock()
testPassOrFail = True
cpu0SensorId = None
cpu1SensorId = None
hsc0SensorId = None
cpu0SensorName = 'Temp_CPU0'
cpu1SensorName = 'Temp_CPU1'
hsc0SensorName = 'HSC0 Input Power'
startTemperature = 0 # in Degrees
startPower = 0 # in Watts
cpu0TjMax = 0 # in degrees
cpu1TjMax = 0 # in degrees
ipmiThreadCycleCount = 0
ipmiThreadCyclesPassed = 0
ipmiThreadCyclesFailed = 0
ipmiThreadDuration = None
stabilityThreadCycleCount = 0
stabilityThreadCyclesPassed = 0
stabilityThreadCyclesFailed = 0
stabilityThreadDuration = None

# Prototype Setup Function
def Setup(interfaceParams):

    # Declare module-scope variables
    global cpu0SensorId
    global cpu1SensorId
    global hsc0SensorId

    # Get Sel entries
    processCmd = ['sel', '-u']
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)
    out, err = IpmiUtil.RunIpmiUtil(processCmd)
    if err:
        UtilLogger.verboseLogger.error("TemperatureAndPowerStabilityStressTest.py: " + \
            "setup SEL entries error: " + str(err))
        setupSuccess = False
    else:
        UtilLogger.verboseLogger.info("TemperatureAndPowerStabilityStressTest.py: " + \
            "setup SEL entries: \n" + str(out))

    # Reserve Sel
    reservationId = []
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnStorage,\
        Config.cmdReserveSel, [])
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info("ReserveSel" + \
            ": Command passed: " + str(respData))
        reservationId = respData
    else:
        UtilLogger.verboseLogger.error("ReserveSel" + \
            ": Command failed. Completion Code: " + \
            str(respData))
    
    # Define sample raw bytes for Clear Sel
    # Raw bytes defined as Initiate Erase
    rawBytesList = []
    for appendByte in reservationId:
        rawBytesList.append(appendByte)
    rawBytesList.append('43')
    rawBytesList.append('4C')
    rawBytesList.append('52')
    rawBytesList.append('AA')

    # Clear Sel
    cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
        interfaceParams, Config.netFnStorage,\
        Config.cmdClearSel,\
        rawBytesList)
    if cmdPassOrFail:
        UtilLogger.verboseLogger.info("ClearSel" + \
            ": Command passed: " + str(respData))
    else:
        UtilLogger.verboseLogger.error("ClearSel" + \
            ": Command failed. Completion Code: " + \
            str(respData))
    
    # Get Cpu 0 Temperature Sensor ID
    parseSuccess, cpu0SensorId = IpmiUtil.GetIpmiUtilSensorId(interfaceParams, cpu0SensorName)
    if parseSuccess:
        UtilLogger.verboseLogger.info("TemperatureAndPowerStabilityStressTest.Setup" + \
            ": successfully parsed " + cpu0SensorName + " sensor ID: " + cpu0SensorId)
    else:
        UtilLogger.verboseLogger.error("TemperatureAndPowerStabilityStressTest.Setup" + \
            ": unable to parse " + cpu0SensorName + " sensor ID. Will not continue test.")
        return False

    # Get Cpu 1 Temperature Sensor ID
    parseSuccess, cpu1SensorId = IpmiUtil.GetIpmiUtilSensorId(interfaceParams, cpu1SensorName)
    if parseSuccess:
        UtilLogger.verboseLogger.info("TemperatureAndPowerStabilityStressTest.Setup" + \
            ": successfully parsed " + cpu1SensorName + " sensor ID: " + cpu1SensorId)
    else:
        UtilLogger.verboseLogger.error("TemperatureAndPowerStabilityStressTest.Setup" + \
            ": unable to parse " + cpu1SensorName + " sensor ID. Will not continue test.")
        return False

    # Get HSC 0 Input Power Sensor ID
    parseSuccess, hsc0SensorId = IpmiUtil.GetIpmiUtilSensorId(interfaceParams, hsc0SensorName)
    if parseSuccess:
        UtilLogger.verboseLogger.info("TemperatureAndPowerStabilityStressTest.Setup" + \
            ": successfully parsed " + hsc0SensorName + " sensor ID: " + hsc0SensorId)
    else:
        UtilLogger.verboseLogger.error("TemperatureAndPowerStabilityStressTest.Setup" + \
            ": unable to parse " + hsc0SensorName + " sensor ID. Will not continue test.")
        return False

    return True

# Function will run single iteration of 
# Temperature and Power Stability Test
def Execute(interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail

    # Define Test variables
    testPassOrFail = True
    threadDuration = Config.temperatureAndPowerStabilityTestThreadDuration # in seconds
    threads = []

    try:

        # Create new threads
        ipmiThread = threading.Thread(name='ipmiThread', target=runIpmiTest, \
            args=(threadDuration, interfaceParams,))
        checkStabilityThread = threading.Thread(\
            name='checkStabilityThread', target=runCheckStabilityTest, \
            args=(threadDuration, interfaceParams))

        # Start threads
        UtilLogger.verboseLogger.info(\
            "TemperatureAndPowerStabilityStressTest.py: starting " + \
            "ipmiThread and checkStabilityThread")
        ipmiThread.start()
        checkStabilityThread.start()

        # Add threads to thread list
        threads.append(ipmiThread)
        threads.append(checkStabilityThread)

        # Wait for all threads to complete
        for testThread in threads:
            testThread.join()

        # Log Statistics
        

        # Log Summary and Statistics
        UtilLogger.verboseLogger.info("")
        UtilLogger.verboseLogger.info(\
            "SUMMARY OF IPMI THREAD (TemperatureAndPowerStabilityStressTest) - " + \
            " Cycles Run: " + str(ipmiThreadCycleCount) + \
            " Cycles Passed: " + str(ipmiThreadCyclesPassed) + \
            " Cycles Failed: " + str(ipmiThreadCyclesFailed) + \
            " Ipmi Thread Duration: " + str(ipmiThreadDuration))
        UtilLogger.verboseLogger.info("")
        UtilLogger.verboseLogger.info(\
            "SUMMARY OF STABILITY THREAD (TemperatureAndPowerStabilityStressTest) - " + \
            " Cycles Run: " + str(stabilityThreadCycleCount) + \
            " Cycles Passed: " + str(stabilityThreadCyclesPassed) + \
            " Cycles Failed: " + str(stabilityThreadCyclesFailed) + \
            " Ipmi Thread Duration: " + str(stabilityThreadDuration))
        UtilLogger.verboseLogger.info("")

    except Exception, e:
        UtilLogger.verboseLogger.error("TemperatureAndPowerStabilityStressTest.py: " + \
            " Test failed with exception - " + str(e))
        testPassOrFail = False

    return testPassOrFail

# Prototype Cleanup Function
def Cleanup(interfaceParams):

    cleanupSuccess = True

    # Get Sel entries
    processCmd = ['sel', '-u']
    for interfaceParam in interfaceParams:
        processCmd.append(interfaceParam)
    out, err = IpmiUtil.RunIpmiUtil(processCmd)
    if err:
        UtilLogger.verboseLogger.error("TemperatureAndPowerStabilityStressTest.py: " + \
            "setup SEL entries error: " + str(err))
        cleanupSuccess = False
    else:
        UtilLogger.verboseLogger.info("TemperatureAndPowerStabilityStressTest.py: " + \
            "setup SEL entries: \n" + str(out))

    # Detect and Remove BMC Hang
    cleanupSuccess &= Helper.DetectAndRemoveBmcHang(interfaceParams)

    return cleanupSuccess

# Function will run Ipmi over LAN+ commands
def runIpmiTest(duration, interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail
    global ipmiThreadCycleCount
    global ipmiThreadCyclesPassed
    global ipmiThreadCyclesFailed
    global ipmiThreadDuration

    # Initialize variables
    threadPassOrFail = True

    # run Ipmi over LAN+ test
    startTime = time.time()
    totalTestTime = startTime + duration

    while time.time() < totalTestTime:

        # Initialize variables
        cyclePassOrFail = True

        # Get Device Id
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnApp,
            Config.cmdGetDeviceId, [])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetDeviceId" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("GetDeviceId" + \
                ": Command failed. Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Get Sdr
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdGetSdr, [ '00', '00', '00', '00', '00', 'FF' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetSdr" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("GetSdr" + \
                ": Command failed. Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Read Fru Data
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdReadFruData, [ '00', '00', '00', '08' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("ReadFruData" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("ReadFruData" + \
                ": Command failed. Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Get Power Reading
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnDcmi,\
            Config.cmdGetPowerReading, [ 'DC', '01', '01', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetPowerReading" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("GetPowerReading" + \
                ": Command failed. Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Set Next Boot to BIOS Setup
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '18', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                ": Command passed for set next boot to Bios Setup: " + \
                str(respData))
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                ": Command failed for set next boot to Bios Setup." + \
                " Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Set Next Boot to EFI
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '00', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                ": Command passed for set next boot to EFI: " + \
                str(respData))
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                ": Command failed for set next boot to EFI." + \
                " Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Set Next Boot to PXE
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '04', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                ": Command passed for set next boot to PXE: " + \
                str(respData))
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                ": Command failed for set next boot to PXE." + \
                " Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail
            
        # Set Next Boot to Hard Disk
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnChassis,\
            Config.cmdSetSystemBootOptions,\
            [ '05', 'A0', '08', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("SetSystemBootOptions" + \
                ": Command passed for set next boot to Hard Disk: " + \
                str(respData))
        else:
            UtilLogger.verboseLogger.error("SetSystemBootOptions" + \
                ": Command failed for set next boot to Hard Disk." + \
                " Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Get Sel Entry
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd(\
            interfaceParams, Config.netFnStorage,\
            Config.cmdGetSelEntry, [ '00', '00', '00', '00', '00', 'FF' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info("GetSelEntry" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error("GetSelEntry" + \
                ": Command failed. Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Get Processor Info
        cmdPassOrFail = True
        for idx in range(0, 2):
            # Set rawByte to cpu index
            cpuIdx = hex(idx).lstrip('0x')
            if idx == 0:
                cpuIdx = '0'
            # Send raw bytes via IpmiUtil
            cpuPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
                Config.netFnOem30, Config.cmdGetProcessorInfo, [ cpuIdx ])
            if cpuPassOrFail:
                UtilLogger.verboseLogger.info("GetProcessorInfo" + \
                    ": Command passed for cpu 0x"\
                    + cpuIdx + ": " + str(respData))
            else:
                UtilLogger.verboseLogger.error("GetProcessorInfo" + \
                    ": Command failed for cpu 0x" + cpuIdx + \
                    ". Completion Code: " + str(respData))
            cmdPassOrFail &= cpuPassOrFail
        cyclePassOrFail &= cmdPassOrFail

        # Get Memory Info
        cmdPassOrFail = True
        for idx in range(0, 25):
            # Set rawByte to memory index
            dimmIdx = hex(idx).lstrip('0x')
            if idx == 0:
                dimmIdx = '0'
            dimmPassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
                Config.netFnOem30, Config.cmdGetMemoryInfo, [ dimmIdx ])
            if dimmPassOrFail:
                UtilLogger.verboseLogger.info("GetMemoryInfo" + \
                    ": Command passed for dimm 0x"\
                    + dimmIdx + ": " + str(respData))
            else:
                UtilLogger.verboseLogger.error("GetMemoryInfo" + \
                    ": Command failed for dimm 0x" + dimmIdx + \
                    ". Completion Code: " + str(respData))
            cmdPassOrFail &= dimmPassOrFail
        cyclePassOrFail &= cmdPassOrFail

        # Get Pcie Info
        for idx in range(0, 22):
            pcieIdx = hex(idx).lstrip('0x')
            if idx == 0:
                pcieIdx = '0'
            pciePassOrFail, respData = IpmiUtil.SendRawCmd(interfaceParams, \
                Config.netFnOem30, Config.cmdGetPcieInfo, [ pcieIdx ])
            if pciePassOrFail:
                UtilLogger.verboseLogger.info("GetPcieInfo" + \
                    ": Command passed for pcie 0x"\
                    + pcieIdx + ": " + str(respData))
            else:
                UtilLogger.verboseLogger.error("GetPcieInfo" + \
                    ": Command failed for pcie 0x" + pcieIdx + \
                    ". Completion Code: " + str(respData))
            cmdPassOrFail &= pciePassOrFail
        cyclePassOrFail &= cmdPassOrFail

        # Get Nic Info
        cyclePassOrFail &= IpmiUtil.VerifyGetNicInfo(interfaceParams)

        # Send Message: Get CPU and Memory Temperature
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', '4B', '57', '01', '00', '03', \
            'FF', 'FF', 'FF', 'FF', '00', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Get CPU and Memory Temperature)" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Get CPU and Memory Temerature)" + \
                ": Command failed. Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Send Message: Set NM Power Draw Range to 200 W max
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
            '00', '00', 'C8', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set NM Power Draw Range)" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set NM Power Draw Range)" + \
                ": Command failed. Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Send Message: Set Intel NM Parameter to enable Fast NM Limiting
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
            '00', '00', '00', '00', '01', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set Intel NM Parameter)" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set Intel NM Parameter)" + \
                ": Command failed. Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Send Message: Set NM Power Draw Range to max
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'CB', '57', '01', '00', '03', \
            '00', '00', 'FF', '7F' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set NM Power Draw Range)" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set NM Power Draw Range)" + \
                ": Command failed. Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Send Message: Set Intel NM Parameter to disable Fast NM Limiting
        cmdPassOrFail, respData = IpmiUtil.SendRawCmd2ME(interfaceParams, \
            [ '00', '20', 'B8', 'F9', '57', '01', '00', '07', \
            '00', '00', '00', '00', '00', '00', '00', '00' ])
        if cmdPassOrFail:
            UtilLogger.verboseLogger.info(\
                "Send Message (Set Intel NM Parameter)" + \
                ": Command passed: " + str(respData))
        else:
            UtilLogger.verboseLogger.error(\
                "Send Message (Set Intel NM Parameter)" + \
                ": Command failed. Completion Code: " + str(respData))
        cyclePassOrFail &= cmdPassOrFail

        # Log cycle results
        if cyclePassOrFail:
            UtilLogger.verboseLogger.info(\
                "TemperatureAndPowerStabilityTest.runIpmiTest: " + \
                "Cycle " + str(ipmiThreadCycleCount) + " passed.")
            ipmiThreadCyclesPassed += 1
        else:
            UtilLogger.verboseLogger.error(\
                "TemperatureAndPoewrStabilityTest.runIpmiTest: " + \
                "Cycle " + str(ipmiThreadCycleCount) + " failed.")
            ipmiThreadCyclesFailed += 1
        ipmiThreadCycleCount += 1
        threadPassOrFail &= cyclePassOrFail

    if threadPassOrFail:
        UtilLogger.verboseLogger.info(\
            "TemperatureAndPowerStabilityStressTest.runIpmiTest: " + \
            "runIpmiTest passed.")
    else:
        UtilLogger.verboseLogger.info(\
            "TemperatureAndPowerStabilityStressTest.runIpmiTest: " + \
            "runIpmiTest failed.")

    ipmiThreadDuration = datetime.timedelta(seconds=time.time() - startTime)

    # Update testPassOrFail
    threadLock.acquire()
    testPassOrFail &= threadPassOrFail
    threadLock.release()

    return

def runCheckStabilityTest(duration, interfaceParams):

    # Declare Module-Scope variables
    global threadLock
    global testPassOrFail
    global stabilityThreadCycleCount
    global stabilityThreadCyclesPassed
    global stabilityThreadCyclesFailed
    global stabilityThreadDuration

    # Initialize variables
    threadPassOrFail = True
    startCpuTemperatures = []
    monitorCpuTemperatures = []
    cpu0ErrorMax = 0
    cpu0ErrorMin = 0
    cpu1ErrorMax = 0
    cpu1ErrorMin = 0
    startPower = 0
    monitorPower = 0
    powerErrorMax = 0
    powerErrorMin = 0
    cycleCount = 0
    cyclesPassed = 0
    cyclesFailed = 0

    # Get initial CPU Temperatures
    readPassOrFail, startCpuTemperatures = ReadCpuTemperatures(interfaceParams)
    if not readPassOrFail:
        UtilLogger.verboseLogger.error(\
            "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
            "unable to read intial CPU temperatures. Will not run test.")
        testPassOrFail = False
        return

    # Get Initial HSC0 Input Power
    readPassOrFail, startPower = ReadPower(interfaceParams)
    if not readPassOrFail:
        UtilLogger.verboseLogger.error(\
            "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
            "unable to read initial HSC0 Input Power. Will not run test.")
        testPassOrFail = False
        return

    # Get all error margins from initial temperatures and power
    cpu0ErrorMax, cpu0ErrorMin = GetErrorMargins(\
        startCpuTemperatures[0], Config.temperatureAndPowerStabilityErrorMargin)
    cpu1ErrorMax, cpu1ErrorMin = GetErrorMargins(\
        startCpuTemperatures[1], Config.temperatureAndPowerStabilityErrorMargin)
    powerErrorMax, powerErrorMin = GetErrorMargins(\
        startPower, Config.temperatureAndPowerStabilityErrorMargin)

    # Verify power reading is not within error margins of CPU temperatures
    if (startPower <= cpu0ErrorMax or startPower <= cpu1ErrorMax) and \
        (startPower >= cpu0ErrorMin or startPower >= cpu1ErrorMin):
        UtilLogger.verboseLogger.error(\
            "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
            "power reading within error margins of cpu temperatures. Test failed." + \
            " Hsc 0 Input Power: " + str(startPower) + " Watts. " + \
            " Cpu 0 Temperature: " + str(startCpuTemperatures[0]) + " degrees Celsius." + \
            " Cpu 0 Temperature Error Max: " + str(cpu0ErrorMax) + " degrees Celsius." + \
            " Cpu 0 Temperature Error Min: " + str(cpu0ErrorMin) + " degrees Celsius." + \
            " Cpu 1 Temperature: " + str(startCpuTemperatures[1]) + " degrees Celsius." + \
            " Cpu 1 Temperature Error Max: " + str(cpu1ErrorMax) + " degrees Celsius." + \
            " Cpu 1 Temperature Error Min: " + str(cpu1ErrorMin) + " degrees Celsius.")
        testPassOrFail = False
        return

    # run Check Temperature and Power Stability test
    startTime = time.time()
    totalTestTime = startTime + duration

    while time.time() < totalTestTime:

        # Initialize variables
        cyclePassOrFail = True

        # Read Cpu temperatures
        readPassOrFail, monitorCpuTemperatures = ReadCpuTemperatures(interfaceParams)
        if not readPassOrFail:
            UtilLogger.verboseLogger.error(\
                "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
                "unable to read CPU temperatures. Will not complete test cycle.")
            cyclePassOrFail = False
            continue
        
        # Verify CPU0 temperature within error margin
        if monitorCpuTemperatures[0] <= cpu0ErrorMax and \
            monitorCpuTemperatures[0] >= cpu0ErrorMin:
            UtilLogger.verboseLogger.info(\
                "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
                "CPU 0 Temperature within error margin of " + \
                str(Config.temperatureAndPowerStabilityErrorMargin) + "%. " + \
                "CPU 0 Temperature value: " + str(monitorCpuTemperatures[0]) + \
                " CPU 0 Temperature Error Max: " + str(cpu0ErrorMax) + \
                " CPU 0 Temperature Error Min: " + str(cpu0ErrorMin))
        else:
            UtilLogger.verboseLogger.info(\
                "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
                "CPU 0 Temperature NOT within error margin of " + \
                str(Config.temperatureAndPowerStabilityErrorMargin) + "%. " + \
                "CPU 0 Temperature value: " + str(monitorCpuTemperatures[0]) + \
                " CPU 0 Temperature Error Max: " + str(cpu0ErrorMax) + \
                " CPU 0 Temperature Error Min: " + str(cpu0ErrorMin))
            cyclePassOrFail = False

        # Verify CPU1 temperature within error margin
        if monitorCpuTemperatures[1] <= cpu1ErrorMax and \
            monitorCpuTemperatures[1] >= cpu1ErrorMin:
            UtilLogger.verboseLogger.info(\
                "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
                "CPU 1 Temperature within error margin of " + \
                str(Config.temperatureAndPowerStabilityErrorMargin) + "%. " + \
                "CPU 1 Temperature value: " + str(monitorCpuTemperatures[1]) + \
                " CPU 1 Temperature Error Max: " + str(cpu1ErrorMax) + \
                " CPU 1 Temperature Error Min: " + str(cpu1ErrorMin))
        else:
            UtilLogger.verboseLogger.info(\
                "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
                "CPU 1 Temperature NOT within error margin of " + \
                str(Config.temperatureAndPowerStabilityErrorMargin) + "%. " + \
                "CPU 1 Temperature value: " + str(monitorCpuTemperatures[1]) + \
                " CPU 1 Temperature Error Max: " + str(cpu1ErrorMax) + \
                " CPU 1 Temperature Error Min: " + str(cpu1ErrorMin))
            cyclePassOrFail = False

        # Read Power
        readPassOrFail, monitorPower = ReadPower(interfaceParams)
        if not readPassOrFail:
            UtilLogger.verboseLogger.error(\
                "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
                "unable to read HSC 0 Input Power. Will not complete test cycle.")
            cyclePassOrFail = False
            continue
                
        # Verify HSC 0 Input Power within error margin
        if monitorPower <= powerErrorMax and \
            monitorPower >= powerErrorMin:
            UtilLogger.verboseLogger.info(\
                "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
                "HSC 0 Input Power within error margin of " + \
                str(Config.temperatureAndPowerStabilityErrorMargin) + "%. " + \
                "HSC 0 Input Power value: " + str(monitorPower) + \
                " HSC 0 Input Power Error Max: " + str(powerErrorMax) + \
                " HSC 0 Input Power Error Min: " + str(powerErrorMin))
        else:
            UtilLogger.verboseLogger.info(\
                "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
                "HSC 0 Input Power NOT within error margin of " + \
                str(Config.temperatureAndPowerStabilityErrorMargin) + "%. " + \
                "HSC 0 Input Power value: " + str(monitorPower) + \
                " HSC 0 Input Power Error Max: " + str(powerErrorMax) + \
                " HSC 0 Input Power Error Min: " + str(powerErrorMin))
            cyclePassOrFail = False

        # Log test cycle results
        if cyclePassOrFail:
            UtilLogger.verboseLogger.info(\
                "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
                "Cycle " + str(stabilityThreadCycleCount) + " passed.")
            stabilityThreadCyclesPassed += 1
        else:
            UtilLogger.verboseLogger.error(\
                "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
                "Cycle " + str(stabilityThreadCycleCount) + " failed.")
            stabilityThreadCyclesFailed += 1
        stabilityThreadCycleCount += 1
        threadPassOrFail &= cyclePassOrFail
        
        # Sleep for 100 milliseconds
        time.sleep(0.1)

    if threadPassOrFail:
        UtilLogger.verboseLogger.info(\
            "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
            "runCheckStabilityTest passed.")
    else:
        UtilLogger.verboseLogger.info(\
            "TemperatureAndPowerStabilityStressTest.runCheckStabilityTest: " + \
            "runCheckStabilityTest failed.")

    stabilityThreadDuration = datetime.timedelta(seconds=time.time() - startTime)

    # Update testPassOrFail
    threadLock.acquire()
    testPassOrFail &= threadPassOrFail
    threadLock.release()

    return

# Function reads power
# Output:
#   bool: function success (True) or failure (False)
#   float: HSC 0 Input Power (in Watts)
def ReadPower(interfaceParams):

    # Initialize Variables
    hsc0Power = 0
    readPassOrFail = False

    # Get HSC 0 Power Reading using IpmiUtil sensor -i 36
    sensorPassOrFail, sensorReading = \
        IpmiUtil.GetIpmiUtilSensorReading(interfaceParams, hsc0SensorId, hsc0SensorName)

    # Verify response
    if sensorPassOrFail:
        UtilLogger.verboseLogger.info("ReadPower: " + \
            "successfully read HSC0 Input Power as " + \
            str(sensorReading) + " Watts.")
        hsc0Power = float(sensorReading)
        readPassOrFail = True
    else:
        UtilLogger.verboseLogger.error("ReadPower: " + \
            "unable to read HSC0 Input Power sensor reading.")

    return readPassOrFail, float(hsc0Power)

# Function reads temperatures of CPU0 and CPU1
# Output: 
#   bool: function success (True) or failure (False)
#   list (float): byte 0 - Cpu 0 Temp (in degrees celsius)
#               byte 1 - Cpu 1 Temp (in degrees celsius)
#               Note: list returns empty when bool is False
def ReadCpuTemperatures(interfaceParams):

    # Initialize Variables
    readPassOrFail = True
    cpuTemps = []

    # Get CPU 0 Temperature
    sensorPassOrFail, sensorReading = \
        IpmiUtil.GetIpmiUtilSensorReading(interfaceParams, \
        cpu0SensorId, cpu0SensorName)
    if sensorPassOrFail:
        UtilLogger.verboseLogger.info("ReadCpuTemperatures: " + \
            "successfully read Cpu 0 temperature as " + \
            str(sensorReading) + " degrees Celsius.")
        cpuTemps.append(float(sensorReading))
    else:
        UtilLogger.verboseLogger.error("ReadCpuTemperatures: " + \
            "unable to read Cpu 0 temperatuer.")
        readPassOrFail = False

    # Get CPU 1 Temperature
    sensorPassOrFail, sensorReading = \
        IpmiUtil.GetIpmiUtilSensorReading(interfaceParams, \
        cpu1SensorId, cpu1SensorName)
    if sensorPassOrFail:
        UtilLogger.verboseLogger.info("ReadCpuTemperatures: " + \
            "successfully read Cpu 1 temperature as " + \
            str(sensorReading) + " degrees Celsius.")
        cpuTemps.append(float(sensorReading))
    else:
        UtilLogger.verboseLogger.error("ReadCpuTemperatures: " + \
            "unable to read Cpu 1 temperature.")
        readPassOrFail = False

    return readPassOrFail, cpuTemps

# This function gets the max (target + errorMargin%)
# and min (target - errorMargin%) of target value
# Output:
#   max (float): target + error margin %
#   min (float): target - error margin %
def GetErrorMargins(target, errorMarginInPercent):

    # Initialize variables
    max = (100 + errorMarginInPercent) * 0.01 * target
    min = (100 - errorMarginInPercent) * 0.01 * target

    return max, min