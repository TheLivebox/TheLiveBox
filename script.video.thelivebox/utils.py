
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
ICON    = os.path.join(HOME, 'logo1.png')
FANART  = os.path.join(HOME, 'fanart.jpg')
SKIN    = 'livebox'

DEFAULTMOVIE  = os.path.join(HOME, 'resources', 'images', 'defaultMovie.png')
DEFAULTFOLDER = os.path.join(HOME, 'resources', 'images', 'defaultFolder.png')

HOME = HOME.replace('storage/emulated/0', 'sdcard') #for Android


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
LOCAL_FOLDER_ROOT     = 1100     
LOCAL_FOLDER          = 1150
RECENT_LOCAL_FOLDER   = 1175
AMAZON_FILE           = 1200
AMAZON_FOLDER         = 1300
LOCAL_PLAYABLE_FOLDER = 1400
UPDATE_FILE_CHK       = 1500
UPDATE_FILE           = 1600
DELETE_LOCAL_FILE     = 1700
DELETE_LOCAL_FOLDER   = 1800
REPLAY                = 1900

SERVER          = 5100
LBVERSION       = 5200
ADDRESS         = 5300
RETRIEVE_URL    = 5400


DELIMETER = s3.DELIMETER


IMG_EXT = ['.jpg', '.png']

SRC = 'src'
DSC = 'dsc'


#PLAYABLE = xbmc.getSupportedMedia('video') + '|' + xbmc.getSupportedMedia('music')
#PLAYABLE = PLAYABLE.replace('|.zip', '')
PLAYABLE = 'mp3|mp4|m4v|avi|flv|mpg|mov|txt|%s' % SRC
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
ISENGARD     = (MAJOR == 15) or (MAJOR == 14 and MINOR == 9)
JARVIS       = (MAJOR == 16) or (MAJOR == 15 and MINOR == 9)
KRYPTON      = (MAJOR == 17) or (MAJOR == 16 and MINOR == 9)


def getSetting(param):
    if param.lower() == 'skin':
        return 'Thumbnails'

    return xbmcaddon.Addon(ADDONID).getSetting(param)


def getAdminSetting(param):
    return xbmcaddon.Addon('plugin.video.thelivebox-admin').getSetting(param)


def setSetting(param, value):
    if xbmcaddon.Addon(ADDONID).getSetting(param) == value:
        return
    xbmcaddon.Addon(ADDONID).setSetting(param, value)



GETTEXT        = ADDON.getLocalizedString
SHOW_CONFIGURE = False #getSetting('SHOW_CONFIGURE') == 'true'
SHOW_REFRESH   = False #getSetting('SHOW_REFRESH')   == 'true'
SHOW_DOWNLOAD  = True  #getSetting('SHOW_DOWNLOAD')  == 'true'
SHOW_REPLAY    = False #getSetting('SHOW_REPLAY')    == 'true'
SHOW_VIMEO     = False #getSetting('SHOW_VIMEO')     == 'true'
SHOW_AMAZON    = True  #getSetting('SHOW_AMAZON')    == 'true'
SHOW_LOCAL     = True  #getSetting('SHOW_LOCAL')     == 'true'
SHOW_HIDDEN    = True  #getSetting('SHOW_HIDDEN')    == 'true'
BOOTVIDEO      = getSetting('BOOTVIDEO')             == 'true'


DEBUG = True
def Log(text, force=False):
    log(text, force)

def log(text, force=False):
    try:
        output = '%s V%s : %s' % (TITLE, VERSION, str(text))
        
        if DEBUG or force:
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
    d.ok(TITLE, line1, line2 , line3)



def DialogYesNo(line1, line2='', line3='', noLabel=None, yesLabel=None):
    d = xbmcgui.Dialog()
    if noLabel == None or yesLabel == None:
        return d.yesno(TITLE, line1, line2 , line3) == True
    else:
        return d.yesno(TITLE, line1, line2 , line3, noLabel, yesLabel) == True


def HideCancelButton():
    xbmc.sleep(250)
    WINDOW_PROGRESS = xbmcgui.Window(10101)

    CANCEL_BUTTON   = WINDOW_PROGRESS.getControl(10)
    CANCEL_BUTTON.setVisible(False)


def CompleteProgress(dp, percent):
    for i in range(percent, 100):
        dp.update(i)
        xbmc.sleep(10)
    dp.close()


def DialogProgress(line1, line2='', line3='', hide=False):
    dp = xbmcgui.DialogProgress()
    dp.create(TITLE, line1, line2, line3)
    dp.update(0)
    if hide:
        HideCancelButton()
    return dp


def checkVersion():
    prev = getSetting('VERSION')
    curr = VERSION

    #if prev == curr:
    #    return

    setSetting('VERSION', curr)

    if curr == '1.0.0.4':
        setSetting('SKIN', 'Thumbnails')

    if curr == '1.0.0.22':
        if getSetting('PLAYBACK_LIMIT_MODE') == '0': #continuous
            setSetting('PLAYBACK_LIMIT_MODE', '1')   #timelimit
            setSetting('PLAYBACK_LIMIT',      '3')   #24 hours

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
        Log('ERROR in GetAddonMessage %s' % str(e))
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
    resolution = getResolution()
    if resolution != '1280x800':
        resolution = '1920x1080'

    resolution = '1280x800'

    src = os.path.join(HOME, 'resources', 'images', 'fanart-%s.jpg' % resolution)
    dst = os.path.join(HOME, 'fanart.jpg')

    sfile.copy(src, dst)

    Execute('Skin.SetBool(UseCustomBackground)')
    Execute('Skin.SetString(%s, %s)' % ('CustomBackgroundPath', src))

    dst = os.path.join(HOME, 'resources', 'skins', 'Thumbnails', 'resources', 'skins', 'Default', 'media', 'lb_background.jpg')
    sfile.copy(src, dst)


def SetShortcut():
    param = 'HomeVideosButton1'
    value = 'script.video.thelivebox'
    Execute('Skin.SetString(%s, %s)' % (param, value))


def HasClient():
    return len(GetClient()) > 0


def GetClient():
    client = getSetting('CLIENT')

    #if len(client) > 0:
    #    return client

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
    return html


def Execute(cmd):
    Log(cmd)
    xbmc.executebuiltin(cmd) 


def verifySkin():
    version = '1.0.3'
    skin    = 'skin.%s' % SKIN

    if installSkin(skin, version):
        changeSkin(skin)

    hideMenus()


def hideMenus():
    params = []
    params.append('HomepageHideRecentlyAddedAlbums')
    params.append('HomepageHideRecentlyAddedVideo')
    params.append('homepageMusicinfo')
    params.append('homepageVideoinfo')
    params.append('HomeMenuNoWeatherButton')
    params.append('HomeMenuNoPicturesButton')
    params.append('HomeMenuNoMusicButton')
    params.append('HomeMenuNoMovieButton')
    params.append('HomeMenuNoTVShowButton')
    params.append('HomeMenuNoProgramsButton')
    params.append('HomeMenuNoVideosButton')

    for param in params:
        xbmc.executebuiltin('Skin.SetBool(%s)' % param)

    #xbmc.executebuiltin('Skin.Reset(HomeMenuNoVideosButton)')

    setKodiSetting('lookandfeel.enablerssfeeds', False)


import re
def compareVersions(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))
    


def validateSkin(skin, reqVersion):
    installed = xbmc.getCondVisibility('System.HasAddon(%s)' % skin) == 1

    if not installed:
        return False

    dst = os.path.join('special://home', 'addons', skin)
    if not sfile.exists(dst):
        return False

    try:    curVersion = xbmcaddon.Addon(skin).getAddonInfo('version')
    except: curVersion = None

    if not curVersion:
        curVersion = '0'

    return compareVersions(curVersion, reqVersion) >= 0


def showBusy():
    # needs to be returned otherwise
    # goes out of scope and closes
    busy = xbmcgui.WindowXMLDialog('DialogBusy.xml', '')
    busy.show()
    busy.getControl(10).setVisible(False)
    return busy


def installSkin(skin, version):
    if HELIX:
        sourceSkin = skin + '-Helix'
    elif JARVIS:
        sourceSkin = skin + '-Jarvis'
    else:
        return

    src = os.path.join(HOME, 'resources', sourceSkin)
    dst = os.path.join('special://home', 'addons', skin)

    if validateSkin(skin, version):
        return True

    busy = showBusy()

    sfile.copytree(src, dst)

    count = 15 * 10 #15 seconds
    xbmc.executebuiltin('UpdateLocalAddons')

    xbmc.sleep(1000)
    installed = xbmc.getCondVisibility('System.HasAddon(%s)' % skin) == 1 and compareVersions(xbmcaddon.Addon(skin).getAddonInfo('version'), version) >= 0

    while not installed and count > 0:
        count -= 1
        xbmc.sleep(100)
        installed = xbmc.getCondVisibility('System.HasAddon(%s)' % skin) == 1 and compareVersions(xbmcaddon.Addon(skin).getAddonInfo('version'), version) >= 0

    busy.close()

    return installed


def changeSkin(skin):
    xbmc.sleep(1000)
    if getKodiSetting('lookandfeel.skin') == skin:
        xbmc.executebuiltin('ReloadSkin()')
        return
        
    setKodiSetting('lookandfeel.skin', skin)

    while xbmc.getCondVisibility('Window.IsActive(yesnodialog)') == 0:
        xbmc.sleep(10)

    cmd = 'Control.Message(11,click)'
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
    return True
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


def disableKodiVersionCheck():
    param = 'versioncheck_enable'
    addID = 'service.xbmc.versioncheck'

    if xbmc.getCondVisibility('System.HasAddon(%s)' % addID) != 1:
        return

    query = '{"jsonrpc":"2.0", "method":"Addons.SetAddonEnabled","params":{ "addonid": "%s", "enabled":false }, "id":1}' % addID
    Log(query)
    response = xbmc.executeJSONRPC(query)
    Log(response)

    addon = xbmcaddon.Addon(addID)

    if addon.getSetting(param) == 'true':
        addon.setSetting(param, 'false')


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
        if isFilePlayable(file[0]):
            return True

    for fold in folders:
        if isAmazonPlayable(fold):
            return True

    return False


def getPlaylistFromLocalSrc(src):
    videos   = []
    playlist = sfile.readlines(src)
    root     = getExternalDrive()

    for video in playlist:
        video = video.strip()
        if len(video) == 0:
            continue

        video = os.path.join(root, video)
        videos.append(video)

    return videos


def getFilename(path):
    try:    
        path = path.rsplit(os.sep, 1)[-1]
        path = path.rsplit(DELIMETER, 1)[-1]
        return path
    except:
        return ''


def removeExtension(path):
    try:    return path.rsplit('.', 1)[0]
    except: path


def getExtension(path):
    try:    return path.rsplit('.')[-1]
    except: return ''


def isFilePlayable(path, maxAge=-1):
    try:
        age = sfile.age(path)
        if maxAge > 0 and age > maxAge:
            return False    
        return (getExtension(path) in PLAYABLE)
    except:
        return False


def isPlayable(path, ignore, maxAge=-1):
    if not sfile.exists(path):
        return False

    if sfile.isfile(path):
        playable = isFilePlayable(path, maxAge)
        return playable

    try:
        if sfile.getfilename(path)[0] in ignore:
            return False
    except:
        pass
         
    current, dirs, files = sfile.walk(path)

    for file in files:
        if isPlayable(os.path.join(current, file), ignore, maxAge):
            return True

    for dir in dirs:
        try: 
            if isPlayable(os.path.join(current, dir), ignore, maxAge):
                return True
        except:
            pass

    return False


def getExternalDrive():
    return getSetting('EXT_DRIVE')


def checkForExternalDrive():
    extDrive = getExternalDrive()
    if sfile.exists(extDrive):
        return True

    DialogOK(GETTEXT(30087), GETTEXT(30088))
    return False


def getDownloadLocation():
    if getSetting('DOWNLOAD_LOC') == '1':
        loc = os.path.join(PROFILE, 'local')
        try:    sfile.makedirs(loc)
        except: pass
        return loc

    return getExternalDrive()


def getAllPlayableFiles(folder):
    files = {}
 
    _getAllPlayableFiles(folder, files)

    return files


def _getAllPlayableFiles(folder, theFiles):
    current, dirs, files = sfile.walk(folder)

    for dir in dirs:        
        path = os.path.join(current, dir)
        _getAllPlayableFiles(path, theFiles)

    for file in files:
        path = os.path.join(current, file)
        if isPlayable(path, ignore=[]):
            size = sfile.size(path)
            theFiles[path] = [path, size]


def parseFolder(folder, root=None, subfolders=True, ignore=[], maxAge=-1):
    #try multiple times because sometimes
    #we get back an empty list

    items   = []
    retries = 50
    while len(items) == 0 and retries > 0:
        items = _parseFolder(folder, root, subfolders, ignore, maxAge)
        retries -= 1
        xbmc.sleep(100)

    return items


def _parseFolder(folder, root, subfolders, ignore, maxAge=-1):
    items = []

    if not folder:
        folder = getExternalDrive()
        if isPlayable(folder, ignore, maxAge):
            items.append([root, folder, False, True])
        return items

    current, dirs, files = sfile.walk(folder)

    if subfolders:
        for dir in dirs:        
            path = os.path.join(current, dir)
            if dir.endswith('_PLAYALL'):
                items.append([dir.rsplit('_PLAYALL', 1)[0], path, True, True])
            elif isPlayable(path, ignore, maxAge):
                items.append([dir, path, False, True])

    for file in files:
        path = os.path.join(current, file)
        if isPlayable(path, ignore, maxAge):
            items.append([removeExtension(file), path, True, False])

    return items

def removePartFiles():
    _removePartFiles(os.path.join(PROFILE, 'local'), recurse=True)
    _removePartFiles(getExternalDrive(), recurse=True)


def _removePartFiles(folder, recurse=True):
    current, dirs, files = sfile.walk(folder)

    for file in files:
        if file.endswith('.part'):
            file = os.path.join(current, file)
            tidyUp(file.rsplit('.part', 1)[0])
            #sfile.remove(file)
            #sfile.remove(file.rsplit('.part', 1)[0])

    if not recurse:
        return

    for dir in dirs:        
        folder = os.path.join(current, dir)
        _removePartFiles(folder, recurse)


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

    sfile.write(source, contents)
    
    return False


def updateAdvancedSettings(input):
    try:
        filename = 'advancedsettings.xml'
        source   = os.path.join('special://userdata', filename)

        if sfile.exists(source):
            contents = sfile.read(source)
            if input in contents:
                Log('%s already in %s' % (input, filename))
                return True

            Log('Updating %s with %s' % (filename, input))
            start = input.replace('>', ' >').split(' ', 1)[0].strip()
            end   = '</' + input.rsplit('</', 1)[-1].strip()

            start = contents.split(start, 1)[0]
            end   = contents.split(end, 1)[-1]

            contents = start
            if start != end:
                contents += end

            contents = contents.replace('</advancedsettings>', '%s</advancedsettings>' % input)
        else:
            Log('Creating %s with %s' % (filename, input))
            contents = '<advancedsettings>%s</advancedsettings>' % input
    except:
        Log('Error updating %s with %s' % (filename, input))
        Log('Resetting %s with %s' % (filename, input))
        contents = '<advancedsettings>%s</advancedsettings>' % input

    sfile.write(source, contents)
    
    return False


def systemUpdated(line1=None, line2='', line3=''):
    if line1:
        DialogOK(line1, line2, line3)
    xbmc.executebuiltin('RestartApp')


def getMD5(value):
    try:    
        from hashlib import md5
        MD5 = md5
    except: 
        import md5
        MD5 = md5.new

    return MD5(value).hexdigest()


def getLocalContent(url, ext):
    filename = None
    try:
        if sfile.isfile(url):
            filename = removeExtension(url) + '.' + ext
        
        if sfile.isdir(url):
            filename = url + '.' + ext

        if filename:
            return sfile.read(filename)

    except:
        pass

    return ''


def getAmazonContent(url, ext):
    try:
        folder = url.rsplit(DELIMETER, 1)[0]
        root   = folder + removeExtension(url.replace(folder, ''))

        nfo = root + '.' + ext
        nfo = s3.getURL(urllib.quote_plus(nfo)) 
        nfo = s3.convertToCloud(nfo)      

        plot = GetHTML(nfo, maxAge=28*86400)

        return plot
    except:
        pass

    return ''


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }


def escape(text):
    return str(''.join(html_escape_table.get(c,c) for c in text))


def unescape(text):
    text = text.replace('&amp;',  '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&apos;', '\'')
    text = text.replace('&gt;',   '>')
    text = text.replace('&lt;',   '<')
    return text


def fixUnicode(text):
    ret = ''
    for ch in text:
        if ord(ch) < 128 and ord(ch) > -1:
            ret += ch   
        else:
            ret += '%LB%' + format(ord(ch), 'x').upper()     
    return ret.strip()


def fix(text):
    ret = ''
    for ch in text:
        if ord(ch) < 128 and ord(ch) > -1:
            ret += ch   
        else:
            ret += '<%d>' % ord(ch)     
    return ret.strip()


def patchAmazonImage(mode, image, url, infoLabels):
    folder = url.rsplit(DELIMETER, 1)[0]
    files  = s3.getAllFiles(folder, recurse=False)
    root   = folder + removeExtension(url.replace(folder, ''))
    root   = urllib.quote_plus(root).replace('%25LB%25', '%')
   
    for ext in IMG_EXT: 
        img  = root + ext

        for file in files:
            file =  urllib.quote_plus(file.encode('utf-8'))
            if img == file:
                img = s3.convertToCloud(s3.getURL(img))
                gif = s3.convertToCloud(s3.getURL(root + '.gif'))

                infoLabels['Gif'] = img

                #Kodi incorrectly handles remote gifs therefore download and store locally
                gifFolder = os.path.join(PROFILE, 'c')

                filename  = os.path.join(gifFolder, getMD5(url.split('?', 1)[0])) + '.gif'

                if sfile.exists(filename):
                    if sfile.size(filename) > 0:
                        infoLabels['Gif'] = filename
                else:   
                    if DownloadIfExists(gif, filename):
                        infoLabels['Gif'] = filename   
                    else:                    
                        sfile.file(filename, 'w') #create empty file so we don't check again   
                  
                return img

    if mode == AMAZON_FOLDER:
        return DEFAULTFOLDER

    if mode == AMAZON_FILE:
        return DEFAULTMOVIE


def patchImage(mode, image, url, infoLabels):
    if mode == SERVER_FOLDER:
        return DEFAULTFOLDER

    if mode == AMAZON_FOLDER or mode == AMAZON_FILE:
        return patchAmazonImage(mode, image, url, infoLabels)
             
    if not image:
        return DEFAULTMOVIE

    if image == DEFAULTMOVIE or image == DEFAULTFOLDER:
        root = removeExtension(url)
        for ext in IMG_EXT:        
            img  = root + ext
           
            if sfile.exists(img):
                if sfile.exists(root + '.gif'):
                    infoLabels['Gif'] = root + '.gif'
                else:
                    infoLabels['Gif'] = img
                return img            

    return image 


def GetTitleAndImage(path):
    root  = removeExtension(path)
    title = root.rsplit(os.sep, 1)[-1]
    title = title.rsplit(DELIMETER, 1)[-1]

    for ext in IMG_EXT:            
        image = root + ext
        if sfile.exists(image):               
            return title.replace('_', ' '), image

    return title.replace('_', ' '), ICON


def DownloadIfExists(url, dst):
    import download
    if not download.getResponse(url, 0, ''):
        return False

    download.download(url, dst)
    return True


def DoDownload(name, dst, src, image=None, orignalSrc=None, progressClose=True, silent=False):
    import download
    import s3
    import sfile

    dst = dst.replace(os.sep, DELIMETER)
    src = src.replace(os.sep, DELIMETER)

    if orignalSrc == None or len(orignalSrc) == 0:
        orignalSrc = src

    temp  = dst + '.temp'

    url = urllib.quote_plus(src)
    url = s3.getURL(url)
    url = s3.convertToCloud(url)

    #image no longer used
    #if image and image.startswith('http'):
    #    pass
    #else:
    #    image = None
    image = None

    resp = download.getResponse(url, 0, '')
    if not resp:
        return 1

    dp = None

    name = name.decode('utf-8')

    if not silent:
        dp = DialogProgress(GETTEXT(30079) % name)
        
    download.doDownload(url, temp, name, dp=dp, silent=silent)
    
    if dp and progressClose:
        dp.close()

    if sfile.exists(temp + '.part'): #if part file exists then download has failed
        return 1

    if not sfile.exists(temp): #download was cancelled
        return 2

    sfile.remove(dst)
    sfile.rename(temp, dst)

    src = orignalSrc

    #recursively get dsc files
    dscFile = removeExtension(dst) + '.%s' % DSC
    while len(src) > 0:
        try:
            plot = getAmazonContent(src, DSC)
            sfile.write(dscFile, plot)

            newSrc = src.rsplit(DELIMETER, 1)[0]
            if newSrc == src:
                break

            src     = newSrc 
            dscFile = dscFile.rsplit(DELIMETER, 1)[0] + '.%s' % DSC

        except:
            pass


    #original image handling - no longer used
    if image:            
        img   = image.rsplit('?', 1)[0]
        ext   = img.rsplit('.'  , 1)[-1]
        root  = dst.rsplit('.'  , 1)[0]
        jpg   = root + '.%s' %  ext
        gif   = root + '.%s' % 'gif'

        gifURL = s3.getURL(urllib.quote_plus(_src.rsplit('.', 1)[0] + '.gif'))
        
        DownloadIfExists(image,  jpg)
        DownloadIfExists(gifURL, gif)


    #recursively get image files
    src = orignalSrc.rsplit('.', 1)[0]
    dst = dst.rsplit('.', 1)[0]

    imageTypes = IMG_EXT
    imageTypes.append('.gif')

    while len(src) > 0:
        for ext in imageTypes: 
            image = src + ext

            image = s3.getURL(urllib.quote_plus(image))
            image = s3.convertToCloud(image)

            DownloadIfExists(image, dst+ext)

        newSrc = src.rsplit(DELIMETER, 1)[0]

        if newSrc == src:    
            break

        src = newSrc 
        dst = dst.rsplit(DELIMETER, 1)[0]

    return 0

import threading
class Downloader(threading.Thread):
     def __init__(self, name, dst, src, postDownload=None):
         super(Downloader, self).__init__()
         self.name         = name
         self.dst          = dst
         self.src          = src
         self.postDownload = postDownload

     def run(self):
         Log('Starting threaded downloader')
         Log('name    = %s' % self.name)
         Log('dst     = %s' % self.dst)
         Log('src     = %s' % self.src)

         if sfile.exists(self.dst + '.temp.part'): #if temp.part file exists then download is already in progress
             Log('Request to download a file that is currently downloading: %s' % self.dst)
             success = False
         else:
             success = DoDownload(self.name, self.dst, self.src, silent=True)
             success = success == 0
             Log('success = %d' % success)

         if self.postDownload:
             self.postDownload(success)


def DoThreadedDownload(name, dst, src, postDownload=None):
    downloader = Downloader(name, dst, src, postDownload)
    downloader.start()


def tidyUp(filename):
    sfile.remove(filename+'.part')
    delete(filename)
    #sfile.remove(filename)
    #sfile.remove(filename+'.part')


def delete(path, APPLICATION=None):
    path = path.replace(DELIMETER, os.sep)
    
    if sfile.isdir(path):        
        _DeleteFolder(path, APPLICATION)
    else:
        _DeleteFile(path, APPLICATION) 

    if APPLICATION:
        APPLICATION.containerRefresh()


def getResolution():
    try:
        resolution = xbmc.getInfoLabel('System.ScreenResolution')
        resolution = resolution.split(' ')[0]
        resolution = resolution.split('@')[0]
    except:
        resolution = 'unknown'

    return resolution
        


def _DeleteFolder(folder, APPLICATION):
    if not sfile.isempty(folder):
        if not DialogYesNo(GETTEXT(30104), GETTEXT(30105)):
            return

    sfile.delete(folder)

    files = sfile.related(folder)
    
    for file in files:
        sfile.delete(file)

    if APPLICATION:
        APPLICATION.containerRefresh()


def _DeleteFile(filename, APPLICATION):
    files = sfile.related(filename)
    for file in files:
        sfile.delete(file)

    folder = sfile.getfolder(filename)
    if sfile.isempty(folder):
        try:
            sfile.delete(folder)
            APPLICATION.containerRefresh()
        except:
            pass


def enableAutoUpdates():
    ON     = 0
    NOTIFY = 1
    NEVER  = 2
    setKodiSetting('general.addonupdates', ON)
    xbmc.sleep(250)


def disableAutoUpdates():
    ON     = 0
    NOTIFY = 1
    NEVER  = 2
    setKodiSetting('general.addonnotifications', False)
    setKodiSetting('general.addonupdates', NEVER)