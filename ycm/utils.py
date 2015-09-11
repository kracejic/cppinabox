import os
import sublime

def get_plugin_path():
    '''
    Get path of the C++YouCompleteMe plugin.
    '''
    plugin_path = os.path.abspath(
        os.path.join(sublime.packages_path(), 'C++YouCompleteMe'))
    return plugin_path


def get_ycmd_path():
    '''
    Get path of the ycmd server.
    '''
    settings = sublime.load_settings('C++YouCompleteMe.sublime-settings')
    ycmd_path = settings.get('ycmd_path', os.path.join(
        get_plugin_path(), 'server'))
    ycmd_path = os.path.join(ycmd_path, 'ycmd')
    return ycmd_path


def get_python_path():
    '''
    Get path of python.
    '''
    settings = sublime.load_settings('C++YouCompleteMe.sublime-settings')
    python_path = settings.get('python_path', 'python')
    return python_path


def get_file_path(filepath=None):
    '''
    Get path of the editing file.
    '''
    if not filepath:
        filepath = active_view().file_name()
    if not filepath:
        filepath = 'tmpfile.cpp'
    return filepath

def get_error_panel_syntax_file():
    settings = sublime.load_settings('C++YouCompleteMe.sublime-settings')
    filepath = settings.get('error_panel_syntax_file',  os.path.join(
        get_plugin_path(), 'ErrorPanel.tmLanguage'))
    return filepath


def check_highlight_on_save():
    '''
    Get if highlight on save.
    '''
    settings = sublime.load_settings('C++YouCompleteMe.sublime-settings')
    rst = settings.get('highlight_errors_on_save', False)
    return rst


def check_select_after_goto():
    '''
    Get if select element after goto command.
    '''
    settings = sublime.load_settings('C++YouCompleteMe.sublime-settings')
    rst = settings.get('select_after_goto', False)
    return rst


def check_ycmd_server():
    '''
    Check if ycmd server exists.
    '''
    return os.path.exists(get_ycmd_path())


def find_recursive(path):
    '''
    Find ycm_extra_conf in path and all directories above it.
    '''
    path = os.path.dirname(path)
    while(True):
        if os.path.exists(os.path.join(path, '.ycm_extra_conf.py')):
            return os.path.join(path, '.ycm_extra_conf.py')
        parent_dir = os.path.dirname(path)
        if parent_dir == path:
            break
        else:
            path = parent_dir
    return None


def is_cpp(view):
    '''
    Determine if the given view is c++ code
    '''
    try:
        return view.match_selector(view.sel()[0].begin(), 'source.c++')
        print("[C++YouCompleteMe] IsCPP")
    except:
        return False


def active_view():
    '''
    Return active view
    '''
    return sublime.active_window().active_view()


def get_row_col(view, location=None):
    '''
    Return 1-based row and column of selected region
    If location is None, set location to cursor location.
    '''
    try:
        if not location:
            location = view.sel()[0].begin()
        row, col = view.rowcol(location)
        return (row + 1, col + 1)
    except:
        return None

