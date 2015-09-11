import collections
import hashlib
import hmac
import sublime


from .utils import *
from ..lib.settings import Settings
from .ycm_handler import *





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

        pluginEnabled = Settings.get(view, "enable", False)
        if not pluginEnabled:
            print('[Cppinabox] Plugin not enabled for this project - ' + name)
            return

        conf_path = Settings.get(view, "ycm_extra_conf", None)
        if conf_path:
            conf_path = os.path.join(os.path.dirname(name), conf_path)
            print('[Cppinabox] .ycm_extra_conf.py FOUND in settings. - ' + conf_path)
        else:
            conf_path = find_recursive(name)

        if conf_path:
            if os.path.isfile(conf_path):
                print('[Cppinabox] .ycm_extra_conf.py is FOUND on disk. - ' + conf_path)
                self.enabled = True
                self.conf_path = conf_path
                self.runServer()
            else:
                print('[Cppinabox] .ycm_extra_conf.py is WRONG. - ' + conf_path)
                self.enabled = False
        else:
            print('[Cppinabox] .ycm_extra_conf.py not found.')

    def getStrStatus(self):
        return "E="+str(self.enabled)+"/R="+str(self.running)

    def runServer(self):
        print('[Cppinabox] starting server - ' + self.conf_path)
        self.server = YcmdHandle.StartYcmdAndReturnHandle()
        # print('[Cppinabox] waiting until ready - ' + self.conf_path)
        self.server.WaitUntilReady()
        # print('[Cppinabox] YCMD server ready, configuring - ' + self.conf_path)
        self.server.LoadExtraConfFile(self.conf_path)
        print('[Cppinabox] YCMD server configured - ' + self.conf_path)
        self.running = True



_server = {}


def getServer(view, project=None, filepath=None):
    global _server
    if project == None:
        project = view.window().project_file_name()
    if project == None:
        project = get_file_path()

    if not project in _server:
        print("[Cppinabox] Creating ProjectYCMDObject( "+project+" )")
        _server[project] = ProjectYCMDObject(view, project)
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
            print("    ...actually shutting down")
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
        else
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
