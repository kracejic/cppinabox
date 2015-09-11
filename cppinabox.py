import sublime, sublime_plugin
from .lib.settings import Settings
from .ycm.server import *

class CppinaboxdebugtestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print("test = " + str(Settings.get(self.view, "test", "default")))
        print("Active window - " + sublime.active_window().project_file_name())
        deleteAllServers()

class CppinaboxkillallCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        deleteAllServers()

class CppinaboxycmdstatusCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        checkAllServers()



class CppYCMLoadExtraConfListener(sublime_plugin.EventListener):

    '''
    Activate ycmd server and loads extra_conf on cpp file loaded.
    '''

    def on_activated_async(self, view):
        print("[Cppinabox] on_activated_async() " + get_file_path(view.file_name()) + " " + getServer(view).getStrStatus())


def plugin_loaded():
    print("[Cppinabox] plugin_loaded() " + sublime.active_window().project_file_name())
    #TODO
    # sublime.message_dialog('[Cppinabox] Ycmd is not found, see https://github.com/glymehrvrd/CppYCM#installation for install instructions.')


def plugin_unloaded():
    print("[Cppinabox] plugin_unloaded() " + sublime.active_window().project_file_name())
    deleteAllServers()
    # server().Shutdown()

