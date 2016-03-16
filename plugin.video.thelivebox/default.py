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


import urllib
import urllib2
import random
import re
import os

import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui

#try:    
#    from hashlib import md5
#    MD5 = md5
#except: 
#    import md5
#    MD5 = md5.new


import sys
addon = xbmcaddon.Addon(id = 'script.video.thelivebox')
path  = addon.getAddonInfo('path')
sys.path.insert(0, path)
import utils
import sfile
import s3


ADDON   = utils.ADDON
HOME    = utils.HOME
ICON    = utils.ICON
FANART  = utils.FANART
PROFILE = utils.PROFILE


#Modes
VIDEO_ADDON     = utils.VIDEO_ADDON
SERVER_FILE     = utils.SERVER_FILE
SETTINGS        = utils.SETTINGS
CLEARCACHE      = utils.CLEARCACHE
WAITING         = utils.WAITING
EXAM            = utils.EXAM
DEMO            = utils.DEMO
SERVER_FOLDER   = utils.SERVER_FOLDER
LOCAL_FOLDER    = utils.LOCAL_FOLDER
AMAZON_FILE     = utils.AMAZON_FILE
AMAZON_FOLDER   = utils.AMAZON_FOLDER
UPDATE_FILE_CHK = utils.UPDATE_FILE_CHK
UPDATE_FILE     = utils.UPDATE_FILE
LOCAL_FILE      = utils.LOCAL_FILE

SERVER           = utils.SERVER
LBVERSION        = utils.LBVERSION
ADDRESS          = utils.ADDRESS
RETRIEVE_URL     = utils.RETRIEVE_URL

# Settings
SHOW_CONFIGURE = utils.SHOW_CONFIGURE
SHOW_REFRESH   = utils.SHOW_REFRESH
SHOW_DOWNLOAD  = utils.SHOW_DOWNLOAD
SHOW_VIMEO     = utils.SHOW_VIMEO
SHOW_AMAZON    = utils.SHOW_AMAZON
SHOW_LOCAL     = utils.SHOW_LOCAL
SHOW_HIDDEN    = utils.SHOW_HIDDEN


DELIMETER = utils.DELIMETER

DSC = utils.DSC
SRC = utils.SRC

GETTEXT = utils.GETTEXT
URL     = 'https://vimeo.com/channels/%s/videos/rss'



def NoPlay(reason):
    utils.Log(reason)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())


def PlayAddonVideo(url, title='', image=''):
    if len(url) == 0:
        return NoPlay('Empty URL passed into PlayVideo')

    img   = image
    if len(img) == 0:
        img = ICON

    label = title
    if len(label) == 0:
        label = GETTEXT(30000)

    pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    pl.clear()  

    liz = xbmcgui.ListItem(label, iconImage=img, thumbnailImage=img)

    liz.setInfo(type='Video', infoLabels={'Title': label})

    pl.add(url, liz)

    repeatMode = GetRepeatMode()

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

    xbmc.executebuiltin('PlayerControl(%s)' % repeatMode)


def getGlobalMenu():
    menu = []
    menu.append((GETTEXT(30020), '?mode=%d' % SETTINGS))
    return menu
    

def MainList(client):    
    hasClient = len(client) > 0

    menu = getGlobalMenu()

    if SHOW_CONFIGURE:
        AddDir( 0, '[I]%s[/I]' % GETTEXT(30020), SETTINGS,        isFolder=False, isPlayable=False, desc=GETTEXT(30021), contextMenu=menu)

    if SHOW_REFRESH:
        AddDir(10, '[I]%s[/I]' % GETTEXT(30007), CLEARCACHE,      isFolder=False, isPlayable=False, desc=GETTEXT(30018), contextMenu=menu)

    if hasClient:
        if SHOW_DOWNLOAD:
            AddDir(20, '[I]%s[/I]' % GETTEXT(30075), UPDATE_FILE_CHK, isFolder=True,  isPlayable=False, desc=GETTEXT(30076), contextMenu=menu)

        if SHOW_VIMEO:
            AddDir(30, GETTEXT(30026),               WAITING,         isFolder=False, isPlayable=True,  desc=GETTEXT(30028), contextMenu=menu)
            AddDir(40, GETTEXT(30027),               EXAM,            isFolder=True,  isPlayable=False, desc=GETTEXT(30029), contextMenu=menu)

    if hasClient and SHOW_AMAZON:
        try:    AddAmazonItems(50, '', menu)
        except: pass

    if SHOW_LOCAL:
        AddFolderItems(100, '', menu)

    if utils.getSetting('DEMO') == 'true':
        AddDir(999, 'Demo',  DEMO, isFolder=True, isPlayable=False, desc='Demo', contextMenu=menu)


def AddAmazonItems(index, folder, menu):
    browseFolder = utils.GETTEXT(30055)
    playVideo    = utils.GETTEXT(30056)

    fileImg   = 'DefaultMovies.png'
    folderImg = 'DefaultFolder.png'

    if len(folder) == 0:
        AddDir(index, utils.GETTEXT(30059), AMAZON_FOLDER, url=utils.GetClient(), image=folderImg, isFolder=True, isPlayable=False, desc=browseFolder, contextMenu=menu)
        return

    if not folder.endswith(DELIMETER):
        folder += DELIMETER

    folders, files = s3.getFolder(folder)

    ignore = folder + '_'

    for fold in folders:        
        try:
            if fold.startswith(ignore):
                continue

            if not utils.isAmazonPlayable(fold):
                continue

            plot = utils.getAmazonContent(fold, DSC)

            label = fold.replace(folder, '', 1).replace('_', ' ')
            AddDir(index, label, AMAZON_FOLDER, url=fold, image=folderImg, isFolder=True,  isPlayable=False, desc=browseFolder, plot=plot, contextMenu=menu)
            index += 1
        except:
            pass


    for _file in files:
        try:
            file = _file[0].encode('utf-8')
            size = _file[1]

            if not utils.isFilePlayable(file):
                continue

            plot = utils.getAmazonContent(file, DSC)

            label = (file.replace(folder, '', 1).replace('_', ' ').rsplit('.', 1)[0])
            AddDir(index, label, AMAZON_FILE, url=file, image=fileImg, isFolder=False, isPlayable=True, desc=playVideo, plot=plot, contextMenu=menu)
            index += 1
        except Exception, e:
            pass


def AddFolderItems(index, folder, menu):
    ignore = ['_', '.']
    if SHOW_HIDDEN:
        ignore = []
    
    items = utils.parseFolder(folder, GETTEXT(30057), ignore=ignore)
    if len(items) == 0:
        return

    browseFolder = utils.GETTEXT(30055)
    playVideo    = utils.GETTEXT(30056)

    file   = 'DefaultMovies.png'
    folder = 'DefaultFolder.png'

    for item in items:
        label      = item[0]
        url        = item[1]
        isPlayable = item[2]

        if isPlayable:
            AddDir(index, label, SERVER_FILE,   url=url, image=file,   isFolder=False, isPlayable=True, desc=playVideo,    contextMenu=menu)
        else:
            AddDir(index, label, SERVER_FOLDER, url=url, image=folder, isFolder=True, isPlayable=False, desc=browseFolder, contextMenu=menu)
            
        index += 1


def DemoList():
    root = xbmc.translatePath(os.path.join(utils.HOME, 'resources', 'video'))
    #root = root.replace('storage/emulated/0', 'sdcard')
   
    AddDir(1, 'Demo Livebox Video', SERVER_FILE, url=os.path.join(root, 'livebox_id_2015.m4v'),isFolder=False, isPlayable=True, desc='Play local video')  

    AddDir(100, 'version',   LBVERSION, isFolder=True,  isPlayable=False, desc='Indicate if this instance is a Livebox server')
    AddDir(101, 'server',    SERVER,    isFolder=True,  isPlayable=False, desc='Indicate version number of Livebox server')
    AddDir(102, 'address',   ADDRESS,   isFolder=True,  isPlayable=False, desc='Indicate address of this Livebox server')


def WaitingRoom(client):    
    html   = utils.GetHTML(URL % client)
    videos = GetVimeoVideos(html)
    
    pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    pl.clear()  

    isFirst = True

    repeatMode = GetRepeatMode()

    for video in videos:
        title  = video[0]
        link   = video[1]
        image  = video[2]

        if len(image) == 0:
            image = ICON

        if len(title) == 0:
            title = GETTEXT(30000)

        liz = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)

        liz.setInfo(type='Video', infoLabels={'Title': title})

        pl.add(link, liz)

        if isFirst:
            isFirst  = False     
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)            

    xbmc.executebuiltin('PlayerControl(%s)' % repeatMode)
    
    
def ExaminationRoom(client):
    html   = utils.GetHTML(URL % client)
    videos = GetVimeoVideos(html)
   
    menu = []
    menu.append((GETTEXT(30020), '?mode=%d' % SETTINGS))

    index = 0

    desc = GETTEXT(30056)

    for video in videos:
        image  = video[2]
        fanart = image.replace('_200x150.jpg', '_1200x800.jpg')
        AddDir(index, video[0], VIDEO_ADDON, video[1], image, fanart, isFolder=False, isPlayable=True, desc=desc, plot=video[3], contextMenu=menu) 
        index += 1


def CheckForVideoUpdates(client):
    amzUpdate = ''

    if len(client) > 0:
        amzUpdate = client + DELIMETER
    
    amzUpdate += '_update' + DELIMETER
    extDrive   = utils.getExternalDrive()
    files      = utils.getAllPlayableFiles(extDrive)
    updates    = s3.getAllFiles(amzUpdate)

    index = 0

    menu = []
    menu.append((GETTEXT(30020), '?mode=%d' % SETTINGS))

    for key in updates.keys():
        suffix = GETTEXT(30083)
        toAdd  = True
        update = updates[key]

        key = key.replace(amzUpdate, extDrive, 1).replace(DELIMETER, os.sep)
       
        if key in files:
            #check if update is different size
           
            current = files[key]

            newSize  = update[1]
            currSize = current[1]            

            if newSize == currSize:
                toAdd = False

            src = update[0]
            dst = current[0]

        else:
            suffix = GETTEXT(30084)
            toAdd  = True
            src    = update[0]
            dst    = src.replace(amzUpdate, extDrive, 1)
            
        if toAdd and utils.isFilePlayable(dst):
            index += 1

            plot = utils.getAmazonContent(src, DSC)

            name = key.rsplit(os.sep)[-1].rsplit('.', 1)[0].replace('_', ' ')
            src  = urllib.quote_plus(src)
            dst  = urllib.quote_plus(dst)
            
            url  = 'name=%s&src=%s&dst=%s' % (urllib.quote_plus(name), src, dst)

            AddDir(index, name+suffix, UPDATE_FILE, url=url, image='DefaultMovies.png', desc=GETTEXT(30077), plot=plot, contextMenu=None)

    if index == 0:
        if xbmcgui.Window(10000).getProperty('LB_AUTOPLAY').lower() <> 'true':
            utils.DialogOK(GETTEXT(30078))

    xbmcgui.Window(10000).setProperty('LB_AUTOPLAY', 'False')

        
def GetRepeatMode():
    repeatMode = 'RepeatOff'
    if not utils.DialogYesNo(GETTEXT(30008), GETTEXT(30009), GETTEXT(30010), GETTEXT(30011), GETTEXT(30012)):
         repeatMode = 'RepeatAll'

    return repeatMode


def GetVimeoVideos(html):
    vimeo   = utils.GetVimeoVersion()
    version = int(vimeo.split('.')[0])

    if version == 0:
        utils.DialogOK('Vimeo not installed')
        utils.Log('Vimeo not installed')
        return []

    utils.Log('Vimeo version %s detected' % str(vimeo))

    if version == 3:
        url = 'plugin://plugin.video.vimeo/?action=play_video&videoid=%s'
    elif version == 4:
        url = 'plugin://plugin.video.vimeo/play/?video_id=%s'
    else:
        return NoPlay('Unknown version of Vimeo installed')

    items = html.split('<item>')[1:]

    videos = []

    for item in items:
        try:
            match = re.compile('<title>(.+?)</title>.+?<link>(.+?)</link>.+?<media:thumbnail(.+?)"/>').findall(item)[0]
            title = match[0]
            id    = match[1].rsplit('/', 1)[-1]
            link  = url % id
            img   = match[2].split('url="', 1)[-1]

            try:    desc = re.compile('class=&quot;first&quot;&gt;(.+?)&lt;').findall(item)[0]
            except: desc = ''

            if desc == '&lt;/p&gt;':
                desc = ''
                      
            videos.append([title, link, img, desc])

        except:
            pass

    videos.sort()
    return videos


def AddDir(index, name, mode, url=None, image=None, fanart=None, isFolder=False, isPlayable=False, desc='', plot='', infoLabels={}, contextMenu=None):
    if not fanart:
        fanart = FANART

    image = utils.patchImage(mode, image, url, infoLabels)   

    u  = sys.argv[0] 
    u += '?mode='  + str(mode)
    u += '&title=' + urllib.quote_plus(name)

    if image:
        u += '&image=' + urllib.quote_plus(image)

    if url:
        u += '&url=' + urllib.quote_plus(url)

    if desc:
        u += '&desc' + urllib.quote_plus(desc)

    if plot:
        u += '&plot' + urllib.quote_plus(plot)

    liz = xbmcgui.ListItem(name, iconImage=image, thumbnailImage=image)

    if contextMenu:
        liz.addContextMenuItems(contextMenu, replaceItems=True)

    if infoLabels:
        liz.setInfo(type='Video', infoLabels=infoLabels)

    if isPlayable:
        liz.setProperty('IsPlayable', 'true')

    liz.setProperty('Fanart_Image', fanart)  

    info  = ''
    info += '&index='      + str(index)
    info += '&name='       + urllib.quote_plus(name)
    info += '&mode='       + str(mode)
    info += '&image='      + (urllib.quote_plus(image)  if image  else '')
    info += '&fanart='     + (urllib.quote_plus(fanart) if fanart else '')
    info += '&desc='       + (urllib.quote_plus(desc)   if desc   else '')
    info += '&plot='       + (urllib.quote_plus(plot)   if plot   else '')
    info += '&isFolder='   + str(isFolder)
    info += '&url='        + (urllib.quote_plus(url) if url        else '')
    info += '&isPlayable=' + (str(isPlayable)        if isPlayable else 'False')

    u += '&info=' + urllib.quote_plus(info)

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder)


def Address():
    import inspect
    script = inspect.getfile(inspect.currentframe())
    home = script.split('addons', 1)[0] #gives the equivalent of 'special://home/'
    AddDir(0, home, 0)



def Version():
    AddDir(0, utils.VERSION, 0)


def Server():
    isServer = utils.getSetting('HOST_MODE') == '0'

    if isServer:
        AddDir(1, 'server', 0)
    else:
        AddDir(1, 'client', 0)


def RetrieveURL(url, type, isServer):
    if len(url) == 0:
        return

    if type == VIDEO_ADDON:
        AddDir(1, url, 0)

    root = utils.getDownloadLocation()

    if type == SERVER_FILE:
        dst = urllib.quote_plus(url)
        dst = os.path.join(root, dst)

        if not sfile.exists(dst):
            try:    sfile.copy(url, dst)
            except: pass
        AddDir(1, dst, 0)

    if type == AMAZON_FILE:
        src = url.lower().endswith('.txt') or url.lower().endswith('.%s' % SRC)
        url = urllib.quote_plus(url)
        dst = os.path.join(root, url)

        import download
        url = s3.getURL(url)
        url = s3.convertToCloud(url)
        utils.Log('Amazon URL : %s' % url)        

        if src:
            url = utils.GetHTML(url, maxAge=7*86400)
            url = urllib.quote_plus(url)
            dst = os.path.join(root, url)
            url = s3.getURL(url)
            url = s3.convertToCloud(url)                
            utils.Log('Real Amazon URL : %s' % url) 
            
        downloading = sfile.exists(dst+'.part')

        if downloading:
            if False:#isServer:
                AddDir(1, dst, 0)
            else:
                AddDir(1, url, 0)

            return

        if sfile.exists(dst):
            AddDir(1, dst, 0)
            return

        download.download(url, dst)

        #if isServer:
        #    while sfile.size(dst) == 0:
        #        xbmc.sleep(100)
        #    AddDir(1, dst, 0)
        #    return

        AddDir(1, url, 0)

def PlayFromScript(url, title, image, mode, window):
    downloadAndPlay = True

    extDrive = utils.getExternalDrive()
    amzUrl   = url.replace(extDrive, '') 
      
    if amzUrl.startswith('AMAZON@'):
        src = amzUrl.replace('AMAZON@', '', 1)
        dst = src.lstrip(utils.GetClient()).lstrip(os.sep).lstrip(DELIMETER)

        if dst.startswith('_update'):
            dst = dst.lstrip('_update').lstrip(os.sep).lstrip(DELIMETER)

        dst = os.path.join(extDrive, dst)
        url = dst

        if sfile.exists(dst):
            downloaded = 0
        else:
            if downloadAndPlay:
                downloaded  = 0 #success
                downloadURL = url
                #give playback a 5 second head start before download
                #utils.DoThreadedDownload(title, downloadURL, src)
                url = urllib.quote_plus(src)
                url = s3.getURL(url)
                url = s3.convertToCloud(url)
            else:
                try:    downloaded = utils.DoDownload(title, dst, src, progressClose=False)
                except: downloaded = 1

        if downloaded > 0: #not successful
            if downloaded == 1:#failed NOT cancelled, cancelled doesn't need to inform user
                utils.DialogOK(title, utils.GETTEXT(30081))
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())
            return

    liz = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)

    liz.setInfo(type='Video', infoLabels={'Title':title} )
    liz.setPath(url)

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

    if downloadAndPlay:
        xbmc.sleep(5*1000)
        utils.DoThreadedDownload(title, downloadURL, src)
   


def getParams(url):
    params = {}
    url    = url.split('?', 1)[-1]
    pairs  = url.split('&')

    for pair in pairs:
        split = pair.split('=')
        if len(split) > 1:
            params[split[0]] = split[1]
  
    for key in params:
        utils.Log('%s\t: %s' % (key, params[key]))

    return params


def main():
    client = utils.GetClient()
    params = getParams(sys.argv[2])
    mode   = None

    try:    mode = int(urllib.unquote_plus(params['mode']))
    except: pass

    if mode == VIDEO_ADDON or mode == SERVER_FILE or mode == AMAZON_FILE:
        isAmazon = (mode == AMAZON_FILE)
        try:    
            try:    url   = urllib.unquote_plus(params['url'])
            except: url = ''

            try:    title = urllib.unquote_plus(params['title'])
            except: title = ''

            try:    image = urllib.unquote_plus(params['image'])
            except: image = ''

            if isAmazon:
                url = s3.getURL(url)
                url = url.replace('thelivebox.s3.amazonaws.com', 'd2blgl3q9xzi92.cloudfront.net')
                utils.Log('Amazon URL : %s' % url)
                           
            PlayAddonVideo(url, title, image)

        except Exception, e:
            utils.Log('Error in VIDEO mode - %s' % str(e))


    elif mode == CLEARCACHE:
        utils.ClearCache()
        #doRefesh = True


    elif mode == SETTINGS:
        ADDON.openSettings()
        
        
    elif mode == WAITING:
        WaitingRoom(client)


    elif mode == SERVER:
        Server()


    elif mode == LBVERSION:
        Version()


    elif mode == RETRIEVE_URL:
        try:    url   = urllib.unquote_plus(params['url'])
        except: url = ''

        try:    type = int(urllib.unquote_plus(params['type']))
        except: type = 0

        try:    isServer = urllib.unquote_plus(params['server']).lower() == 'true'
        except: isServer = False


        RetrieveURL(url, type, isServer)


    elif mode == ADDRESS:
        Address()


    elif mode == EXAM:
        ExaminationRoom(client)


    elif mode == DEMO:
        DemoList()


    elif mode == SERVER_FOLDER:
        try:    url   = urllib.unquote_plus(params['url'])
        except: url = ''

        AddFolderItems(0, url, getGlobalMenu())


    elif mode == AMAZON_FOLDER:
        try:    url   = urllib.unquote_plus(params['url'])
        except: url = ''

        AddAmazonItems(0, url, getGlobalMenu())


    elif mode == UPDATE_FILE_CHK:
        CheckForVideoUpdates(client)


    elif mode > 10000:
        try:    url   = urllib.unquote_plus(params['url'])
        except: url = ''

        try:    title = urllib.unquote_plus(params['title'])
        except: title = ''

        try:    image = urllib.unquote_plus(params['image'])
        except: image = ''

        try:    window = urllib.unquote_plus(params['window']).lower() == 'true'
        except: window = False

        PlayFromScript(url,  title, image, mode-10000, window)        

    else:           
        MainList(client)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if __name__ == '__main__': 
    try:    main()
    except: pass