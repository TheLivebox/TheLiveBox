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


def launchAndroid(app, intent, dataType, dataURI):
    import utils
    utils.Log('Launching Android App : %s' % app)

    import xbmc
    cmd = 'StartAndroidActivity("%s", "%s", "%s", "%s")' % (app, intent, dataType, dataURI)

    utils.Log(cmd)

    xbmc.executebuiltin(cmd)

   
if __name__ == '__main__':
    app      = None
    intent   = ''
    dataType = ''
    dataURI  = ''

    if len(sys.argv) == 1:
        # open selection box to chooose from
        app = None
    else:
        try:
            app      = sys.argv[1]
            intent   = sys.argv[2]
            dataType = sys.argv[3]
            dataURI  = sys.argv[4]
        except:
            pass

    if app:
        launchAndroid(app, intent, dataType, dataURI)
