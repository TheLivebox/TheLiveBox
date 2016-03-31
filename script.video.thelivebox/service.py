
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

import xbmc
import xbmcaddon
import xbmcgui
import network

import utils

#if not utils.verifySource():
#    utils.systemUpdated(utils.GETTEXT(30060), utils.GETTEXT(30061))
#    exit()

utils.disableKodiVersionCheck()

utils.updateAdvancedSettings('<loglevel hide="false">-1</loglevel>')
utils.setKodiSetting('debug.showloginfo',  False) 
utils.setKodiSetting('debug.extralogging', False) 

xbmcaddon.Addon('plugin.video.vimeo').setSetting('kodion.setup_wizard', 'false')

utils.enableWebserver()
utils.removePartFiles()

#scanner = network.Scanner()
#scanner.start()
#started = True

import checkUpdates
checkUpdates.checkRepo()

utils.checkVersion()


if utils.BOOTVIDEO:
    utils.SetFanart()
    utils.SetShortcut()

    import os

    path  = os.path.join(utils.HOME, 'resources', 'video', 'livebox_id_2015.m4v')
    title = utils.TITLE
    
    liz = xbmcgui.ListItem(title, iconImage=utils.ICON, thumbnailImage=utils.ICON)

    liz.setInfo(type='Video', infoLabels={'Title': title})

    xbmc.Player().play(path, liz)

    while not xbmc.Player().isPlayingVideo():
        xbmc.sleep(100)

    while xbmc.Player().isPlayingVideo():
        xbmc.sleep(100)

    cmd = 'RunAddon(%s)' % utils.ADDONID
    xbmc.executebuiltin(cmd)


#------------------------------------------------------------------------

class MyMonitor(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)

        self.settings = {}
        self.settings['SKIN']           = ''
        self.settings['CLIENT']         = ''
        self.settings['EXT_DRIVE']      = ''
        self.settings['SHOW_CONFIGURE'] = ''
        self.settings['SHOW_REFRESH']   = ''
        self.settings['SHOW_DOWNLOAD']  = ''
        self.settings['SHOW_VIMEO']     = ''
        self.settings['SHOW_AMAZON']    = ''
        self.settings['SHOW_LOCAL']     = ''
        self.settings['SHOW_HIDDEN']    = ''

        self.PLAYBACK_LIMIT_MODE = utils.getSetting('PLAYBACK_LIMIT_MODE')
        self.PLAYBACK_START      = utils.getSetting('PLAYBACK_START')
        self.PLAYBACK_END        = utils.getSetting('PLAYBACK_END')

        self._onSettingsChanged(init=True)


    def onSettingsChanged(self):
        self._onSettingsChanged()


    def _onSettingsChanged(self, init=False):
        relaunch = False

        for key in self.settings:
            value = utils.getSetting(key)
            if value <> self.settings[key]:
                relaunch           = True
                self.settings[key] = value

        if init:
            return

        self.checkLimitMode()

        if relaunch:
            utils.Log('Settings changed - relaunching')
            self.relaunch()

    def relaunch(self):
        xbmcgui.Window(10000).setProperty('LB_RELAUNCH', 'true')


    def checkLimitMode(self):
        newMode = utils.getSetting('PLAYBACK_LIMIT_MODE')

        NONE  = '0'
        LIMIT = '1'
        FRAME = '2'

        if newMode == LIMIT and self.PLAYBACK_LIMIT_MODE == LIMIT:
            return

        import playbackTimer

        playbackTimer.cancel()
        self.PLAYBACK_LIMIT_MODE = newMode


        if self.PLAYBACK_LIMIT_MODE == LIMIT:
           playbackTimer.start()


        if self.PLAYBACK_LIMIT_MODE == FRAME:
            start = utils.getSetting('PLAYBACK_START')
            end   = utils.getSetting('PLAYBACK_END')

            if self.PLAYBACK_START <> start:
                xbmcgui.Window(10000).setProperty('LB_RESET_START', 'true')
                self.PLAYBACK_START = start

            if self.PLAYBACK_END <> end:
                xbmcgui.Window(10000).setProperty('LB_RESET_END', 'true')
                self.PLAYBACK_END = end

        
#------------------------------------------------------------------------


def showLiveboxes():
    boxes = network.getLiveboxes()
    utils.Log('%d Liveboxes detected:' % len(boxes))
    for box in boxes:
        utils.Log(box)


monitor = MyMonitor()


while (not xbmc.abortRequested):
    xbmc.sleep(1000) 
    #if not started:
    #    scanner = network.Scanner()
    #    scanner.start()
    #    started = True

    #if len(xbmcgui.Window(10000).getProperty('LB_RESTART_SCAN')) > 0:
    #    xbmcgui.Window(10000).clearProperty('LB_RESTART_SCAN')
    #    scanner.stop()
    #    started = False
  

del monitor

xbmcgui.Window(10000).setProperty('LB_XBMC_ABORTED', 'true')

#scanner.stop()
