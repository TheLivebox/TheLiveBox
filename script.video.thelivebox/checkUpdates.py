'''
    Copyright (C) 2015 Sean Poyser (seanpoyser@gmail.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import xbmc
import xbmcaddon

import os
import re

from sqlite3 import dbapi2 as sqlite3

import utils
import sfile

REPO = 'repository.thelivebox'


#return types
DISABLED  = 0
UPDATED   = 1
FAILED    = 2
CANCELLED = 3
CURRENT   = 4



def _checkRepo():
    dbPath = xbmc.translatePath('special://home/userdata/Database')
    dbPath = os.path.join(dbPath, 'Addons15.db')

    latestChk = getCurrentChecksum()
    if not latestChk:
        return FAILED

    db   = xbmc.translatePath(dbPath)
    conn = sqlite3.connect(db, timeout = 10, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread = False)
    conn.row_factory = sqlite3.Row
    c = conn.cursor() 

    c.execute("SELECT checksum FROM repo WHERE addonID = ?", (REPO,))

    updated = False
    for row in c:
        updated = checksum(row['checksum'], latestChk)

    c.close()

    return updated


def checksum(chksum, latestChk):
    utils.Log('Current local checksum  : %s' % chksum)
    utils.Log('Current remote checksum : %s' % latestChk)
    if chksum == latestChk:
        return CURRENT

    dp  = utils.DialogProgress(utils.GETTEXT(30071), utils.GETTEXT(30068))
    ret = doUpdate(dp)

    dp.close()

    return ret


def doUpdate(dp):
    addons = []

    addons.append('script.video.thelivebox')
    addons.append('plugin.video.thelivebox')
    addons.append('plugin.video.thelivebox-admin')
    addons.append(REPO)

    versions = []

    url = getURL()
    xml = utils.GetHTML(url, maxAge=0)

    for addon in addons:
        newer = getNewerVersion(addon, xml)
        versions.append([addon, newer])

    xbmc.executebuiltin('UpdateAddonRepos')

    tries = 600
    count = 0

    while count < tries:
        count += 1
        percent = int(100 * count / tries)
        dp.update(percent)

        if dp.iscanceled():
            return CANCELLED

        if checkComplete(versions):
            utils.CompleteProgress(dp, percent)
            return UPDATED

        xbmc.sleep(1000)

    return FAILED


def getURL():
    path  = xbmcaddon.Addon(REPO).getAddonInfo('path')
    path  = os.path.join(path, 'addon.xml')

    xml = sfile.read(path)
    url = re.compile('<info.+?>(.+?)</info>').search(xml).group(1)

    return url


def checkComplete(versions):
    for version in versions:
        current = getCurrentVersion(version[0])
        utils.Log('In check complete')
        utils.Log('Current version of %s  : %s' % (version[0], current))
        utils.Log('Newer version of %s    : %s' % (version[0], version[1]))
        if current <> version[1]:
            return False

    return True

def getCurrentVersion(addonID):
    return xbmcaddon.Addon(addonID).getAddonInfo('version')


def getNewerVersion(addonID, xml):
    match   = '<addon id="%s".+?version="(.+?)"' % addonID
    version = re.compile(match).search(xml).group(1)

    utils.Log('Newer version of %s  : %s' % (addonID, version))

    return version


def getCurrentChecksum():
    try:
        path = os.path.join('special://home', 'addons', REPO, 'addon.xml')
        xml  = sfile.read(path)
        url  = re.compile('<checksum>(.+?)</checksum>').search(xml).group(1)

        import urllib2
        req = urllib2.Request(url)

        response = urllib2.urlopen(req)
        chk     = response.read()

        response.close()
        return chk

    except Exception, e:
        utils.Log('Error in getCurrentChecksum : %s' % str(e))
        pass

    return None


def checkRepo():
    #this method does not report if current
    ret = _checkRepo()

    utils.Log('checkRepo returned %d' % ret)

    if ret == DISABLED:
        utils.DialogOK(utils.GETTEXT(30074))

    elif ret == UPDATED:
        utils.DialogOK(utils.GETTEXT(30069))

    elif ret == CANCELLED:
        utils.DialogOK(utils.GETTEXT(30072))

    elif ret == FAILED:
        utils.DialogOK(utils.GETTEXT(30073))


if __name__ == '__main__': 
    ret = _checkRepo()

    utils.Log('checkRepo returned %d' % ret)

    if ret == DISABLED:
        utils.DialogOK(utils.GETTEXT(30074))

    elif ret == UPDATED:
        utils.DialogOK(utils.GETTEXT(30069))

    elif ret == CURRENT:
        utils.DialogOK(utils.GETTEXT(30070))

    elif ret == CANCELLED:
        utils.DialogOK(utils.GETTEXT(30072))

    elif ret == FAILED:
        utils.DialogOK(utils.GETTEXT(30073))
