import sublime, sublime_plugin
from .lib.settings import Settings
from .ycm import *
from .ycm.completionlistener import CppYCMCompletionsListener
from .ycm.server import *
from .lib.settings import printd

class CppinaboxdebugtestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print("test = " + str(Settings.get(self.view, "test", "default")))
        print("Active window - " + sublime.active_window().project_file_name())
        # deleteAllServers()

class CppinaboxkillallCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        stopServer()

class CppinaboxycmdstatusCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        checkServer()



class CppYCMLoadExtraConfListener(sublime_plugin.EventListener):

    '''
    Activate ycmd server and loads extra_conf on cpp file loaded.
    '''

    def on_activated_async(self, view):
        loadConfig(view)
        status = getServer().getStrStatus()
        printd("[Cppinabox] on_activated_async() " + status + " - " + get_file_path(view.file_name()) )


def plugin_loaded():
    print("[Cppinabox] plugin_loaded() " + str(sublime.active_window().project_file_name()))
    #TODO
    # sublime.message_dialog('[Cppinabox] Ycmd is not found, see https://github.com/glymehrvrd/CppYCM#installation for install instructions.')


def plugin_unloaded():
    print("[Cppinabox] plugin_unloaded() " + str(sublime.active_window().project_file_name()))
    deleteAllServers()
    # server().Shutdown()

