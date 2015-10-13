import sublime
import os

class Settings(object):
    """docstring for Settings"""
    def __init__(self):
        super(Settings, self).__init__()


    def _get_settings():
        """Load settings.

        :returns: dictionary containing settings
        """
        return sublime.load_settings("cppinabox.sublime-settings")

    def isDebugMode():
        return Settings.get(None, "debugMode", False)

    def isEnabled():
        return Settings.get(None, "enable", False)

    def getYcmdPath():
        ycmd_path = Settings._get_settings().get("ycmd_path", "server")
        ycmd_path = os.path.join(ycmd_path, 'ycmd')
        ycmd_path = str(ycmd_path).replace("\\", "/")
        return ycmd_path

    def isMSYSenviroment():
        return Settings._get_settings().get("MSYS_path_fix", False)

    def getMSYSPRECommand():
        return Settings._get_settings().get("MSYS_pre_command", "")

    def get(view, key, default=None):
        """Load individual setting.

        :param key: setting key to get value for
        :param default: default value to return if no value found

        :returns: value for ``key`` if ``key`` exists, else ``default``
        """
        if view == None:
            view = sublime.active_window().active_view()

        if view != None:
            if view.settings().get('cppinabox') != None:
                if key in view.settings().get('cppinabox'):
                    return view.settings().get('cppinabox')[key];

        return Settings._get_settings().get(key, default)


def printd(*args):
    if Settings.isDebugMode() == True:
        print(*args)

