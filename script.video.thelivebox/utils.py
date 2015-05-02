
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


ADDONID = 'script.video.thelivebox'
ADDON   = xbmcaddon.Addon(ADDONID)
HOME    = ADDON.getAddonInfo('path')
PROFILE = ADDON.getAddonInfo('profile')
TITLE   = ADDON.getAddonInfo('name')
VERSION = ADDON.getAddonInfo('version')
ICON    = os.path.join(HOME, 'icon.png')
FANART  = os.path.join(HOME, 'fanart.jpg')


VIDEO_ADDON  = 100
VIDEO_LOCAL  = 200
VIDEO_REMOTE = 300
CLEARCACHE   = 400
SETTINGS     = 500
WAITING      = 600
EXAM         = 700
DEMO         = 800
EXTERNAL     = 900

SERVER       = 5100
LBVERSION    = 5200
ADDRESS      = 5300
RETRIEVE_URL = 5400


def getSetting(param):
    return xbmcaddon.Addon(ADDONID).getSetting(param)

def setSetting(param, value):
    if xbmcaddon.Addon(ADDONID).getSetting(param) == value:
        return
    xbmcaddon.Addon(ADDONID).setSetting(param, value)


GETTEXT   = ADDON.getLocalizedString
BOOTVIDEO = getSetting('BOOTVIDEO') == 'true'


DEBUG = True
def Log(text):
    try:
        output = '%s V%s : %s' % (TITLE, VERSION, str(text))
        
        if DEBUG:
            xbmc.log(output)
        else:
            xbmc.log(output, xbmc.LOGDEBUG)
    except:
        pass


def DialogOK(line1, line2='', line3=''):
    d = xbmcgui.Dialog()
    d.ok(TITLE + ' - ' + VERSION, line1, line2 , line3)



def DialogYesNo(line1, line2='', line3='', noLabel=None, yesLabel=None):
    d = xbmcgui.Dialog()
    if noLabel == None or yesLabel == None:
        return d.yesno(TITLE + ' - ' + VERSION, line1, line2 , line3) == True
    else:
        return d.yesno(TITLE + ' - ' + VERSION, line1, line2 , line3, noLabel, yesLabel) == True


def CheckVersion():
    prev = getSetting('VERSION')
    curr = VERSION

    if prev == curr:
        return

    setSetting('VERSION', curr)

    #DialogOK(GETTEXT(30004), GETTEXT(30005), GETTEXT(30006))



def GetAddonMessage(addr, port, msg, params = {}):
    try:
        req = ''

        for key in params.keys():
            req += '&%s=%s' %  (key, params[key])

        req = 'plugin://plugin.video.thelivebox/?mode=%d%s' % (msg, req)

        resp = GetJSON(addr, port, urllib.quote_plus(req))

        result  = resp['result']
        return result['files'][0]['label']
    except Exception, e:
        utils.Log('ERROR in GetAddonMessage %s' % str(e))
        pass


def GetJSON(addr, port, params):
    import json as simplejson 
    import urllib2

    method = 'Files.GetDirectory'
    host   = '%s:%s' % (addr, str(port))

    url  = 'http://%s/jsonrpc?request={"jsonrpc":"2.0","method":"%s","params":{"directory":"%s"},"id":1}' % (host, method, params)
    req  = urllib2.Request(url)
    resp = urllib2.urlopen(req, timeout=5).read()
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

    DialogOK(GETTEXT(30001), GETTEXT(30002), GETTEXT(30003))

    ADDON.openSettings()

    client = getSetting('CLIENT')
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


def GetHost():
    import network

    if getSetting('FALLBACK').lower() == 'true':
        return network.getLocalHost()

    if getSetting('HOST_MODE') == '0':
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


def GetPassword():
    return xbmcaddon.Addon('plugin.video.thelivebox-admin').getSetting('PASSWORD')


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



