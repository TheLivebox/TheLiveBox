
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
import xbmcgui
import network

started = False

import utils


utils.enableWebserver()


if utils.BOOTVIDEO:    
    utils.SetFanart()

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


def showLiveboxes():
    boxes = network.getLiveboxes()
    utils.Log('%d Liveboxes detected:' % len(boxes))
    for box in boxes:
        utils.Log(box)



while (not xbmc.abortRequested):
    xbmc.sleep(1000) 
    if not started:
        scanner = network.Scanner()
        scanner.start()
        started = True

    if len(xbmcgui.Window(10000).getProperty('LB_RESTART_SCAN')) > 0:
        xbmcgui.Window(10000).clearProperty('LB_RESTART_SCAN')
        scanner.stop()
        started = False


scanner.stop()