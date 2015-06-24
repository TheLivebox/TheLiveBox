
#       Copyright (C) 2013-
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

import xbmcaddon
import xbmcgui
import xbmc

import urllib
import os

import json as simplejson 

import sfile
import s3


ADDONID = 'script.video.thelivebox'
ADDON   = xbmcaddon.Addon(ADDONID)
HOME    = ADDON.getAddonInfo('path')
PROFILE = ADDON.getAddonInfo('profile')
TITLE   = ADDON.getAddonInfo('name')
VERSION = ADDON.getAddonInfo('version')
ICON    = os.path.join(HOME, 'icon.png')
FANART  = os.path.join(HOME, 'fanart.jpg')


VIDEO_ADDON           = 100
VIDEO_REMOTE          = 200
SERVER_FILE           = 300
LOCAL_FILE            = 400
SETTINGS              = 500
CLEARCACHE            = 600
WAITING               = 700
EXAM                  = 800
DEMO                  = 900
SERVER_FOLDER         = 1000
LOCAL_FOLDER          = 1100
AMAZON_FILE           = 1200
AMAZON_FOLDER         = 1300
LOCAL_PLAYABLE_FOLDER = 1400

SERVER          = 5100
LBVERSION       = 5200
ADDRESS         = 5300
RETRIEVE_URL    = 5400


DELIMETER = s3.DELIMETER


PLAYABLE = xbmc.getSupportedMedia('video') + '|' + xbmc.getSupportedMedia('music')
PLAYABLE = PLAYABLE.replace('|.zip', '')
PLAYABLE = PLAYABLE.split('|')


def GetXBMCVersion():
    #xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')

    version = xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')
    version = version.split('.')
    return int(version[0]), int(version[1]) #major, minor eg, 13.9.902


MAJOR, MINOR = GetXBMCVersion()
FRODO        = (MAJOR == 12) and (MINOR < 9)
GOTHAM       = (MAJOR == 13) or (MAJOR == 12 and MINOR == 9)
HELIX        = (MAJOR == 14) or (MAJOR == 13 and MINOR == 9)


def getSetting(param):
    return xbmcaddon.Addon(ADDONID).getSetting(param)


def getAdminSetting(param):
    return xbmcaddon.Addon('plugin.video.thelivebox-admin').getSetting(param)


def setSetting(param, value):
    if xbmcaddon.Addon(ADDONID).getSetting(param) == value:
        return
    xbmcaddon.Addon(ADDONID).setSetting(param, value)


GETTEXT   = ADDON.getLocalizedString
BOOTVIDEO = getSetting('BOOTVIDEO') == 'true'


DEBUG = False
def Log(text):
    try:
        output = '%s V%s : %s' % (TITLE, VERSION, str(text))
        
        if DEBUG:
            xbmc.log(output)
        else:
            xbmc.log(output, xbmc.LOGDEBUG)
    except:
        pass


def Notify(message, length=10000):
    cmd = 'XBMC.notification(%s,%s,%d,%s)' % (TITLE, message, length, ICON)
    xbmc.executebuiltin(cmd)



def DialogOK(line1, line2='', line3=''):
    d = xbmcgui.Dialog()
    d.ok(TITLE + ' - ' + VERSION, line1, line2 , line3)



def DialogYesNo(line1, line2='', line3='', noLabel=None, yesLabel=None):
    d = xbmcgui.Dialog()
    if noLabel == None or yesLabel == None:
        return d.yesno(TITLE + ' - ' + VERSION, line1, line2 , line3) == True
    else:
        return d.yesno(TITLE + ' - ' + VERSION, line1, line2 , line3, noLabel, yesLabel) == True


def checkVersion():
    prev = getSetting('VERSION')
    curr = VERSION

    if prev == curr:
        return

    setSetting('VERSION', curr)

    if curr == '1.0.0.4':
        setSetting('SKIN', 'Thumbnails')

    #DialogOK(GETTEXT(30004), GETTEXT(30005), GETTEXT(30006))
    

def GetAddonMessage(addr, port, msg, params = {}, timeout=60):
    try:
        req = ''

        for key in params.keys():
            req += '&%s=%s' %  (key, params[key])

        req = 'plugin://plugin.video.thelivebox/?mode=%d%s' % (msg, req)

        resp = GetJSON(addr, port, urllib.quote_plus(req), timeout=timeout)

        result  = resp['result']
        return result['files'][0]['label']
    except Exception, e:
        utils.Log('ERROR in GetAddonMessage %s' % str(e))
        pass


def ClearCache():
    import cache
    cache.clearCache()


def GetJSON(addr, port, params, timeout=60):
    import json as simplejson 
    import urllib2

    method = 'Files.GetDirectory'
    host   = '%s:%s' % (addr, str(port))

    url  = 'http://%s/jsonrpc?request={"jsonrpc":"2.0","method":"%s","params":{"directory":"%s"},"id":1}' % (host, method, params)

    req  = urllib2.Request(url)
    resp = urllib2.urlopen(req, timeout=timeout).read()

    resp = simplejson.loads(resp) 
    return resp


def SetFanart():
    path = os.path.join(HOME, 'fanart.jpg')
    Execute('Skin.SetBool(UseCustomBackground)')
    Execute('Skin.SetString(%s, %s)' % ('CustomBackgroundPath', path))


def GetClient():
    client = getSetting('CLIENT')
    if len(client) > 0:
        return client

    #DialogOK(GETTEXT(30001), GETTEXT(30002), GETTEXT(30003))

    #ADDON.openSettings()

    #client = getSetting('CLIENT')
    return client


def GetVimeoVersion():
    try:
        vimeo = xbmcaddon.Addon('plugin.video.vimeo')
        return vimeo.getAddonInfo('version')
    except:
        pass

    return '0'


def GetHTML(url, maxAge = 86400):
    import cache
    html = cache.getURL(url, maxSec=5*86400, agent='Firefox')
    html = html.replace('\n', '')
    html = html.replace('\r', '')
    html = html.replace('\t', '')
    return html


def Execute(cmd):
    Log(cmd)
    xbmc.executebuiltin(cmd) 


def Launch(param=None):
    name      = 'launch'
    addonPath = HOME
    addonID   = addonPath.rsplit(os.sep, 1)[-1]
    script    = os.path.join(addonPath, 'launch.py')
    args      = ADDONID
    if param:
        args += ',' + param
    cmd       = 'AlarmClock(%s,RunScript(%s,%s),%d,True)' % (name, script, args, 0)

    xbmc.executebuiltin('CancelAlarm(%s,True)' % name)  
    xbmc.executebuiltin(cmd) 


def IsServer():
    #currently ignore server mode and always return True
    return True
    return getSetting('HOST_MODE') == '0'


def GetHost():
    import network

    if getSetting('FALLBACK').lower() == 'true':
        return network.getLocalHost()

    if IsServer():
        return network.getLocalHost()

    if getSetting('SERVER_MODE') == '0':
        server = network.getAutoServer()
        if not server:
            return None, None
        return server[1], server[2]

    return getSetting('SERVER_IP'), int(getSetting('SERVER_PORT'))


def GetText(title, text='', hidden=False, allowEmpty=False):
    kb = xbmc.Keyboard(text.strip(), title)
    kb.setHiddenInput(hidden)
    kb.doModal()
    if not kb.isConfirmed():
        return None

    text = kb.getText().strip()

    if (len(text) < 1) and (not allowEmpty):
        return None

    return text


def VerifyPassword():
    if xbmcaddon.Addon('plugin.video.thelivebox-admin').getSetting('REQ_PASS').lower() != 'true':
        return True

    pwd = GetText(GETTEXT(30051), hidden=True, allowEmpty=True)

    if pwd == None:
        return False

    return pwd == GetPassword()


def GetPassword():
    return getAdminSetting('PASSWORD')


def enableWebserver():
    setKodiSetting('services.webserverpassword', '') 
    setKodiSetting('services.webserverusername', '') 
    setKodiSetting('services.webserverport',     8080) 
    setKodiSetting('services.webskin',           'webinterface.default') 
    setKodiSetting('services.zeroconf',          True) 
    setKodiSetting('services.webserver',         True) 

    Log('----- Webserver Settings -----')
    Log(getKodiSetting('services.webserverpassword'))
    Log(getKodiSetting('services.webserverusername'))
    Log(getKodiSetting('services.webserverport'))
    Log(getKodiSetting('services.webskin'))
    Log(getKodiSetting('services.zeroconf'))
    Log(getKodiSetting('services.webserver'))


def setKodiSetting(setting, value):
    setting = '"%s"' % setting

    if isinstance(value, list):
        text = ''
        for item in value:
            text += '"%s",' % str(item)

        text  = text[:-1]
        text  = '[%s]' % text
        value = text

    elif isinstance(value, bool):
        value = 'true' if value else 'false'

    elif not isinstance(value, int):
        value = '"%s"' % value

    query = '{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":%s,"value":%s}, "id":1}' % (setting, value)
    Log(query)
    response = xbmc.executeJSONRPC(query)
    Log(response)


def getKodiSetting(setting):
    try:
        setting = '"%s"' % setting
 
        query = '{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":%s}, "id":1}' % (setting)
        Log(query)
        response = xbmc.executeJSONRPC(query)
        Log(response)

        response = simplejson.loads(response)                

        if response.has_key('result'):
            if response['result'].has_key('value'):
                return response ['result']['value'] 
    except:
        pass

    return None


def isAmazonPlayable(folder):
    folders, files = s3.getFolder(folder)

    for file in files:
        if isFilePlayable(file):
            return True

    for fold in folders:
        if isAmazonPlayable(fold):
            return True

    return False


def isFilePlayable(path):
    try:
        ext = '.' + path.rsplit('.')[-1]
        return ext in PLAYABLE
    except:
        pass

    return False


def isPlayable(path):
    if not sfile.exists(path):
        return False

    if sfile.isfile(path):
        playable = isFilePlayable(path)
        return playable
         
    current, dirs, files = sfile.walk(path)

    for file in files:
        if isPlayable(os.path.join(current, file)):
            return True

    for dir in dirs:        
        if isPlayable(os.path.join(current, dir)):
            return True

    return False


def getExternalDrive():
    return getSetting('EXT_DRIVE')


def parseFolder(folder, root=None, recurse=True):
    items = []

    if not folder:
        folder = getExternalDrive()
        if isPlayable(folder):
            items.append([root, folder, False, True])
        return items

    current, dirs, files = sfile.walk(folder)

    for dir in dirs:        
        path = os.path.join(current, dir)
        if dir.endswith('_PLAYALL'):
            items.append([dir.rsplit('_PLAYALL', 1)[0], path, True, True])
        elif isPlayable(path):
            items.append([dir, path, False, True])

    for file in files:
        path = os.path.join(current, file)
        if isPlayable(path):
            items.append([file.rsplit('.', 1)[0], path, True, False])

    return items


def removePartFiles():
    folder = os.path.join(PROFILE, 'local')

    current, dirs, files = sfile.walk(folder)

    for file in files:
        if file.endswith('.part'):
            file = os.path.join(current, file)
            sfile.remove(file)
            sfile.remove(file.rsplit('.part', 1)[0])


def verifySource():
    input  = '<source><name>Livebox Cache</name><path pathversion="1">special://userdata/addon_data/script.video.thelivebox/</path></source></video>'
    source = os.path.join('special://userdata', 'sources.xml')
    if sfile.exists(source):
        contents = sfile.read(source)
        if 'Livebox Cache' in contents:
            Log('Source already exists')
            return True
        Log('Updating sources')
        contents = contents.replace('</video>', input)
    else:
        Log('Creating sources.xml file')
        contents = '<sources><video><default pathversion="1"></default>%s</sources>' % input

    source = sfile.file(source, 'w')
    source.write(contents)
    source.close()

    return False


def systemUpdated(line1=None, line2='', line3=''):
    if line1:
        DialogOK(line1, line2, line3)
    xbmc.executebuiltin('RestartApp')
 