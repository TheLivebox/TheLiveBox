
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


VIDEO_ADDON = utils.VIDEO_ADDON
VIDEO_LOCAL = utils.VIDEO_LOCAL
CLEARCACHE  = utils.CLEARCACHE
SETTINGS    = utils.SETTINGS
WAITING     = utils.WAITING
EXAM        = utils.EXAM
DEMO        = utils.DEMO

SERVER      = utils.SERVER
LBVERSION   = utils.LBVERSION
ADDRESS     = utils.ADDRESS


GETTEXT = utils.GETTEXT
URL     = 'https://vimeo.com/channels/%s/videos/rss'


global APPLICATION



def NoPlay(reason):
    utils.Log(reason)
    setResolvedUrl(url='', success=False)


def SetResolvedUrl(url, success=True, listItem=None, windowed=True):
    APPLICATION.setResolvedUrl(url, success=success, listItem=listItem, windowed=windowed)


def GetJSON(params):
    addr, port = utils.GetHost()

    try:
        return utils.GetJSON(addr, port, params)
    except:
        pass

    return {}


def GetFiles(params):
    resp = GetJSON(params)
        
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


def GetListItems(params):
    list = []
    files = GetFiles(params)

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
    addr, port = utils.GetHost()
    url = utils.GetAddonMessage(addr, port, utils.RETRIEVE_URL, {'type':mode, 'url':urllib.quote_plus(url)})
    
    if len(url) == 0:
        return NoPlay('Empty URL obtained in PlayAddonVideo')
 
    img   = image
    if len(img) == 0:
        img = ICON

    label = title
    if len(label) == 0:
        label = GETTEXT(30000)

    repeatMode = GetRepeatMode()


    liz = xbmcgui.ListItem(label, iconImage=img, thumbnailImage=img)

    liz.setInfo(type='Video', infoLabels={'Title': label})

    windowed = utils.getSetting('PLAYBACK') == '1'

    if mode == VIDEO_ADDON:
        PlayAddonVideo(url, liz, windowed)

    if mode == VIDEO_LOCAL:
        PlayLocalVideo(url, liz, windowed)


    xbmc.executebuiltin('PlayerControl(%s)' % repeatMode)
        

def PlayAddonVideo(url, liz, windowed):
    APPLICATION.setResolvedUrl(url, success=True, listItem=liz, windowed=windowed)


def PlayLocalVideo(url, liz, windowed):
    addr, port = utils.GetHost()

    url = urllib.quote_plus(url)
    url = 'http://%s:%d/vfs/%s' % (addr, port, url)
    
    utils.Log('Playback URL %s' % url)
    
    APPLICATION.setResolvedUrl(url, success=True, listItem=liz, windowed=windowed)


def DoMainList():
    menu = []
    menu.append((GETTEXT(30020), '?mode=%d' % SETTINGS))

    list = GetListItems('plugin://plugin.video.thelivebox/?mode=')
    for item in list:
        AddDir(item[1], item[2], url=item[3], isFolder=item[6], desc=item[8], contextMenu=menu, replaceItems=True)

    return len(list) > 0


def MainList():
    if DoMainList():
        return

    xbmc.sleep(5000)
    
    if DoMainList():
        return

    utils.DialogOK(GETTEXT(30043), GETTEXT(30044))

    APPLICATION.addonSettings()

    if DoMainList():
        return

    utils.DialogOK(GETTEXT(30043), GETTEXT(30052))

    utils.setSetting('FALLBACK', 'true')
    if DoMainList():
        return
   
    #name = '[I]%s[/I]' % GETTEXT(30043)
    #desc = '%s %s' % (GETTEXT(30043), GETTEXT(30044))
    #mode = 300
    #AddDir(name, mode, url=None, image=None, fanart=FANART, isFolder=False, isPlayable=False, desc=desc)


def GenericList(mode):
    menu = []
    menu.append((GETTEXT(30020), '?mode=%d' % SETTINGS))

    list = GetListItems('plugin://plugin.video.thelivebox/?mode=%d' % mode)
    for item in list:
        AddDir(item[1], item[2], url=item[3], isFolder=item[6], desc=item[8], contextMenu=menu, replaceItems=True)        


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


def GetRepeatMode():
    repeatMode = 'RepeatOff'
    if not utils.DialogYesNo(GETTEXT(30008), GETTEXT(30009), GETTEXT(30010), GETTEXT(30011), GETTEXT(30012)):
         repeatMode = 'RepeatAll'

    return repeatMode


def GetVimeoVideos():
    videos = []

    list = GetListItems('plugin://plugin.video.thelivebox/?mode=%d' % EXAM)
    for item in list: #title, id, image, desc
        videos.append([item[1], item[3], item[4], item[8]])

    return videos


def AddDir(name, mode, url=None, image=None, fanart=None, isFolder=False, isPlayable=False, desc='', contextMenu=None, replaceItems=False, infoLabels=None):
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

    if mode == VIDEO_ADDON or mode == VIDEO_LOCAL:
        try:    
            try:    url   = urllib.unquote_plus(params['url'])
            except: url = ''

            try:    title = urllib.unquote_plus(params['title'])
            except: title = ''

            try:    image = urllib.unquote_plus(params['image'])
            except: image = ''
            
            PlayVideo(mode, url, title, image)

        except Exception, e:
            utils.Log('Error in VIDEO mode - %s' % str(e))


    elif mode == CLEARCACHE:
        import cache
        cache.clearCache()


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

    else:
        MainList()

    if utils.getSetting('FALLBACK').lower() == 'true':
        mode = GETTEXT(30053)
    elif utils.getSetting('HOST_MODE') == '0':
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