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

import argparse

import Config

def initParser():

    # Initialize argument parser
    # with switches used in CLI
    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter )
    parser.add_argument('-platform', '-plt',
                        choices=[Config.bmcPlatformC2010Value, Config.bmcPlatformJ2010Value, Config.bmcPlatformG50Value],
                        default=Config.bmcPlatformC2010Value,
                        help='BMC platform that is currently being tested'),
    parser.add_argument('-conn', '-c', 
                        choices=['eth', 'kcs'],
                        help='interface connection ' + \
        '(shorthand: \'-c\') - ' + \
        'options: eth (IPMI over LAN+ or J2010 REST), kcs (in-band compute server)')
    parser.add_argument('-ip', '-i', help='IP address of BMC ' + \
        '(shorthand: \'-i\') - ' + \
        'required for \'-conn eth\'')
    parser.add_argument('-user', '-u', help='User Name for ' + \
        'connecting LAN single session or J2010 REST session (shorthand: \'-u\') - ' + \
        'required for \'-conn eth\'')
    parser.add_argument('-pwd', '-p', help='Password for ' + \
        'connecting LAN single session or J2010 REST session (shorthand: \'-p\') - '\
        'required for \'-conn eth\'')
    parser.add_argument('-test', '-t', help='Tests to run ' + \
        '(shorthand: \'-t\') - ' + \
        'options: a (run all test scripts placed in <platform>TestScripts folder, ' + \
        'b (run test scripts in <platform>TestScripts folder specified in XMLFILEPATH), ' + \
        '<testScriptName> (run single test script with name ' + \
        '<testScriptName> (do not include \'.py\' extension) in <platform>TestScripts folder)')
    parser.add_argument('-xmlfilepath', '-f', help='Path to XML file ' + \
        '(shorthand: \'-f\') - ' + \
        'file contains list of test scripts to run (required with \'-test b\')')
    parser.add_argument('-verbosename', '-vbn', help='Name of verbose log file.' + \
        'File will be renamed as <verbosename>_<timeStamp>.log.' + \
        ' Shorthand: \'-vbn\'')
    parser.add_argument("-xlo", "--excelOutput", help="Optional output Excell file name (excluding " \
                        + ".xlsx extension). The directory path that contains the output file " \
                        + "is configurable and is set in the configuration file (Config.py). " \
                        + "If no file name is provided a default name is used. The default name " \
                        + "is configurable and is set in the configuration file.")
    parser.add_argument("-xli", "--excelInput", help="Optional verbose log input file to use " \
                        + "(including file extension) to generate the Excel output file. " \
                        + "This parameter can include the path (absolute or relative) of the file, " \
                        + "in addition to the file name. If only the file name is provided, then " \
                        + "it is assumed that the file is in the current directory. " \
                        + "If this parameter is provided, then there are no test scripts to " \
                        + "execute. In this case, the OneBMCTest tool simply processes the " \
                        + "verbose log file to generate the ouput Excel file and nothing else.")
    parser.add_argument('-version', '-v', help='BMC Version string that is' + \
        ' being tested')
    parser.add_argument('-debug', '-dbg', help='Switch for complete IpmiUtil' + \
        ' output in ' + \
        Config.verboseLogPath + Config.verboseLogFileName + \
        Config.verboseLogFileExtension, action="store_true", default=False)
    parser.add_argument('-showverbose', '-svb', help='Switch to print verbose logging' + \
        ' on console ', action="store_true", default=False)
    parser.add_argument('-timestamp', '-ts', help='Switch to print timestamp for every' + \
        ' verbose log entry', action="store_true", default=False)
    parser.add_argument('-email', '-e', help='Email string to send results to')
    parser.add_argument('-sender', '-sn', help='Email string for sender')
    parser.add_argument('-senderpwd', '-sp', help='Password string for sender')
    parser.add_argument('-server', '-sv', help='SMTP server to use' + \
        ' to send email')
    parser.add_argument('-port', '-po', help='SMTP server port to use' + \
        ' for sending email')
    parser.add_argument('-switch', '-switch', help='IP Power Switch IP address. Requires for connecting to the switch ')
    
    # Parse arguments and return
    return parser
