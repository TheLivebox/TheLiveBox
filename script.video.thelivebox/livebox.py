
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

SERVER          = utils.SERVER
LBVERSION       = utils.LBVERSION
ADDRESS         = utils.ADDRESS


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

    return [index, name, mode, url, image, fanart, isFolder, isPlayable, desc]


def GetListItems(params, timeout=60):
    list = []
    files = GetFiles(params, timeout)

    if files == None:
        return list

    for file in files:
        if 'file' in file:
            file   = file['file']
            params = get_params(file)
            try:    
                info = urllib.unquote_plus(params['info'])
                list.append(ParseListItem(get_params(info)))
            except:
                pass
    list.sort()
    return list


def PlayVideo(mode, url, title='', image=''):
    APPLICATION.showBusy()

    addr, port = utils.GetHost()
    url = utils.GetAddonMessage(addr, port, utils.RETRIEVE_URL, {'type':mode, 'url':urllib.quote_plus(url), 'server':utils.IsServer()}, timeout=60)

    APPLICATION.closeBusy()
    
    if len(url) == 0:
        return NoPlay('Empty URL obtained in PlayVideo')

    PlayResolvedVideo(mode, url, title, image)


def PlayResolvedVideo(mode, url, title='', image=''):
    img = image
    if len(img) == 0:
        img = ICON

    label = title
    if len(label) == 0:
        label = GETTEXT(30000)

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
    APPLICATION.setResolvedUrl(url, success=True, listItem=liz, windowed=windowed)


def PlayServerVideo(url, liz, windowed):
    if url.startswith('http'):
        pass
    else:
        addr, port = utils.GetHost()

        url = urllib.quote_plus(url)
        url = 'http://%s:%d/vfs/%s' % (addr, port, url)
    
    utils.Log('Playback URL %s' % url)
    
    APPLICATION.setResolvedUrl(url, success=True, listItem=liz, windowed=windowed)


def getGlobalMenu():
    menu = []
    menu.append((GETTEXT(30020), '?mode=%d' % SETTINGS))
    return menu


def DoMainList():
    menu = getGlobalMenu()

    list = GetListItems('plugin://plugin.video.thelivebox/?mode=', timeout=60)
    for item in list:
        mode = item[2]
        if mode == AMAZON_FILE or mode == AMAZON_FOLDER:
        #if False:
            pass
        else:           
            AddDir(item[1], item[2], url=item[3], isFolder=item[6], desc=item[8], contextMenu=menu, replaceItems=True)

    return len(list) > 0


def AddFolderItems(_folder):
    items = utils.parseFolder(_folder, GETTEXT(30058))
    if len(items) == 0:
        return

    browseFolder = utils.GETTEXT(30055)
    playVideo    = utils.GETTEXT(30056)
    playFolder   = utils.GETTEXT(30062)

    file   = 'DefaultMovies.png'
    folder = 'DefaultFolder.png'

    for item in items:
        label      = item[0]
        url        = item[1]
        isPlayable = item[2]
        isFolder   = item[3]

        if isPlayable:
            if isFolder:
                menu = getGlobalMenu()
                menu.append((GETTEXT(30062), '?mode=%d&url=%s' % (LOCAL_PLAYABLE_FOLDER, url)))
                AddDir(label, LOCAL_PLAYABLE_FOLDER, url=url, image=file,   isFolder=False, isPlayable=True,  desc=playFolder,   contextMenu=menu, replaceItems=True)
            else:
                menu = getGlobalMenu()
                menu.append((GETTEXT(30063), '?mode=%d&url=%s' % (LOCAL_PLAYABLE_FOLDER, _folder)))
                AddDir(label, LOCAL_FILE,            url=url, image=file,   isFolder=False, isPlayable=True,  desc=playVideo,    contextMenu=menu, replaceItems=True)
        else:
            menu = getGlobalMenu()
            menu.append((GETTEXT(30062), '?mode=%d&url=%s' % (LOCAL_PLAYABLE_FOLDER, url)))
            AddDir(label, LOCAL_FOLDER,              url=url, image=folder, isFolder=True,  isPlayable=False, desc=browseFolder, contextMenu=menu, replaceItems=True)


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
        AddDir(item[1], item[2], url=item[3], isFolder=item[6], desc=item[8], contextMenu=menu, replaceItems=True)        


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
        AddDir(video[0], VIDEO_ADDON, video[1], image, fanart, isPlayable=True, desc=video[3], contextMenu=menu, replaceItems=True)


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
    videos = utils.parseFolder(folder, recurse=False)

    pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    pl.clear()  

    isFirst = True

    repeatMode = GetRepeatMode()

    for video in videos:
        image      = ''
        title      = video[0]
        url        = video[1]
        isPlayable = video[2]
        isFolder   = video[3]

        if (not isPlayable) or isFolder:
            continue

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
        AddDir(name, mode, url, image, fanart, isFolder, isPlayable, desc, contextMenu=menu, replaceItems=True, infoLabels=None)

          
def GetVimeoVideos():
    videos = []

    list = GetListItems('plugin://plugin.video.thelivebox/?mode=%d' % EXAM)
    for item in list: #title, id, image, desc
        videos.append([item[1], item[3], item[4], item[8]])

    return videos


def PatchImage(mode, image):
    if mode == SERVER_FOLDER:
        return 'DefaultFolder.png'

    if mode == AMAZON_FOLDER:
        return 'DefaultFolder.png'

    return image


def validateMode(mode, name):
    if mode == SERVER_FOLDER:
        if name == GETTEXT(30057):
            if utils.IsServer():
                return False
            if utils.getSetting('FALLBACK').lower() == 'true':
                return False

    return True


def AddDir(name, mode, url=None, image=None, fanart=None, isFolder=False, isPlayable=False, desc='', contextMenu=None, replaceItems=False, infoLabels=None):

    if not validateMode(mode, name):
        return

    image = PatchImage(mode, image)
 
    if not image:
        image = ICON

    if not fanart:
        fanart = FANART

    u  = ''
    u += '?mode='  + str(mode)
    u += '&title=' + urllib.quote_plus(name)

    if image:
        u += '&image=' + urllib.quote_plus(image)

    if url:
        u += '&url=' + urllib.quote_plus(url)

    infoLabels = {'title':name, 'fanart':fanart, 'description':desc}

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


def refresh():
    xbmc.executebuiltin('Container.Refresh')


def main(params):
    try:    mode = int(urllib.unquote_plus(params['mode']))
    except: mode = None

    try:    url   = urllib.unquote_plus(params['url'])
    except: url = ''


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
        

    elif mode == SERVER_FOLDER or mode == mode == AMAZON_FOLDER:
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


    title = GETTEXT(30000) + ' [COLOR=blue]-[/COLOR] ' + mode


    APPLICATION.setProperty('LB_TITLE',    title)
    APPLICATION.setProperty('LB_MAINDESC', GETTEXT(30019))


def onParams(application, params):
    global APPLICATION
    APPLICATION = application

    params = get_params(params)
    main(params)