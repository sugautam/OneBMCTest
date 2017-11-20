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

import UtilLogger
import os
import xml.etree.cElementTree as ElementTree

# Class will parse the Xml Tree
# and hold the elements, sub-elements,
# and attributes in the 'root' object
class XmlParser(object):

    root = None

    def __init__(self, xmlFilePath):
        # Check that the file exists
        if not os.path.isfile(xmlFilePath):
            UtilLogger.verboseLogger.info("XmlParser: file path " + xmlFilePath + " is invalid. Will not parse.")
        else:            
            tree = ElementTree.parse(xmlFilePath, parser=ElementTree.XMLParser(encoding='utf-8'))
            self.root = tree.getroot()