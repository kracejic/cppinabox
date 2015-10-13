import sublime, sublime_plugin
from .lib.settings import Settings
from .ycm import *
from .ycm.completionlistener import CppinaboxCompletionsListener
from .ycm.server import *
from .lib.settings import printd

import urllib.request


class CppinaboxdebugtestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # print("test = " + str(Settings.get(self.view, "test", "default")))
        # print("Active window - " + sublime.active_window().project_file_name())
        # deleteAllServers()
        # loc = "http://localhost:62562/ready"
        # print("Connecting to: " + loc)
        # proxies={'http':None}
        # # print(urllib.request.FancyURLopener({}).open(loc).read())
        # # print(urllib.request.urlopen(loc, proxies={}).read())

        # proxy_handler = urllib.request.ProxyHandler({})
        # opener = urllib.request.build_opener(proxy_handler)
        # opener.open('http://localhost:62562/ready')
        # print(str(opener.open(loc)))
        # print(str(opener.open(loc).read()))
        # print(urllib.request.urlopen(loc, proxies={}).read())
        #
        #
        #
        window = sublime.active_window()
        pt = window.create_output_panel("paneltest")
        pt.set_read_only(False)
        # edit = pt.begin_edit()
        pt.insert(edit, pt.size(), "Writing...2")
        pt.set_read_only(True)
        # pt.end_edit(edit)
        window.run_command("show_panel", {"panel": "output.paneltest"})


class CppinaboxkillallCommand(sublime_plugin.TextCommand):
    '''
    Kills the server and clears all the flags... this causes server to restart
    '''
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
    print("[Cppinabox] plugin_loaded()")


def plugin_unloaded():
    print("[Cppinabox] plugin_unloaded()")
    stopServer()

