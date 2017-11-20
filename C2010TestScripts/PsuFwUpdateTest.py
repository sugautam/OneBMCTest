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

import Config
import IpmiUtil
import Psu
import UtilLogger

# Module-scope variables
currFwImageA = Psu.PsuFwInfo()
currFwImageB = Psu.PsuFwInfo()
prevFwImageA = Psu.PsuFwInfo()
prevFwImageB = Psu.PsuFwInfo()

nextBinFilePathIdx = 0
prevBinFilePathIdx = 1
currFwImgObjIdx = 2
prevFwImgObjIdx = 3

# Dictionary of PSU FW Image Type key (int): value (string list) pairs 
# that define PSU FW Bin paths and PSU FW Info objects for: 
# [ nextBinPath, prevBinPath, currentFwImageObject, previousFwImageObject ]
psuFwBinPathObjDict = { \
    Psu.PsuFwInfo.psuImageTypeFwImageA : \
    [ Config.psuFwImgANextBinFilePath, Config.psuFwImgAPrevBinFilePath, \
    currFwImageA, prevFwImageA ], \
    Psu.PsuFwInfo.psuImageTypeFwImageB : \
    [ Config.psuFwImgBNextBinFilePath, Config.psuFwImgBPrevBinFilePath, \
    currFwImageB, prevFwImageB ] \
    }

# Setup Function
# Update PSU FW to previous version
def Setup(interfaceParams):

    # Initialize variables
    setupPassOrFail = False

    # Update Image A and B
    setupPassOrFail = UpdatePsuFwImgAAndB(interfaceParams, prevBinFilePathIdx, \
        prevFwImgObjIdx)

    return setupPassOrFail

# Execute Function
def Execute(interfaceParams):

    # Declare module-scope variables
    global psuFwBinPathObjDict

    # Initialize variables
    executePassOrFail = True

    # Update Image A and B with next bin file
    executePassOrFail &= UpdatePsuFwImgAAndB(interfaceParams, nextBinFilePathIdx, \
        currFwImgObjIdx)

    # Compare Image A and Image B with previous update (in Setup())
    # Expected: current newer than previous
    executePassOrFail &= ComparePsuFwImg(Psu.PsuFwInfo.psuImageTypeFwImageA, 1)
    executePassOrFail &= ComparePsuFwImg(Psu.PsuFwInfo.psuImageTypeFwImageB, 1)

    # Update previous FW Info objects with current versions
    psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageA][prevFwImgObjIdx] = \
        psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageA][currFwImgObjIdx]
    psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageB][prevFwImgObjIdx] = \
        psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageB][currFwImgObjIdx]

    # Update Image A and B with next bin file
    executePassOrFail &= UpdatePsuFwImgAAndB(interfaceParams, nextBinFilePathIdx, \
        currFwImgObjIdx)

    # Compare Image A and B with previous update
    # Expected: current equal to previous
    executePassOrFail &= ComparePsuFwImg(Psu.PsuFwInfo.psuImageTypeFwImageA, 0)
    executePassOrFail &= ComparePsuFwImg(Psu.PsuFwInfo.psuImageTypeFwImageB, 0)

    # Update previous FW Info objects with current versions
    psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageA][prevFwImgObjIdx] = \
        psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageA][currFwImgObjIdx]
    psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageB][prevFwImgObjIdx] = \
        psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageB][currFwImgObjIdx]

    # Update Image A and B with previous bin file
    executePassOrFail &= UpdatePsuFwImgAAndB(interfaceParams, prevBinFilePathIdx, \
        currFwImgObjIdx)

    # Compare Image A and B with previous update
    # Expected: current older than previous
    executePassOrFail &= ComparePsuFwImg(Psu.PsuFwInfo.psuImageTypeFwImageA, -1)
    executePassOrFail &= ComparePsuFwImg(Psu.PsuFwInfo.psuImageTypeFwImageB, -1)

    # Update previous FW Info objects with current versions
    psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageA][prevFwImgObjIdx] = \
        psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageA][currFwImgObjIdx]
    psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageB][prevFwImgObjIdx] = \
        psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageB][currFwImgObjIdx]

    # Update Image A and B with previous bin file
    executePassOrFail &= UpdatePsuFwImgAAndB(interfaceParams, prevBinFilePathIdx, \
        currFwImgObjIdx)

    # Compare Image A and B with previous update
    # Expected: current older than previous
    executePassOrFail &= ComparePsuFwImg(Psu.PsuFwInfo.psuImageTypeFwImageA, 0)
    executePassOrFail &= ComparePsuFwImg(Psu.PsuFwInfo.psuImageTypeFwImageB, 0)

    # Update previous FW Info objects with current versions
    psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageA][prevFwImgObjIdx] = \
        psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageA][currFwImgObjIdx]
    psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageB][prevFwImgObjIdx] = \
        psuFwBinPathObjDict[Psu.PsuFwInfo.psuImageTypeFwImageB][currFwImgObjIdx]

    return executePassOrFail

# Cleanup Function
def Cleanup(interfaceParams):

    # Update Image A and B with next bin file
    cleanupPassOrFail = UpdatePsuFwImgAAndB(interfaceParams, nextBinFilePathIdx, \
        currFwImgObjIdx)

    return cleanupPassOrFail

# Function will provide available PSU FW for update
def GetAvailablePsuFw(interfaceParams):

    # Initialize variables
    getPassOrFail = False
    psuFwInfoObj = Psu.PsuFwInfo()

    # Get Active PSU FW Image Type
    getPassOrFail, activeImage = \
        psuFwInfoObj.GetPsuActiveImageType(interfaceParams)
    if getPassOrFail:
        if activeImage == Psu.PsuFwInfo.psuImageTypeFwImageA:
            activeImage = Psu.PsuFwInfo.psuImageTypeFwImageB
        elif activeImage == Psu.PsuFwInfo.psuImageTypeFwImageB:
            activeImage = Psu.PsuFwInfo.psuImageTypeFwImageA
        else: # default
            activeImage = Psu.PsuFwInfo.psuImageTypeFwImageA
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.GetAvailablePsuFw:' + \
            ' successfully determined image available for update.' + \
            ' Available Image Type: ' + Psu.PsuFwInfo.imageTypeDict[activeImage][0])
    else:
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.GetAvailablePsuFw:' + \
            ' failed to determine image available for update.' + \
            ' Available Image Type: ' + str(activeImage))
        activeImage = Psu.PsuFwInfo.psuImageTypeFwImageA # default

    return getPassOrFail, activeImage

# Function will compare current PSU FW Version for specified imageType
# with previous PSU FW Version for same imageType. Function will return
# True if current image is newer, older, or same as previous image as 
# specified in input.
def ComparePsuFwImg(imageType, expectedCompareOut):

    # Initialize variables
    comparePassOrFail = False

    # Compare current image and previous image
    psuFwInfoObj = Psu.PsuFwInfo()
    comparePassOrFail, compareOut = psuFwInfoObj.ComparePsuFwVersion(\
        psuFwBinPathObjDict[imageType][currFwImgObjIdx], \
        psuFwBinPathObjDict[imageType][prevFwImgObjIdx])
    if comparePassOrFail and compareOut == expectedCompareOut:
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.ComparePsuFwImg:' + \
            ' comparison passed. Current PSU FW Version ' + \
            Psu.PsuFwInfo.compareOutDict[expectedCompareOut] + \
            ' previous PSU FW Version. Image Type: ' + \
            Psu.PsuFwInfo.imageTypeDict[imageType][0] + '.' + \
            ' Current version: ' + \
            str(psuFwBinPathObjDict[imageType][currFwImgObjIdx].psuFwVersion) + '.' + \
            ' Previous version: ' + \
            str(psuFwBinPathObjDict[imageType][prevFwImgObjIdx].psuFwVersion))
    elif comparePassOrFail and compareOut != expectedCompareOut:
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.ComparePsuFwImg:' + \
            ' comparison failed. Current PSU FW Version ' + \
            Psu.PsuFwInfo.compareOutDict[compareOut] + \
            ' previous PSU FW Version. Expected ' + \
            Psu.PsuFwInfo.compareOutDict[expectedCompareOut] + '.' + \
            ' Image Type: ' + \
            Psu.PsuFwInfo.imageTypeDict[imageType][0] + '.' + \
            ' Current version: ' + \
            str(psuFwBinPathObjDict[imageType][currFwImgObjIdx].psuFwVersion) + '.' + \
            ' Previous version: ' + \
            str(psuFwBinPathObjDict[imageType][prevFwImgObjIdx].psuFwVersion))
        comparePassOrFail = False
    else:
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.ComparePsuFwImg:' + \
            ' comparison failed. Expected comparison: ' + \
            Psu.PsuFwInfo.compareOutDict[expectedCompareOut] + \
            ' . Image Type: ' + \
            Psu.PsuFwInfo.imageTypeDict[imageType][0] + '.' + \
            ' Current version: ' + \
            str(psuFwBinPathObjDict[imageType][currFwImgObjIdx].psuFwVersion) + '.' + \
            ' Previous version: ' + \
            str(psuFwBinPathObjDict[imageType][prevFwImgObjIdx].psuFwVersion))
        comparePassOrFail = False

    return comparePassOrFail

# Function will update PSU FW Image A and FW Image B
# It is expected that both versions will be updated in sequence
# and PSU will automatically switch from A to B or vice versa after update
def UpdatePsuFwImgAAndB(interfaceParams, binFilePathIdx, fwImgObjIdx):

    # Initialize variables
    funcPassOrFail = True
    compImageType1 = None # imageType for 1st update
    compImageType2 = None # imageType for 2nd update

    # Get PSU FW available for update
    getPassOrFail, imageType = GetAvailablePsuFw(interfaceParams)
    if not getPassOrFail:
        UtilLogger.verboseLogger.error(\
            'PsuFwUpdateTest.UpdatePsuFwImgAAndB:' + \
            ' failed to get available PSU FW for update.')
        funcPassOrFail = False
    else:
        compImageType1 = imageType

    # Update Available PSU FW image
    funcPassOrFail &= UpdatePsuFwAndVersion(interfaceParams, imageType, \
        binFilePathIdx, fwImgObjIdx)

    # Get PSU FW available for update
    getPassOrFail, imageType = GetAvailablePsuFw(interfaceParams)
    if not getPassOrFail:
        UtilLogger.verboseLogger.error(\
            'PsuFwUpdateTest.UpdatePsuFwImgAAndB:' + \
            ' failed to get available PSU FW for update.')
        funcPassOrFail = False
    else:
        compImageType2 = imageType

    # Update Available PSU FW image
    funcPassOrFail &= UpdatePsuFwAndVersion(interfaceParams, imageType, \
        binFilePathIdx, fwImgObjIdx)

    # Compare imageType from 1st update with imageType from 2nd update
    # Expect imageType to transition from Image A -> Image B or 
    # Image B -> Image A
    if funcPassOrFail and \
        (compImageType1 == Psu.PsuFwInfo.psuImageTypeFwImageA and \
        compImageType2 == Psu.PsuFwInfo.psuImageTypeFwImageB) or \
        (compImageType1 == Psu.PsuFwInfo.psuImageTypeFwImageB and \
        compImageType2 == Psu.PsuFwInfo.psuImageTypeFwImageA):
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.UpdatePsuFwImgAAndB:' + \
            ' successfully update Image A and Image B. First Update Image Type: ' + \
            Psu.PsuFwInfo.imageTypeDict[compImageType1][0] + '.' + \
            ' First Update Image PSU FW Version: ' + \
            psuFwBinPathObjDict[compImageType1][fwImgObjIdx].psuFwVersion + '.' + \
            ' Second Update Image Type: ' + \
            Psu.PsuFwInfo.imageTypeDict[compImageType2][0] + '.' + \
            ' Second Update Image PSU FW Version: ' + \
            psuFwBinPathObjDict[compImageType2][fwImgObjIdx].psuFwVersion)
    else:
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.UpdatePsuFwImgAAndB:' + \
            ' failed to update Image A and Image B.')
        funcPassOrFail = False

    return funcPassOrFail

# Function will update PSU FW 
def UpdatePsuFwAndVersion(interfaceParams, imageType, \
    binFilePathIdx, fwImgObjIdx):

    # Declare module-scope variables
    global psuFwBinPathObjDict

    # Initialize variables
    funcPassOrFail = False

    # Update Available PSU FW
    confFwObj = IpmiUtil.ConfigureFwUpdate(1, 1, imageType, \
        psuFwBinPathObjDict[imageType][binFilePathIdx])
    updatePassOrFail, updateDuration = \
        confFwObj.UpdateFw(interfaceParams, Config.psuFwUpdateTimeLimit, \
        Config.psuFwUpdatePollStatusInterval)
    if updatePassOrFail:
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.UpdatePsuFwAndVersion:' + \
            ' successfully updated PSU FW. Image Type: ' + \
            Psu.PsuFwInfo.imageTypeDict[imageType][0] + '.' + \
            ' Image File Path: ' + psuFwBinPathObjDict[imageType][binFilePathIdx])
    else:
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.UpdatePsuFwAndVersion:' + \
            ' failed to update PSU FW. Image Type: ' + \
            Psu.PsuFwInfo.imageTypeDict[imageType][0] + '.' + \
            ' Image File Path: ' + psuFwBinPathObjDict[imageType][binFilePathIdx])
        return funcPassOrFail

    # Get PSU FW Version
    psuFwInfoObj = Psu.PsuFwInfo()
    updatePassOrFail = \
        psuFwInfoObj.UpdatePsuFwInfo(interfaceParams, imageType)
    if updatePassOrFail:
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.UpdatePsuFwAndVersion:' + \
            ' successfully received PSU FW Info. Image Type: ' + \
            Psu.PsuFwInfo.imageTypeDict[psuFwInfoObj.imageType][0] + \
            ' Image Activate: ' + str(psuFwInfoObj.activeOrInactive) + \
            ' PSU FW Version: ' + str(psuFwInfoObj.psuFwVersion))
    else:
        UtilLogger.verboseLogger.info('PsuFwUpdateTest.UpdatePsuFwAndVersion:' + \
            ' failed to receive PSU FW Info. Image Type: ' + \
            Psu.PsuFwInfo.imageTypeDict[psuFwInfoObj.imageType][0] + \
            ' Image Activate: ' + str(psuFwInfoObj.activeOrInactive) + \
            ' PSU FW Version: ' + str(psuFwInfoObj.psuFwVersion))

    # Update output
    psuFwBinPathObjDict[imageType][fwImgObjIdx] = psuFwInfoObj
    funcPassOrFail = updatePassOrFail

    return funcPassOrFail