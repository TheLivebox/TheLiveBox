'''
    Copyright (C) 2015- Sean Poyser (seanpoyser@gmail.com)

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

import os
import re

import utils
import sfile
import s3


#return types
DISABLED  = 0
UPDATED   = 1
FAILED    = 2
CANCELLED = 3
CURRENT   = 4
DECLINED  = 5



PROFILE = utils.PROFILE
ROOT    = '_software'
FILE    = 'latest_version.txt'


def _checkRepo():
    #return DISABLED

    updated = CANCELLED

    latestVersion = getLatestVersion()
    if not latestVersion:
        return FAILED

    if latestVersion == '0':
        return CURRENT

    try:    currentVersion = getCurrentVersion()
    except: return FAILED

    updated = checkLatest(currentVersion, latestVersion)
    
    return updated


def getLatestVersion():
    try:
        url = s3.getFile(ROOT, FILE)

        import urllib2
        req = urllib2.Request(url)

        response = urllib2.urlopen(req)
        latest   = response.read()

        return latest

    except Exception, e:
        pass

    return None


def getCurrentVersion():
    return utils.ADDON.getAddonInfo('version')


def checkLatest(current, latest):
    if current == latest:
        return CURRENT

    if not utils.DialogYesNo(utils.GETTEXT(30115), utils.GETTEXT(30116)):
        return DECLINED

    filename = 'addon-%s.zip' % latest

    url   = s3.getFile(ROOT, filename)
    dest  = os.path.join(PROFILE, filename)
    title = utils.GETTEXT(30117)
    dp    = utils.DialogProgress(utils.GETTEXT(30079) % title, utils.GETTEXT(30080))

    import download
    download.doDownload(url, dest, title=title, referrer='', dp=dp, silent=False)

    if not sfile.exists(dest):
        return FAILED

    extracted = extract(dest, dp)

    try:    sfile.delete(dest)
    except: pass

    if not extracted:
        return FAILED

    import xbmcgui
    xbmcgui.Window(10000).setProperty('LB_RELAUNCH', 'true')

    cmd = 'UpdateLocalAddons'
    xbmc.executebuiltin(cmd)

    return UPDATED


def extract(src, dp):
    success = False
    try:
        src = xbmc.translatePath(src)
        import zipfile

        update = os.path.join(PROFILE, 'update')
        update = xbmc.translatePath(update)
        sfile.makedirs(update)

        zin   = zipfile.ZipFile(src, 'r')
        nItem = float(len(zin.infolist()))

        index = 0
        for item in zin.infolist():
            index += 1

            percent  = int(index / nItem *100)
            #filename = item.filename

            zin.extract(item, update)
  
            if dp:
                dp.update(percent, utils.GETTEXT(30118), utils.GETTEXT(30080))

        addons = os.path.join('special://home', 'addons')
        current, folders, files = sfile.walk(update)

        for folder in folders:
            ori = os.path.join(addons, folder)
            src = os.path.join(current, folder)
            dst = os.path.join(addons, folder + '.temp')
            sfile.copytree(src, dst)
            sfile.rmtree(ori)
            while not sfile.exists(dst):
                xbmc.sleep(100)
            while sfile.exists(ori):
                xbmc.sleep(100)
            sfile.rename(dst, ori)   

        success = True
    except:
        success = False

    sfile.delete(update)
    return success


def checkRepo(reportCurrent=False):
    ret  = _checkRepo()
    type = 'unknown'

    if ret == DISABLED:
        type = 'disabled'
        utils.DialogOK(utils.GETTEXT(30074))

    elif ret == UPDATED:
        type = 'updated'
        utils.DialogOK(utils.GETTEXT(30069))

    elif ret == CANCELLED:
        type = 'cancelled'
        utils.DialogOK(utils.GETTEXT(30072))

    elif ret == FAILED:
        type = 'failed'
        utils.DialogOK(utils.GETTEXT(30073))

    elif ret == CURRENT:
        type = 'current'
        if reportCurrent:
            utils.DialogOK(utils.GETTEXT(30070))

    elif ret == DECLINED:
        type = 'update declined'

    utils.Log('checkRepo returned %s' % type)

    return ret



def main():
    checkRepo(reportCurrent=True)


if __name__ == '__main__': 
    main()