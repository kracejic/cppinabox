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


class ProjectYCMDObject(object):
    """docstring for ProjectYCMDObject"""
    enabled = False
    running = False
    server = None
    name = None
    conf_path = None

    def __init__(self, view, name):
        super(ProjectYCMDObject, self).__init__()
        self.name = name

        self.reset(view)

    def reset(self, view):
        pluginEnabled = Settings.get(view, "enable", False)
        if not pluginEnabled:
            print('[Cppinabox] Plugin not enabled for this project - ' + self.name)
            return

        #find correct path
        conf_path = Settings.get(view, "ycm_extra_conf", None)
        if conf_path:
            if conf_path[0] == '\\' or conf_path[1] == ':':
              pass
            elif conf_path[0:2] == "./":
                conf_path = os.path.join(os.path.dirname(self.name), conf_path[2:])
            else:
                conf_path = os.path.join(os.path.dirname(self.name), conf_path)
            printd('[Cppinabox] .ycm_extra_conf.py FOUND in settings. - ' + conf_path)
        else:
            conf_path = find_recursive(self.name)

        if conf_path:
            if os.path.isfile(conf_path):
                printd('[Cppinabox] .ycm_extra_conf.py is FOUND on disk. - ' + conf_path)
                self.enabled = True
                self.conf_path = conf_path
                self.runServer()
            else:
                print('[Cppinabox] .ycm_extra_conf.py is specified, but wrongly. - ' + conf_path)
                self.enabled = False
        else:
            print('[Cppinabox] .ycm_extra_conf.py was not specified and was not found.')

    def getStrStatus(self):
        return "E="+str(self.enabled)+"/R="+str(self.running)

    def checkAndRestartIfNeeded(self, view):
        if self.enabled:
            self.running = False
            try:
                self.running = self.server.IsReady()
            except:
                print("[Cppinabox] Unexpected error:", sys.exc_info()[0])
            if self.running == False:
                try:
                    self.server.Shutdown()
                except:
                    print("[Cppinabox] Unexpected error:", sys.exc_info()[0])
                self.server = None
                self.reset(view)



    def runServer(self):
        printd('[Cppinabox] starting server - ' + self.conf_path)
        try:
            self.server = YcmdHandle.StartYcmdAndReturnHandle()
        except FileNotFoundError:
            print("[Cppinabox] File not found error: ", sys.exc_info())
            self.enabled = False
            sublime.error_message("[cppinabox] YCMD is enabled but it was not found on this path: \n" + Settings.getYcmdPath() 
                + "\n\nPlease configure valid path in user settings for cppinabox. You can trigger another attempt by executing 'Stop YCMD server' command (via ctrl+P). ")
            return
        except:
            print("[Cppinabox] Unexpected error:", sys.exc_info()[0])
            self.enabled = False
            return
        self.server.WaitUntilReady()
        self.server.LoadExtraConfFile(self.conf_path)
        self.server.WaitUntilReady()
        print('[Cppinabox] YCMD server configured and running - ' + self.conf_path)
        self.running = True



_server = {}


def getServer(view, project=None, filepath=None):
    global _server
    # start = time.time()
    if project == None:
        project = view.window().project_file_name()
    if project == None:
        project = get_file_path()


    if not project in _server:
        printd("[Cppinabox] Creating ProjectYCMDObject( "+project+" )")
        printd("[Cppinabox]   *- file_name = "+str(view.file_name()))
        printd("[Cppinabox]   *- name      = "+str(view.name()))
        printd("[Cppinabox]   *- is_scratch= "+str(view.is_scratch()))
        printd("[Cppinabox]   *- id        = "+str(view.id()))
        printd("[Cppinabox]   *- size      = "+str(view.size()))
        printd("[Cppinabox]   *- is_loading= "+str(view.is_loading()))
        printd("[Cppinabox]   *- is_read_only= "+str(view.is_read_only()))
        _server[project] = ProjectYCMDObject(view, project)
    _server[project].checkAndRestartIfNeeded(view)
    # print ("TIME= " + str((time.time() - start)*1000) + " ms")
    return _server[project]


def deleteCurrentServer(view):
    global _server
    name = sublime.active_window().project_file_name()
    if name in _server:
        print("[Cppinabox] Deleted YCM " + view.window().project_file_name())
        if _server[name]:
            if _server[name].server:
                print("  actually shutting down")
                _server[name].server.Shutdown()
        _server[name] = None

def deleteAllServers():
    global _server
    print ("[Cppinabox]  Deleting All YCMs()")
    for key,val in _server.items():
        print ("  " + key)
        if val.server:
            printd("    ...actually shutting down")
            val.server.Shutdown()
    _server = {}


def checkAllServers():
    global _server
    print ("[Cppinabox] Checking All YCMs()")
    for key,val in _server.items():
        print ("  " + key)
        if val.server:
            print("    ...actually checking")
            print("    Running: " + str(val.server.IsReady()))
        else:
            print("    not using ycmd")


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
