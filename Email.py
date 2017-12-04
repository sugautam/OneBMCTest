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

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import UtilLogger

def send_mail(send_from, send_password, send_to, subject, text, files=None,
              server="127.0.0.1", port=None):

    sendPassOrFail = True

    try:
        assert isinstance(send_to, list)

        msg = MIMEMultipart(
            From=send_from,
            To=COMMASPACE.join(send_to),
            Date=formatdate(localtime=True),
            Subject=subject
        )
        msg.attach(MIMEText(text))

        for f in files or []:
            with open(f, "rb") as fil:
                msg.attach(MIMEApplication(
                    fil.read(),
                    Content_Disposition='attachment; filename="%s"' % basename(f),
                    Name=basename(f)
                ))

        # Add Subject, To, and From line to message
        msg['Subject'] = subject
        msg['To'] = ', '.join(send_to)
        msg['From'] = send_from

        smtp = smtplib.SMTP(server, port)

        # identify to smtp client
        smtp.ehlo()
        # secure email with tls encryption
        smtp.starttls()
        # re-identify as an encrypted connection
        smtp.ehlo()
        smtp.login(send_from, send_password)

        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()
    except Exception, e:
        UtilLogger.verboseLogger.error(\
            "send_mail: failed to send mail with exception: " + repr(e))
        sendPassOrFail = False

    return sendPassOrFail
