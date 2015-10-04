
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

import urllib
import random
import re
import os

import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui


import utils


ADDON  = utils.ADDON
HOME   = utils.HOME

ICON   = utils.ICON
FANART = utils.FANART

DSC = utils.DSC
SRC = utils.SRC


VIDEO_ADDON           = utils.VIDEO_ADDON
SERVER_FILE           = utils.SERVER_FILE
LOCAL_FILE            = utils.LOCAL_FILE
SETTINGS              = utils.SETTINGS
CLEARCACHE            = utils.CLEARCACHE
WAITING               = utils.WAITING
EXAM                  = utils.EXAM
DEMO                  = utils.DEMO
SERVER_FOLDER         = utils.SERVER_FOLDER
LOCAL_FOLDER          = utils.LOCAL_FOLDER
AMAZON_FILE           = utils.AMAZON_FILE
AMAZON_FOLDER         = utils.AMAZON_FOLDER
LOCAL_PLAYABLE_FOLDER = utils.LOCAL_PLAYABLE_FOLDER
UPDATE_FILE_CHK       = utils.UPDATE_FILE_CHK
UPDATE_FILE           = utils.UPDATE_FILE
DELETE_LOCAL_FILE     = utils.DELETE_LOCAL_FILE

SERVER          = utils.SERVER
LBVERSION       = utils.LBVERSION
ADDRESS         = utils.ADDRESS


# Settings
SHOW_CONFIGURE = utils.SHOW_CONFIGURE
SHOW_REFRESH   = utils.SHOW_REFRESH
SHOW_DOWNLOAD  = utils.SHOW_DOWNLOAD
SHOW_VIMEO     = utils.SHOW_VIMEO
SHOW_AMAZON    = utils.SHOW_AMAZON
SHOW_LOCAL     = utils.SHOW_LOCAL



GETTEXT = utils.GETTEXT
URL     = 'https://vimeo.com/channels/%s/videos/rss'


global APPLICATION



def NoPlay(reason):
    utils.Log(reason)
    setResolvedUrl(url='', success=False)


def SetResolvedUrl(url, success=True, listItem=None, windowed=True):
    APPLICATION.setResolvedUrl(url, success=success, listItem=listItem, windowed=windowed)


def GetJSON(params, timeout):
    addr, port = utils.GetHost()
       
    try:
        return utils.GetJSON(addr, port, params, timeout)
    except:
        pass

    return {}


def GetFiles(params, timeout):
    resp = GetJSON(params, timeout)
        
    if 'result' not in resp:
        return []

    if 'files' not in resp['result']:
        return []

    return resp['result']['files']


def ParseListItem(item):
    index      = int(urllib.unquote_plus(item['index']))
    name       = urllib.unquote_plus(item['name'])
    mode       = int(urllib.unquote_plus(item['mode']))
    url        = urllib.unquote_plus(item['url'])
    image      = urllib.unquote_plus(item['image'])
    fanart     = urllib.unquote_plus(item['fanart'])
    isFolder   = urllib.unquote_plus(item['isFolder'])   == 'True'
    isPlayable = urllib.unquote_plus(item['isPlayable']) == 'True'
    desc       = urllib.unquote_plus(item['desc'])
    plot       = urllib.unquote_plus(item['plot'])

    return [index, name, mode, url, image, fanart, isFolder, isPlayable, desc, plot]


def GetListItems(params, timeout=60):
    files = GetFiles(params, timeout)

    if files == None:
        return []

    list = []

    for file in files:
        if 'file' in file:
            file   = file['file']
            params = get_params(file)
            try:    
                info = urllib.unquote_plus(params['info'])
                item = ParseListItem(get_params(info))
                list.append(item)
            except:
                pass
    list.sort()
    return list


def PlayVideo(mode, url, title='', image=''):
    if mode == AMAZON_FILE:
        return PlayAmazonVideo(mode, url, title, image)

    _PlayVideo(mode, url, title, image)


def _PlayVideo(mode, url, title, image):
    APPLICATION.showBusy()

    addr, port = utils.GetHost()
    url = utils.GetAddonMessage(addr, port, utils.RETRIEVE_URL, {'type':mode, 'url':urllib.quote_plus(url), 'server':utils.IsServer()}, timeout=60)

    APPLICATION.closeBusy()
    
    if len(url) == 0:
        return NoPlay('Empty URL obtained in PlayVideo')

    PlayResolvedVideo(mode, url, title, image)


def PlayResolvedVideo(mode, url, title='', image='', repeatMode=None):
    img = image
    if len(img) == 0:
        img = ICON

    label = title
    if len(label) == 0:
        label = GETTEXT(30000)

    if not repeatMode:
        repeatMode = GetRepeatMode()

    liz = xbmcgui.ListItem(label, iconImage=img, thumbnailImage=img)

    liz.setInfo(type='Video', infoLabels={'Title': label})

    windowed = utils.getSetting('PLAYBACK') == '1'

    if mode == VIDEO_ADDON or mode == LOCAL_FILE:
        PlayAddonVideo(url, liz, windowed)

    if mode == SERVER_FILE or mode == AMAZON_FILE:
        PlayServerVideo(url, liz, windowed)

    xbmc.executebuiltin('PlayerControl(%s)' % repeatMode)
        


def PlayAddonVideo(url, liz, windowed):
    SetResolvedUrl(url, success=True, listItem=liz, windowed=windowed)


def PlayAmazonVideo(mode, url, title, image):
    #if utils.getSetting('DOWNLOAD_LOC') == '1':
    #    return _PlayVideo(mode, url, title, image)
 
    import s3
    import sfile

    loc = utils.getDownloadLocation()

    if not sfile.exists(loc):
        utils.DialogOK(GETTEXT(30095), GETTEXT(30096))
        return

    client = utils.GetClient() + s3.DELIMETER        
    dst    = os.path.join(loc, url.replace(client, ''))

    DownloadFile(title, url, dst, image)


def PlayServerVideo(url, liz, windowed):
    if url.startswith('http'):
        pass
    else:
        addr, port = utils.GetHost()

        #url = urllib.quote_plus(url)
        #url = 'http://%s:%d/vfs/%s' % (addr, port, url)
    
    utils.Log('Playback URL %s' % url)
    
    SetResolvedUrl(url, success=True, listItem=liz, windowed=windowed)


def getGlobalMenu():
    menu = []
    menu.append((GETTEXT(30020), '?mode=%d' % SETTINGS))
    return menu


def DoMainList():
    menu = getGlobalMenu()

    list = GetListItems('plugin://plugin.video.thelivebox/?mode=', timeout=60)

    for item in list:
        mode = item[2]
        #if mode == AMAZON_FILE or mode == AMAZON_FOLDER:                   
        #    pass
        #else:
        #    AddDir(item[1], item[2], url=item[3], isFolder=item[6], desc=item[8], plot=item[9], contextMenu=menu, replaceItems=True)
        AddDir(item[1], item[2], url=item[3], isFolder=item[6], desc=item[8], plot=item[9], contextMenu=menu, replaceItems=True)

    return len(list) > 0


def AddFolderItems(_folder):
    if not SHOW_LOCAL:
        return

    items = utils.parseFolder(_folder, GETTEXT(30058))
    if len(items) == 0:
        return

    browseFolder = utils.GETTEXT(30055)
    playVideo    = utils.GETTEXT(30056)
    playFolder   = utils.GETTEXT(30098)

    file   = 'DefaultMovies.png'
    folder = 'DefaultFolder.png'

    for item in items:
        label      = item[0]
        url        = item[1]
        isPlayable = item[2]
        isFolder   = item[3]
        plot       = utils.getLocalContent(url, DSC)

        if isPlayable:
            if isFolder:
                menu = getGlobalMenu()
                menu.append((GETTEXT(30062), '?mode=%d&url=%s' % (LOCAL_PLAYABLE_FOLDER, url)))
                AddDir(label, LOCAL_PLAYABLE_FOLDER, url=url, image=file,   isFolder=False, isPlayable=True,  desc=playFolder,   plot=plot, contextMenu=menu, replaceItems=True)
            else:
                menu = getGlobalMenu()
                menu.append((GETTEXT(30063), '?mode=%d&url=%s' % (LOCAL_PLAYABLE_FOLDER, _folder)))
                menu.append((GETTEXT(30097), '?mode=%d&url=%s' % (DELETE_LOCAL_FILE, url)))
                AddDir(label, LOCAL_FILE,            url=url, image=file,   isFolder=False, isPlayable=True,  desc=playVideo,    plot=plot, contextMenu=menu, replaceItems=True)
        else:
            menu = getGlobalMenu()
            menu.append((GETTEXT(30062), '?mode=%d&url=%s' % (LOCAL_PLAYABLE_FOLDER, url)))
            AddDir(label, LOCAL_FOLDER,              url=url, image=folder, isFolder=True,  isPlayable=False, desc=browseFolder, plot=plot, contextMenu=menu, replaceItems=True)


def MainList():
    attempts = 0
    while attempts < 5:
        attempts += 1
        if DoMainList():
            return
        xbmc.sleep(100)

    xbmc.sleep(5000)

    #try again
    if DoMainList():
        return

    showSettings = False
    if showSettings:
        utils.DialogOK(GETTEXT(30043), GETTEXT(30044))

        APPLICATION.addonSettings()

        if DoMainList():
            return

    showFallackMessage = False
    if showFallackMessage:
        utils.DialogOK(GETTEXT(30043), GETTEXT(30052))

    utils.setSetting('FALLBACK', 'true')
    if DoMainList():
        return   

def GenericList(mode):
    menu = []
    menu.append((GETTEXT(30020), '?mode=%d' % SETTINGS))

    list = 'plugin://plugin.video.thelivebox/?mode=%d' % mode
    list = GetListItems(list)

    for item in list:
        AddDir(item[1], item[2], url=item[3], isFolder=item[6], desc=item[8], plot=item[9], contextMenu=menu, replaceItems=True)        


def ClearCache():
    APPLICATION.showBusy()
    resp = GetJSON('plugin://plugin.video.thelivebox/?mode=%d' % CLEARCACHE, 60)
    APPLICATION.closeBusy()
        
    if 'result' not in resp:
        return

    utils.DialogOK(GETTEXT(30064))


def ExaminationRoom():
    videos = GetVimeoVideos()
   
    menu = []
    menu.append((GETTEXT(30020), '?mode=%d' % SETTINGS))

    for video in videos:
        image  = video[2]
        fanart = image.replace('_200x150.jpg', '_1200x800.jpg')
        AddDir(video[0], VIDEO_ADDON, video[1], image, fanart, isPlayable=True, desc=video[3], plot=video[4], contextMenu=menu, replaceItems=True)


def WaitingRoom():
    videos = GetVimeoVideos()

    pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    pl.clear()  

    isFirst = True

    repeatMode = GetRepeatMode()

    for video in videos:
        title  = video[0]
        url    = video[1]
        image  = video[2]

        if len(image) == 0:
            image = ICON

        if len(title) == 0:
            title = GETTEXT(30000)

        liz = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)

        liz.setInfo(type='Video', infoLabels={'Title': title})

        pl.add(url, liz)

        if isFirst:
            isFirst  = False
            windowed = utils.getSetting('PLAYBACK') == '1'
            SetResolvedUrl(url, success=True, listItem=liz, windowed=windowed)


    xbmc.executebuiltin('PlayerControl(%s)' % repeatMode)


def PlayFolder(folder):
    videos = utils.getAllPlayableFiles(folder)

    pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    pl.clear()  

    isFirst = True

    repeatMode = GetRepeatMode()

    title = GETTEXT(30000)
    image = ICON

    for video in videos:
        liz = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)

        liz.setInfo(type='Video', infoLabels={'Title': title})

        pl.add(video, liz)

        if isFirst:
            isFirst  = False
            windowed = utils.getSetting('PLAYBACK') == '1'
            SetResolvedUrl(video, success=True, listItem=liz, windowed=windowed)

    xbmc.executebuiltin('PlayerControl(%s)' % repeatMode)


def UpdateFile(url):
    if not utils.IsServer():
        return

    items = url.split('&')
    name  = urllib.unquote_plus(items[0].split('=', 1)[-1])
    src   = urllib.unquote_plus(items[1].split('=', 1)[-1])
    dst   = urllib.unquote_plus(items[2].split('=', 1)[-1])

    DownloadFile(name, src,  dst)


def Delete(filename):
    import sfile

    files = sfile.related(filename)
    for file in files:
        sfile.delete(file)


def DownloadFile(name, _src,  dst, image=None):
    import download
    import s3
    import sfile

    src = _src

    isSrc = src.lower().endswith('.txt') or src.lower().endswith('.%s' % SRC)
    if isSrc:
        src = urllib.quote_plus(src)
        src = s3.getURL(src)
        src = s3.convertToCloud(src)
        src = utils.GetHTML(src, maxAge=7*86400)

        #replace extension on destination
        dst = dst.rsplit('.', 1)[0] + '.' + src.rsplit('.', 1)[-1]

    autoPlay   = True
    repeatMode = False
    thumb      = ICON

    if sfile.exists(dst):
        autoPlay   = True
        repeatMode = GetRepeatMode()
        root       = dst.rsplit('.', 1)[0]
        jpg        = root + '.jpg'
        png        = root + '.png'
        if sfile.exists(jpg):
            thumb = jpg
        elif sfile.exists(png):
            thumb = png

    else:
        autoPlay = False
        if utils.DialogYesNo(utils.GETTEXT(30085), utils.GETTEXT(30086)):
            autoPlay   = True
            repeatMode = GetRepeatMode()

        temp  = dst + '.temp'

        url = urllib.quote_plus(src)
        url = s3.getURL(url)
        url = s3.convertToCloud(url)

        if image and image.startswith('http'):
            pass
        else:
            image = None

        dp = utils.DialogProgress(GETTEXT(30079) % name)
        download.doDownload(url, temp, name, dp=dp)
        dp.close()

        if sfile.exists(temp + '.part'): #if part file exists then download has failed
            utils.DialogOK(name, utils.GETTEXT(30081))
            return

        if not sfile.exists(temp):
            return

        sfile.remove(dst)
        sfile.rename(temp, dst)

        try:
            plot = utils.getAmazonContent(_src, DSC)
            if len(plot) > 0:      
                plotFile = dst.rsplit('.', 1)[0] + '.%s' % DSC
                f = sfile.file(plotFile, 'w')
                f.write(plot)
                f.close()
        except:
            pass

        if image:            
            img   = image.rsplit('?', 1)[0]
            ext   = img.rsplit('.'  , 1)[-1]
            root  = dst.rsplit('.'  , 1)[0]
            jpg   = root + '.%s' %  ext
            gif   = root + '.%s' % 'gif'

            download.download(image, jpg)
            thumb = jpg

            gifURL = s3.getURL(urllib.quote_plus(_src.rsplit('.', 1)[0] + '.gif'))
            resp = download.getResponse(gifURL, 0, '')
            if resp:
                download.download(gifURL, gif)

    if autoPlay:
        xbmcgui.Window(10000).setProperty('LB_AUTOPLAY', 'True')
        APPLICATION.containerRefresh()
        PlayResolvedVideo(LOCAL_FILE, dst, name, thumb, repeatMode)        
    else:
        utils.DialogOK(name, utils.GETTEXT(30082))
        APPLICATION.containerRefresh()
    

def GetRepeatMode():
    repeatMode = 'RepeatOff'
    if not utils.DialogYesNo(GETTEXT(30008), GETTEXT(30009), GETTEXT(30010), GETTEXT(30011), GETTEXT(30012)):
         repeatMode = 'RepeatAll'

    return repeatMode


def ParseLocalFolder(url):
    AddFolderItems(url)


def ParseRemoteFolder(url, mode):   
    videos = []

    list = 'plugin://plugin.video.thelivebox/?mode=%d&url=%s' % (mode, urllib.quote_plus(url))
    list = GetListItems(urllib.quote_plus(list), timeout=120)

    menu = getGlobalMenu()

    for item in list:
        name       = item[1]
        mode       = item[2]
        url        = item[3]
        image      = item[4]
        fanart     = item[5]
        isFolder   = item[6]
        isPlayable = item[7]
        desc       = item[8]
        plot       = item[9]
        AddDir(name, mode, url, image, fanart, isFolder, isPlayable, desc, plot, contextMenu=menu, replaceItems=True, infoLabels=None)

          
def GetVimeoVideos():
    videos = []

    list = GetListItems('plugin://plugin.video.thelivebox/?mode=%d' % EXAM)
    for item in list: #title, id, image, desc,plot
        videos.append([item[1], item[3], item[4], item[8], item[9]])

    return videos


def validateMode(mode, name):
    if mode == SERVER_FOLDER:
        if name == GETTEXT(30057):
            if utils.IsServer():
                return False
            if utils.getSetting('FALLBACK').lower() == 'true':
                return False

    return True


def AddDir(name, mode, url=None, image=None, fanart=None, isFolder=False, isPlayable=False, desc='', plot='', contextMenu=None, replaceItems=False, infoLabels=None):

    if not validateMode(mode, name):
        return

    if not fanart:
        fanart = FANART

    name = name.replace('_', ' ')

    infoLabels = {'title':name, 'fanart':fanart, 'description':desc, 'plot':plot}    

    image = utils.patchImage(mode, image, url, infoLabels)
 
    u  = ''
    u += '?mode='  + str(mode)
    u += '&title=' + urllib.quote_plus(name)

    if image:
        u += '&image=' + urllib.quote_plus(image)

    if url:
        u += '&url=' + urllib.quote_plus(url)

    APPLICATION.addDir(name, mode, u, image, isFolder, isPlayable, contextMenu=contextMenu, replaceItems=replaceItems, infoLabels=infoLabels)

    
def get_params(params):
    if not params:
        return {}

    param = {}

    cleanedparams = params.replace('?','')

    if (params[len(params)-1] == '/'):
       params = params[0:len(params)-2]

    pairsofparams = cleanedparams.split('&')    

    for i in range(len(pairsofparams)):
        splitparams = pairsofparams[i].split('=')

        if len(splitparams) == 2:
            param[splitparams[0]] = splitparams[1]

    return param


def onBack(application, params):
    if params == 'init':
        application.containerRefresh()


def main(params):
    try:    mode = int(urllib.unquote_plus(params['mode']))
    except: mode = None

    try:    url   = urllib.unquote_plus(params['url'])
    except: url = ''

    try:    utils.Log('Selected mode = %s' % str(mode))
    except: pass

    if mode == VIDEO_ADDON or mode == SERVER_FILE or mode == AMAZON_FILE:
        try:    
            try:    title = urllib.unquote_plus(params['title'])
            except: title = ''

            try:    image = urllib.unquote_plus(params['image'])
            except: image = ''
            
            PlayVideo(mode, url, title, image)

        except Exception, e:
            utils.Log('Error in VIDEO mode(%d) - %s' % (mode, str(e)))
            APPLICATION.closeBusy()            


    elif mode == LOCAL_FILE:
        try:    
            try:    title = urllib.unquote_plus(params['title'])
            except: title = ''

            try:    image = urllib.unquote_plus(params['image'])
            except: image = ''
            
            PlayResolvedVideo(mode, url, title, image)

        except Exception, e:
            utils.Log('Error in LOCAL_FILE mode - %s' % str(e))

    elif mode == DELETE_LOCAL_FILE:
        Delete(url)
        APPLICATION.containerRefresh()
        

    elif mode == SERVER_FOLDER or mode == AMAZON_FOLDER:
        try:    
            ParseRemoteFolder(url, mode)

        except Exception, e:
            utils.Log('Error in SERVER_FOLDER mode(%d) - %s' % (mode, str(e)))


    elif mode == LOCAL_FOLDER:
        try:    
            ParseLocalFolder(url)

        except Exception, e:
            utils.Log('Error in LOCAL_FOLDER mode - %s' % str(e))


    elif mode == CLEARCACHE:
        ClearCache()


    elif mode == SETTINGS:
        APPLICATION.closeBusy()
        APPLICATION.addonSettings()
        xbmcgui.Window(10000).setProperty('LB_RESTART_SCAN', 'True')


    elif mode == WAITING:
        WaitingRoom()


    elif mode == EXAM:
        ExaminationRoom()


    elif mode == ADDRESS:
        GenericList(ADDRESS)


    elif mode == SERVER:
        GenericList(SERVER)


    elif mode == LBVERSION:
        GenericList(LBVERSION)


    elif mode == DEMO:
        GenericList(DEMO)


    elif mode == UPDATE_FILE_CHK:
        import sfile
        extDrive = utils.getExternalDrive()
        if not sfile.exists(extDrive):
            APPLICATION.closeBusy()
            utils.DialogOK(GETTEXT(30087) , GETTEXT(30088))
        else:
            GenericList(UPDATE_FILE_CHK)

    elif mode == UPDATE_FILE:
        UpdateFile(url)


    elif mode == LOCAL_PLAYABLE_FOLDER:
        PlayFolder(url)

    else:
        MainList()
        AddFolderItems('')

    if utils.getSetting('FALLBACK').lower() == 'true':
        mode = GETTEXT(30053)
    elif utils.IsServer():
        mode  = GETTEXT(30046)    
    else:
        mode  = GETTEXT(30045)


    title  = '%s [COLOR=blue]-[/COLOR] v%s' % (GETTEXT(30000), utils.VERSION) + ' [COLOR=blue]-[/COLOR] ' + mode
    footer = '%s [COLOR=blue]-[/COLOR] v%s' % (GETTEXT(30000), utils.VERSION) + ' [COLOR=blue]-[/COLOR] ' + mode

    APPLICATION.setProperty('LB_TITLE',    title)
    APPLICATION.setProperty('LB_MAINDESC', GETTEXT(30019))
    APPLICATION.setProperty('LB_FOOTER', footer)


def onParams(application, params):
    global APPLICATION
    APPLICATION = application

    params = get_params(params)
    main(params)