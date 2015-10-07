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
    enabled = False
    running = False
    configured = False

    server = None
    conf_path = None
    errorSilenced = False

    def __init__(self):
        super(YCMDServer, self).__init__()
        print('[Cppinabox] Wrapper Init')

    def runServer(self):
        printd('[Cppinabox] Starting server')
        try:
            self.server = YcmdHandle.StartYcmdAndReturnHandle()
        except FileNotFoundError:
            print("[Cppinabox] File not found error: ", sys.exc_info())
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
            print("[Cppinabox] Unexpected error:", sys.exc_info()[0])
            self.enabled = False
            return
        self.server.WaitUntilReady()
        self.running = True

    def loadConfig(self, view):
        pluginEnabled = Settings.get(view, "enable", False)
        self.configured = False
        if not pluginEnabled:
            print('[Cppinabox] Plugin not enabled for current project')
            return
        if self.running == False:
            print('[Cppinabox] Server not running')
            return
        if self.server == None:
            print('[Cppinabox] YCMD low level not instantiated')
            return

        if projectPath == None:
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

        self.server.LoadExtraConfFile(path)
        self.server.WaitUntilReady()
        self.configured = True
        print('[Cppinabox] YCMD server configured - ' + conf_path)

    def getStrStatus(self):
        if self.server:
            self.running = self.server.IsReady()
        return "E="+str(self.enabled)+" /R="+str(self.running)+" /C="+str(self.configured)

    def checkAndRestartIfNeeded(self, view):
        self.enabled = Settings.get(view, "enable", False)
        if self.enabled:
            try:
                self.running = False
                if self.server:
                    self.running = self.server.IsReady()
            except:
                print("[Cppinabox] Unexpected error:", sys.exc_info()[0])
            if self.running == False:
                try:
                    if self.server:
                        self.server.Shutdown()
                except:
                    print("[Cppinabox] Unexpected error:", sys.exc_info()[0])
                self.server = None
                self.runServer()


    def stopServer(self):
        self.errorSilenced = False
        if self.server == None:
            return
        try:
            self.server.Shutdown()
        except:
            print("[Cppinabox] Unexpected error:", sys.exc_info()[0])
        self.server = None



    def isRunning():
        if self.server:
            if self.running:
                self.running = self.server.IsReady()
                if self.running:
                    return True
        return False





_server = {}

_server1 = None

def loadConfig(view):
    global _server1
    if _server1 == None:
        _server1 = YCMDServer()
    _server1.checkAndRestartIfNeeded(view)
    _server1.loadConfig(view)
    return _server1

def getServer():
    global _server1
    if _server1 == None:
        print("[Cppinabox] Wrapper not running")

    return _server1


def stopServer():
    global _server1
    if _server1:
        _server1.stopServer()

def checkServer():
    global _server1
    print("[Cppinabox] Checking Wrapper / YCMD")
    print("    result: " + str(_server1.getStrStatus()))
    print("    result: " + str(_server1.isRunning()))



# def getServer(view, project=None, filepath=None):
#     global _server

#     if project == None:
#         project = view.window().project_file_name()
#     if project == None:
#         project = get_file_path()


#     if not project in _server:
#         printd("[Cppinabox] Creating YCMDServer( "+project+" )")
#         printd("[Cppinabox]   *- file_name = "+str(view.file_name()))
#         printd("[Cppinabox]   *- name      = "+str(view.name()))
#         printd("[Cppinabox]   *- is_scratch= "+str(view.is_scratch()))
#         printd("[Cppinabox]   *- id        = "+str(view.id()))
#         printd("[Cppinabox]   *- size      = "+str(view.size()))
#         printd("[Cppinabox]   *- is_loading= "+str(view.is_loading()))
#         printd("[Cppinabox]   *- is_read_only= "+str(view.is_read_only()))
#         _server[project] = YCMDServer(view, project)
#     _server[project].checkAndRestartIfNeeded(view)
#     return _server[project]


# def deleteAllServers():
#     global _server
#     print ("[Cppinabox]  Deleting All YCMs()")
#     for key,val in _server.items():
#         print ("  " + key)
#         if val.server:
#             printd("    ...actually shutting down")
#             val.server.Shutdown()
#     _server = {}


# def checkAllServers():
#     global _server
#     print ("[Cppinabox] Checking All YCMs()")
#     for key,val in _server.items():
#         print ("  " + key)
#         if val.server:
#             print("    ...actually checking")
#             print("    Running: " + str(val.server.IsReady()))
#         else:
#             print("    not using ycmd")


# def server(filepath=None):
#     '''
#     return singleton server instance and load extra configuration.
#     '''
#     global _server
#     if not _server and filepath:
#         # load server
#         print("[C++YouCompleteMe] Loading server")
#         _server = _YcmdHandle.StartYcmdAndReturnHandle()
#         _server.WaitUntilReady()
#         print(MsgTemplates.LOAD_SERVER_FINISHED.format(
#               _server._server_location))
#     if not _server:
#         raise RuntimeError(MsgTemplates.SERVER_NOT_LOADED)
#     return _server

# def deleteSingleton():
#     '''
#     deletes Singleton for use in restart
#     '''
#     global _server
#     _server = None
