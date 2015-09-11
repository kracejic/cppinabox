import collections
import hashlib
import hmac
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import sublime

from base64 import b64encode, b64decode
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError

from .utils import *
from ..lib.settings import Settings
# from .msgs import MsgTemplates

_server = {}




class ProjectYCMDObject(object):
    """docstring for ProjectYCMDObject"""
    enabled = False
    server = None
    name = None

    def __init__(self, name):
        super(ProjectYCMDObject, self).__init__()
        self.name = name

        conf_path = find_recursive(filepath)






def getYCMServer(project=None, filepath=None):
    if project == None:
        project = sublime.active_window().project_file_name()

    if not project in _server:
        print("[Cppinabox] Creating ProjectYCMDObject( "+project+" )")
        _server[project] = ProjectYCMDObject(project)
    return _server[project]


def deleteCurrentYCMServer():
    name = sublime.active_window().project_file_name()
    if name in _server:
        print("[Cppinabox] Deleted YCM " + sublime.active_window().project_file_name())
        _server[name] = None

def deleteAllYCMServer():
    print ("[Cppinabox]  Deleting All YCMs()")
    for key,val in d.items():
        print ("  " + key)
    _server = {}


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
