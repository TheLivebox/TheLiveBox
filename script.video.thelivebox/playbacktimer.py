
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
import utils

GETTEXT = utils.GETTEXT


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
        utils.initialisePlaybackTimer()
        return

    xbmc.Player().stop()
        

if __name__ == '__main__':
    xbmcgui.Window(10000).clearProperty('LB_ALARM_ACTIVE')

    try:
        main()
    except Exception, e:
        utils.Log('Error in playbacktimer.py %s' % str(e))