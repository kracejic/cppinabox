import sublime


class Settings(object):
    """docstring for Settings"""
    def __init__(self):
        super(Settings, self).__init__()


    def _get_settings():
        """Load settings.

        :returns: dictionary containing settings
        """
        return sublime.load_settings("cppinabox.sublime-settings")


    def get(view, key, default=None):
        """Load individual setting.

        :param key: setting key to get value for
        :param default: default value to return if no value found

        :returns: value for ``key`` if ``key`` exists, else ``default``
        """


        if view != None:
            if view.settings().get('cppinabox') != None:
                if key in view.settings().get('cppinabox'):
                    return view.settings().get('cppinabox')[key];    

        return Settings._get_settings().get(key, default)


