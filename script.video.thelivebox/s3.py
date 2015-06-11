#
#       Copyright (C) 2015-
#       Sean Poyser (seanpoyser@gmail.com)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import datetime
import urllib
import re

AWSAccessKeyId     = 'AKIAINUS2YCRTDBD674Q'
AWSSecretAccessKey = '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'

DELIMETER = '/'


def getSignature(resource, expires):
    import base64
    import hmac
    import sha

    HTTPVERB                = 'GET'
    ContentMD5              = ''
    ContentType             = ''
    CanonicalizedAmzHeaders = ''
    CanonicalizedResource   = '/thelivebox/%s' % resource

    string_to_sign = HTTPVERB + '\n' +  ContentMD5 + '\n' +  ContentType + '\n' + expires + '\n' + CanonicalizedAmzHeaders + CanonicalizedResource

    sig = base64.b64encode(hmac.new(AWSSecretAccessKey, string_to_sign, sha).digest())
    sig = urllib.urlencode({'Signature':sig})

    return sig


def getURL(resource=''):
    delta   = datetime.datetime.today() - datetime.datetime(1970,1,1)
    expires = (delta.days * 86400) + (delta.seconds) + (4 * 3600)
    expires = int(expires / 3600) * 3600
    expires = str(expires)

    sig = getSignature(resource, expires)
    url = 'http://thelivebox.s3.amazonaws.com/%s?AWSAccessKeyId=%s&Expires=%s&%s' % (resource, AWSAccessKeyId, expires, sig)

    return url

    
def getFile(folder, file):
    if not folder.endswith(DELIMETER):
        folder += DELIMETER

    return getURL(folder + file)


def getFolder(folder):
    import utils

    folders  = []
    files    = []

    if not folder.endswith(DELIMETER):
        folder += DELIMETER

    url = getURL()

    utils.Log('Amazon S3 URL : %s' % url)

    content = utils.GetHTML(url, maxAge = 3600)
    keys    = re.compile('<Key>(.+?)</Key>').findall(content)

    for key in keys:
        if not key.startswith(folder):
            continue

        if key == folder:
            continue

        name = key.replace(folder, '', 1)
        
        if DELIMETER in name:
            thisFolder = folder + name.split(DELIMETER, 1)[0]
            if thisFolder not in folders:
                folders.append(thisFolder)
        else:
            files.append(key)

    return folders, files