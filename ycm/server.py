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
    configured = False

    server = None
    conf_path = None
    errorSilenced = False

    def __init__(self):
        super(YCMDServer, self).__init__()
        printd('[Cppinabox] Wrapper Init')


    def runServer(self):
        printd('[Cppinabox] Starting server')
        if self.enabled == False:
            printd('[Cppinabox] ... is disabled')
            return

        try:
            self.server = YcmdHandle.StartYcmdAndReturnHandle()
        except FileNotFoundError:
            self.enabled = False
            self.running = False
            self.configured = False
            msg = "[cppinabox] YCMD is enabled but it was not found on this path: \n" + Settings.getYcmdPath() + "\n\nPlease configure valid path in user settings for cppinabox. You can trigger another attempt by executing 'Stop YCMD server' command (via ctrl+P). "
            if self.errorSilenced:
                print(msg)
            else:
                sublime.error_message(msg)
            self.errorSilenced = True
            return
        except:
            print("[Cppinabox] Unexpected error during startup of YCMD:", sys.exc_info())
            self.enabled = False
            return

        try:
            self.server.WaitUntilReady()
            self.running = True
        except:
            print("[Cppinabox] YCMD is not running even if it should:", sys.exc_info())
            self.enabled = False
            return


    def loadConfig(self, view):
        pluginEnabled = Settings.get(view, "enable", False)
        self.configured = False
        if not pluginEnabled:
            printd('[Cppinabox] Plugin not enabled for current project')
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
        conf_path = Settings.get(view, "ycm_extra_conf", None)
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

        self.server.LoadExtraConfFile(os.path.normpath(conf_path))
        self.server.WaitUntilReady()
        self.configured = True
        printd('[Cppinabox] YCMD server configured - ' + os.path.normpath(conf_path))


    def getStrStatus(self):
        if self.server:
            self.running = self.server.IsReady()
        return "E="+str(self.enabled)+" /R="+str(self.running)+" /C="+str(self.configured)


    def checkAndRestartIfNeeded(self, view):
        pluginEnabled = Settings.get(view, "enable", False)
        if self.enabled == True and pluginEnabled == True:
            try:
                self.running = False
                if self.server:
                    self.running = self.server.IsReady()
            except:
                print("[Cppinabox] Error during isReady test:", sys.exc_info()[0])
            if self.running == False:
                try:
                    if self.server:
                        self.server.Shutdown()
                except:
                    print("[Cppinabox] Error during shutdown:", sys.exc_info()[0])
                self.server = None
                self.runServer()


    def stopServer(self):
        self.errorSilenced = False
        self.enabled = True
        if self.server == None:
            return
        try:
            self.server.Shutdown()
        except:
            print("[Cppinabox] Error during shutdown2:", sys.exc_info()[0])
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


def stopServer():
    getServer()
    if _server1:
        _server1.stopServer()

def checkServer():
    getServer()
    print("[Cppinabox] Checking Wrapper / YCMD")
    if _server1 == None:
        print("    Wrapper not running")
    else:
        print("    result: " + str(_server1.getStrStatus()))



