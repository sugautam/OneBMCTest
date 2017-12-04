

# Python modules in current project.
import UtilLogger
import IpmiUtil


# Prototype Setup Function
def Setup(interfaceParams):

    return True


def Execute(interfaceParams):

    result = None
    try:
        result = IpmiUtil.VerifyThresholdSensors([], "./C2010TestScripts/XmlFiles/sensorlistxmlfile.xml")
    except AssertionError, ex:
        print("Exception Caught: Invalid input argument(s) for function IpmiUtil.VerifyThresholdSensors")
        print("Exception Message: {}".format(ex))
        return False
    except BaseException, ex:
        print("Caught an exception while calling function IpmiUtil.VerifyThresholdSensors")
        print("Exception Message: {}".format(ex))
        return False

    return result


# Prototype Cleanup Function
def Cleanup(interfaceParams):

    return True