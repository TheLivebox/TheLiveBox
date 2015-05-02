
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

import utils


def ping(hostname):
    import platform

    if platform.system() == 'Windows':
        import subprocess
        cmd   = 'ping %s -n 1 -l 1 -w 1' % hostname
        shell = False

        si              = subprocess.STARTUPINFO
        si.dwFlags     |= subprocess._subprocess.STARTF_USESHOWWINDOW

        si.wShowWindow  = subprocess._subprocess.SW_HIDE

        ping     = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, startupinfo=si)
        response = ping.stdout.read()

        return 'Received = 1' in response

    import os
    cmd   = 'ping -c1 -w1 -l1 %s' % hostname
    return os.system(cmd) == 0


def getHost():
    net = xbmc.getInfoLabel('Network.IPAddress')
    return net


def ipScan():
    nItem = float(255)

    xbmc.executebuiltin('Dialog.Close(all, true)')
    xbmc.sleep(1000)

    dp = xbmcgui.DialogProgress()
    dp.create('Network Scan')
    dp.update(0)

    utils.Log('Starting IP Scan')

    for i in range(0, int(nItem+1)):
        ip = '192.168.1.%d' % i

        percent  = int(i / nItem*100)
        dp.update(percent, 'Scanning %s' % ip)

        if ping(ip):
            utils.Log('%s is in network' % ip)

        if dp.iscanceled():
            break

    utils.Log('Ending IP Scan')


def setLivebox(name, addr, port):
    nBoxes = getNmrLiveBoxes()
    index = getIndex(name, addr)
    if index < 0:
        index   = nBoxes
        nBoxes += 1

    xbmcgui.Window(10000).setProperty('LB_NMR_LIVEBOX', str(nBoxes))
    xbmcgui.Window(10000).setProperty('LB_LIVEBOX_NAME_%d' % index, name)
    xbmcgui.Window(10000).setProperty('LB_LIVEBOX_ADDR_%d' % index, addr)
    xbmcgui.Window(10000).setProperty('LB_LIVEBOX_PORT_%d' % index, str(port))


def getIndex(_name, _addr):
    nBoxes = getNmrLiveBoxes()
    for i in range(0, nBoxes):
        name, addr, port = getLivebox(i)
        if name != _name: continue
        if addr != _addr: continue
        return i

    return -1


def getLivebox(index):
    name = xbmcgui.Window(10000).getProperty('LB_LIVEBOX_NAME_%d' % index)
    addr = xbmcgui.Window(10000).getProperty('LB_LIVEBOX_ADDR_%d' % index)
    port = int(xbmcgui.Window(10000).getProperty('LB_LIVEBOX_PORT_%d' % index))

    return name, addr, port


def getLocalHost():
    localIP = xbmc.getInfoLabel('Network.IPAddress')
    nBoxes  = getNmrLiveBoxes()
    for i in range(0, nBoxes):
        name, addr, port = getLivebox(i)
        if addr == localIP:
            return addr, port

    return 'locallhost', 8080


def getAutoServer():
    boxes = getLiveboxes()
    for box in boxes:
        if isServer(box[1], box[2]):
            return box
    return None


def getNmrLiveBoxes():
    try:    return int(xbmcgui.Window(10000).getProperty('LB_NMR_LIVEBOX'))
    except: return 0


def getLiveboxes():
    boxes = []
    nBoxes = getNmrLiveBoxes()
    for i in range(0, nBoxes):
        name, addr, port = getLivebox(i)
        boxes.append([name, addr, port])

    return boxes


def isServer(addr, port):
    utils.Log('isLiveboxServer %s:%d' % (addr, port))
    try:
        server = utils.GetAddonMessage(addr, port, utils.SERVER)
        utils.Log(server)
        return server.lower() == 'server'
    except:
        pass

    return False


def isLivebox(addr, port):
    utils.Log('isLivebox %s:%d' % (addr, port))
    try:
        version = utils.GetAddonMessage(addr, port, utils.LBVERSION)
        utils.Log(version)
        return version
    except:
        pass

    return None


from zeroconf import ServiceBrowser, Zeroconf
import socket

class MyListener(object):
    def removeService(self, zeroconf, type, name):
        info = zeroconf.getServiceInfo(type, name)

        if not info:
            return

        name = name.replace('._http._tcp.local.','')
        addr = socket.inet_ntoa(info.address)
        port = info.port

        utils.Log('Service %s removed (%s:%d)' % (name, addr, port))


    def addService(self, zeroconf, type, name):
        info = zeroconf.getServiceInfo(type, name)

        if not info:
            return

        name = name.replace('._http._tcp.local.','')
        addr = socket.inet_ntoa(info.address)
        port = info.port

        if isLivebox(addr, port):
            setLivebox(name, addr, port)


import threading
class Scanner(threading.Thread):
    def __init__(self):
        super(Scanner, self).__init__()
        self.abort   = False


    def run(self):
        utils.Log('Starting Zeroconf Scan')

        self.listener = MyListener()
        self.zeroconf = Zeroconf()
        self.browser  = ServiceBrowser(self.zeroconf, "_http._tcp.local.", self.listener)

        while not self.abort:
            xbmc.sleep(100)

        self.zeroconf.close() 

        utils.Log('Ending Zeroconf Scan')

        exit()


    def stop(self):
        self.abort = True


    def getServers(self):
        return getServers()
