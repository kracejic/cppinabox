import sublime
import sublime_plugin
import json
from threading import Thread

from .server import *
from .utils import *
from ..lib.settings import Settings
from ..lib.settings import printd



def goto_func(server, filepath, contents, row, col, callback, command):
    '''
    Thread that send goto declaration
    '''
    if command == "declaration":
        cmd = 'GoToDeclaration'
    elif command == "definition":
        cmd = 'GoToDefinition'
    elif command == "imprecise":
        cmd = 'GoToImprecise'
    else:
        cmd = 'GoTo'
    rst = server.server.SendRequest(filepath=filepath,
                             contents=contents,
                             filetype='cpp',
                             line_num=row,
                             column_num=col,
                             reqcommand=cmd)


    printd("[Cppinabox]   return("+cmd+") = " + str(rst))
    if rst == '':
        sublime.status_message("[Cppinabox] Cannot do "+cmd)
        print("[Cppinabox] Cannot do "+cmd)
        return
    data = json.loads(rst)
    # row = data.get('line_num', 1) - 1
    # col = data.get('column_num', 1) - 1
    # filepath = data.get('filepath', '')
    callback(data, cmd)


class CppycmgotoCommand(sublime_plugin.TextCommand):

    '''
    Goto command
    '''

    def run(self, edit, command):
        if not getServer().configured:
            printd("[Cppinabox] GOTO - test if configured and enabled - NO")
            return
        printd("[Cppinabox] GOTO - test if configured and enabled - YES")

        # prepare parameters
        row, col = get_row_col(self.view)
        filepath = get_file_path(self.view.file_name())
        contents = self.view.substr(sublime.Region(0, self.view.size()))

        # start goto thread
        t = Thread(None, goto_func, 'GotoAsync',
                   [getServer(), filepath, contents, row, col, self._goto, command])
        t.daemon = True
        t.start()

    def is_enabled(self):
        '''
        Determine if this command is enabled or not
        '''

        return is_cpp(self.view)

    def _goto(self, data, cmd):
        '''
        Goto declaration callback
        '''
        # point = self.view.text_point(row, col)
        # region = self.view.word(
        #     point) if check_select_after_goto() else sublime.Region(point, point)
        # self.view.sel().clear()
        # self.view.sel().add(region)
        # self.view.show_at_center(region)

        row = data.get('line_num', 1)
        col = data.get('column_num', 1)
        # filepath = get_file_path(data.get('filepath', self.view.file_name()), reverse=True)
        filepath = data.get('filepath', self.view.file_name())
        print("[Ycmd][GoTo] file: {}, row: {}, col: {}".format(filepath, row, col))
        sublime.active_window().open_file('{}:{}:{}'.format(filepath, row, col),
                                          sublime.ENCODED_POSITION)