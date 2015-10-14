import sublime
import sublime_plugin
import os.path

from .lib.settings import Settings
from .lib.settings import printd


class CppinaboxOpenHeaderCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        filepath = self.view.file_name()
        if filepath == None:
            return
        if os.path.exists(filepath) == False:
            return

        searchDirs = [os.path.dirname(filepath), 
            os.path.dirname(os.path.dirname(filepath))]

        extension = os.path.splitext(filepath)[1]
        bareName = os.path.splitext(os.path.split(filepath)[1])[0]
        dirPath = os.path.dirname(filepath)

        printd("Open Header")
        printd(" filepath = " + filepath)
        printd(" dirPath = " + dirPath)
        printd(" dirPathUp = " + os.path.dirname(os.path.dirname(filepath)))
        printd(" extension = " + extension)
        printd(" bareName = " + bareName)

        possibleDirs = []
        if extension in Settings.get("header_extensions", []):
            possibleExtensions = Settings.get("source_extensions", [])
            possibleDirs = Settings.get("source_directories_paths", [])
        elif extension in Settings.get("source_extensions", []):
            possibleExtensions = Settings.get("header_extensions", [])
            possibleDirs = Settings.get("header_directories_paths", [])
        else:
            sublime.status_message("[Cppinabox] [OpenHeader] Not C/C++ file")
            print("[Cppinabox] [OpenHeader] Not C/C++ file")
            return

        tmpList = []
        for x in possibleDirs:
            tmpList.append("../"+x)
        possibleDirs.extend(tmpList)


        for directory in possibleDirs:
            for ext in possibleExtensions:
                filename = os.path.normpath(os.path.join(dirPath, directory, bareName + ext))
                if os.path.exists(filename):
                    printd("  * " + filename)
                    sublime.active_window().open_file(filename)
                    return
                else:
                    printd("    " + filename)

        sublime.status_message("[Cppinabox] [OpenHeader] Cannot find header/source for this file ")
        print("[Cppinabox] [OpenHeader] Cannot find header/source for this file ")
        pass

