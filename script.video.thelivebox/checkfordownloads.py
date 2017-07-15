#
#       Copyright (C) 2016-
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

import os
import urllib

import utils
import sfile
import s3



GETTEXT   = utils.GETTEXT
DELIMETER = utils.DELIMETER

DSC = utils.DSC
SRC = utils.SRC


def verifyExtDrive():
    extDrive = utils.getExternalDrive()
    return sfile.exists(extDrive)


def download(name, dst, src):
    url = urllib.quote_plus(src) 
    url = s3.getURL(url)
    url = s3.convertToCloud(url)

    utils.Log('Amazon name : %s' % name)        
    utils.Log('Amazon dst :  %s' % dst)        
    utils.Log('Amazon src :  %s' % src)
    utils.Log('Amazon URL :  %s' % url)        
        
    utils.DoThreadedDownload(name, dst, src, postDownload=postDownload)


def restart(when):
    import xbmc
    import inspect

    script = inspect.getfile(inspect.currentframe())
    name   = 'checkForDownloads'
    cmd    = 'AlarmClock(%s,RunScript(%s),%d,True)' % (name, script, when)
    xbmc.executebuiltin('CancelAlarm(%s,True)' % name)  
    xbmc.executebuiltin(cmd)


def postDownload(success):
    if not success:
        return

    import xbmcgui
    xbmcgui.Window(10000).setProperty('LB_CHECK_FOR_UPDATED_FILES', 'true')

    check()
   

def check():
    if not verifyExtDrive():
        return

    amzUpdate = ''
    client    = utils.GetClient()

    if len(client) > 0:
        amzUpdate = client + DELIMETER
    
    amzUpdate += '_update' + DELIMETER
    extDrive   = utils.getExternalDrive()
    files      = utils.getAllPlayableFiles(extDrive)
    updates    = s3.getAllFiles(amzUpdate)

    #index = 0

    for key in updates.keys():
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
            toAdd  = True
            src    = update[0]
            dst    = src.replace(amzUpdate, extDrive, 1)
            
        if toAdd and utils.isFilePlayable(dst):
            name = key.rsplit(os.sep)[-1].rsplit('.', 1)[0].replace('_', ' ')  
            #only download one at a time to spare bandwidth 
            return download(name, dst, src)

    #if we ge here then restart script in 30 minutes
    restart(30)
 

    
def main():
    check()


if __name__ == '__main__':
    try:
        main()
    except:
        pass