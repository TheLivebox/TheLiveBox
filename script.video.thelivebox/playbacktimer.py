
#       Copyright (C) 2015-
#       Sean Poyser (seanpoyser@gmail.com)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Progr`am is distributed in the hope that it will be useful,
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
import os
import utils

GETTEXT = utils.GETTEXT
NAME    = 'Livebox Playback Timer'


def main():
    utils.Log('Playback Timer Stopped')

    if not xbmc.Player().isPlaying():    
        utils.Log('No video playing in playback timer')
        return

    if xbmc.getCondVisibility('player.paused') <> 1:
        utils.Log('Pausing video in playback timer')
        xbmc.Player().pause()

    try:
        limit = utils.getSetting('PLAYBACK_LIMIT')
        limit = GETTEXT(35101+int(limit))
    except:
        limit = '4 hours'

    if utils.DialogYesNo(GETTEXT(30106) % limit, GETTEXT(30107), GETTEXT(30108), noLabel=GETTEXT(30109), yesLabel=GETTEXT(30110)):
        xbmc.Player().pause()
        start()
        return

    xbmc.Player().stop()


def cancel():
    xbmcgui.Window(10000).clearProperty('LB_ALARM_ACTIVE')
    xbmc.executebuiltin('CancelAlarm(%s,True)' % NAME)


def isActive():
    return xbmcgui.Window(10000).getProperty('LB_ALARM_ACTIVE').lower() == 'true'


def restart():
    cancel()
    start()


def start():
    if isActive():
        return

    cancel()

    if utils.getSetting('PLAYBACK_LIMIT_MODE') <> '1': #i.e. not time-limit
        return

    xbmcgui.Window(10000).setProperty('LB_ALARM_ACTIVE', 'true')

    limits = [4, 8, 12, 14]
    try:    limit = int(getSetting('PLAYBACK_LIMIT'))
    except: limit = 0

    limit = limits[limit]
    limit = limit * 60 #convert to hours

    import inspect
    script =  inspect.getfile(inspect.currentframe())    #os.path.join(utils.HOME, 'playbacktimer.py')
    cmd    = 'AlarmClock(%s,RunScript(%s),%d,silent)' % (NAME, script, limit)
 
    utils.Log('Playback Timer Started: %s' % str(limit))
    utils.Log(cmd)

    xbmc.executebuiltin(cmd)

        

if __name__ == '__main__':
    cancel()

    try:
        main()
    except Exception, e:
        utils.Log('Error in playbacktimer.py %s' % str(e))