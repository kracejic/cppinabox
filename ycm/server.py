import collections
import hashlib
import hmac
import sublime
import sys
import time

from .utils import *
from ..lib.settings import Settings
from .ycm_handler import *
from ..lib.settings import printd





import os.path


class YCMDServer(object):
    """docstring for YCMDServer"""
    enabled = True
    running = False
    failcount = 0


    configured = False

    server = None
    lastConfPath = None

    def __init__(self):
        super(YCMDServer, self).__init__()
        printd('[Cppinabox] Wrapper Init')

    def _fail(self):
        self.running = False
        self.configured = False
        self.failcount = self.failcount + 1
        if self.failcount > 3:
            self.enabled = False

    def _runServer(self):
        if Settings.isEnabled() == False:
            printd('[Cppinabox] Not starting server, since it is disabled')
            return
        if self.enabled == False:
            printd('[Cppinabox] Not starting server, since it had some problems in past, try to restart it with restart')
            return
        printd('[Cppinabox] Starting server...')

        try:
            sublime.status_message("[Cppinabox] starting YCMD server")
            self.server = YcmdHandle.StartYcmdAndReturnHandle()
        except FileNotFoundError:
            self._fail()
            msg = "[cppinabox] YCMD is enabled but it was not found on this path: \n" \
                + Settings.getYcmdPath() + "\n\nPlease configure valid path in user \
                settings for cppinabox. You can trigger another attempt by executing \
                'Stop YCMD server' command (via ctrl+P). \n or Python is on wrong path"
            if self.failcount > 1:
                print(msg)
            else:
                sublime.error_message(msg)
                print(msg)
            return
        except:
            print("[Cppinabox] Unexpected error during startup of YCMD:", sys.exc_info())
            sublime.status_message("[Cppinabox] Unexpected error during startup of YCMD:")
            self._fail()
            return

        try:
            self.server.WaitUntilReady()
            self.running = True
        except:
            print("[Cppinabox] YCMD is not running even if it should:", sys.exc_info())
            sublime.status_message("[Cppinabox] YCMD is not running even if it should:")
            self._fail()
            return


    def loadConfig(self, view):
        self.configured = False
        if Settings.isEnabled() == False:
            printd('[Cppinabox] Plugin not enabled for current project')
            return
        if self.enabled == False:
            printd('[Cppinabox] Plugin was disabled')
            return
        if self.server == None:
            print('[Cppinabox] YCMD handler not instantiated') #should not happen
            return
        if self.running == False:
            print('[Cppinabox] Server not running')
            return

        projectPath = view.window().project_file_name()
        if projectPath == None:
            projectPath = get_file_path()
        filePath = get_file_path()

        #find correct path
        conf_path = Settings.get("ycm_extra_conf", None)
        if conf_path:
            if conf_path[0] == '\\' or conf_path[1] == ':':
              pass
            elif conf_path[0:2] == "./":
                conf_path = os.path.join(os.path.dirname(projectPath), conf_path[2:])
            else:
                conf_path = os.path.join(os.path.dirname(projectPath), conf_path)
            printd('[Cppinabox] .ycm_extra_conf.py FOUND in settings. - ' + conf_path)
        else:
            conf_path = find_recursive(filePath)

        if conf_path:
            if os.path.isfile(conf_path):
                printd('[Cppinabox] .ycm_extra_conf.py is FOUND on disk. - ' + conf_path)
            else:
                print('[Cppinabox] .ycm_extra_conf.py is specified, but wrongly. - ' + conf_path)
                return
        else:
            print('[Cppinabox] .ycm_extra_conf.py was not specified and was not found.')
            return

        printd(str(conf_path) + " == " + str(self.lastConfPath) + " ???")
        if conf_path == self.lastConfPath:
            self.configured = True
            # printd('[Cppinabox] PATH is the same, nothing configured - ' + os.path.normpath(conf_path))
            return

        self.server.LoadExtraConfFile(os.path.normpath(conf_path))
        try:
            self.server.WaitUntilReady()
        except:
            print("[Cppinabox] Unexpected error during configuring of YCMD:", sys.exc_info())
            self._fail()
            return

        self.lastConfPath = conf_path
        self.configured = True
        printd('[Cppinabox] YCMD server configured - ' + os.path.normpath(conf_path))


    def getStrStatus(self):
        if self.server:
            self.running = self.server.IsReady()
        return "E="+str(Settings.isEnabled())+" /R="+str(self.running)+" /C="+str(self.configured)

    def getStrStatusLong(self):
        if self.server:
            self.running = self.server.IsReady()
        txt =  "  Enabled="+str(Settings.isEnabled()) \
            +"\n  Runnning="+str(self.running) \
            +"\n  Configured="+str(self.configured) \
            +"\n  Failcount="+str(self.failcount)
        return txt


    def checkAndRestartIfNeeded(self, view):
        if self.enabled == True and Settings.isEnabled() == True:
            try:
                self.running = False
                if self.server:
                    self.running = self.server.IsReady()
            except:
                print("[Cppinabox] Error during isReady test:", sys.exc_info()[0])
            if self.running == False:
                self._stopServer()
                self._runServer()


    def _stopServer(self):
        try:
            if self.server:
                self.server.Shutdown()
        except:
            print("[Cppinabox] Error during shutdown:", sys.exc_info()[0])
        self.lastConfPath = None
        self.configured = False
        self.running = False
        self.server = None


    def stopServer(self):
        self.errorSilenced = False
        self.enabled = True
        self._stopServer()
        self.server = None





# static _server reference
_server1 = None

def loadConfig(view):
    global _server1
    if _server1 == None:
        _server1 = YCMDServer()
    if not is_cpp(view) or view.is_scratch():
        return
    _server1.checkAndRestartIfNeeded(view)
    _server1.loadConfig(view)
    return _server1

def getServer():
    global _server1
    if _server1 == None:
        printd("[Cppinabox] Wrapper not running")
        _server1 = YCMDServer()

    return _server1


def restartServer():
    getServer()
    if _server1:
        _server1.stopServer()
    _server1.checkAndRestartIfNeeded(sublime.active_window().active_view())


def stopServer():
    getServer()
    if _server1:
        _server1.stopServer()



def checkServer():
    getServer()
    txt =  "Status of cppinabox:\n";
    print("[Cppinabox] Checking Wrapper / YCMD")
    if _server1 == None:
        print("    Wrapper not running")
        txt = txt + "\n    Wrapper not running"
    else:
        print("    result: " + str(_server1.getStrStatusLong()))
        txt = txt + str(_server1.getStrStatusLong())
    return txt


