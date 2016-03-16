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

#thumb="androidapp://sources/apps/com.android.vending.png


def launchAndroid(app):
    import utils
    utils.Log('Launching Android App : %s' % app)

    import xbmc
    cmd = 'StartAndroidActivity("%s")' % app
    xbmc.executebuiltin(cmd)

   
if __name__ == '__main__':
    app = None
    if len(sys.argv) == 1:
        # open selection box to chooose from
        app = None
    else:
        app = sys.argv[1]

    if app:
        launchAndroid(app)
