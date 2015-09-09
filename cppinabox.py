import sublime, sublime_plugin
from .lib.settings import Settings

class CppinaboxdebugtestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print("test = " + str(Settings.get(self.view, "test", "default")))


