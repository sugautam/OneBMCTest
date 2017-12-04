

# Python modules in current project.
import UtilLogger
import IpmiUtil


# Prototype Setup Function
def Setup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifySelAgainstXmlList_DebugTest.py: running Setup fxn")

    return True


def Execute(interfaceParams):

    UtilLogger.verboseLogger.info("VerifySelAgainstXmlList_DebugTest.py: running Execute fxn")

    try:
        selPassOrFail, unexpectedSels = IpmiUtil.VerifySelAgainstXmlList([], "./../SupportFiles/ValidSelEvents.xml")
    except AssertionError, ex:
        print("Exception Caught: Invalid input argument(s) for function IpmiUtil.VerifySelAgainstXmlList")
        print("Exception Message: {}".format(ex))
        return False
    except BaseException, ex:
        print("Caught an exception while calling function IpmiUtil.VerifySelAgainstXmlList")
        print("Exception Message: {}".format(ex))
        return False

    if (unexpectedSels != None):
        UtilLogger.verboseLogger.info("VerifySelAgainstXmlList_DebugTest.py: Unexpected SEL events are:")
        for event in unexpectedSels:
            UtilLogger.verboseLogger.info(event)
        UtilLogger.verboseLogger.info("\n")
    else:
        UtilLogger.verboseLogger.info("VerifySelAgainstXmlList_DebugTest.py: No Unexpected SEL events found.\n")

    return selPassOrFail


# Prototype Cleanup Function
def Cleanup(interfaceParams):

    UtilLogger.verboseLogger.info("VerifySelAgainstXmlList_DebugTest.py: running Cleanup fxn")

    return True