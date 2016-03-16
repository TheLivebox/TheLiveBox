'''
    Copyright (C) 2015 Sean Poyser (seanpoyser@gmail.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import xbmc
import utils


def main():
    utils.Log('Launching support')

    #cmd = 'StartAndroidActivity("com.teamviewer.quicksupport.market")' #TeamViewer
    #cmd = 'StartAndroidActivity("com.android.settings")' #Settings
    #cmd = 'StartAndroidActivity("com.mbx.settingsmbox")' #MBox settings
    cmd = 'StartAndroidActivity("com.android.vending")' #Play Sstore <favourite name="Google Play Store" thumb="androidapp://sources/apps/com.android.vending.png">StartAndroidActivity(&quot;com.android.vending&quot;)</favourite>
    xbmc.executebuiltin(cmd)

if __name__ == '__main__': 
    main()
