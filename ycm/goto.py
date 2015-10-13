import sublime
import sublime_plugin
import json
from threading import Thread

from .server import *
from .utils import *
from ..lib.settings import Settings
from ..lib.settings import printd



def goto_func(server, filepath, contents, row, col, callback, callbackFail, cmd):
    '''
    Thread that sends request to server and waits for response. It will call 
    proper callback on the end.
    '''


    rst = server.server.SendRequest(filepath=filepath,
                             contents=contents,
                             filetype='cpp',
                             line_num=row,
                             column_num=col,
                             reqcommand=cmd)


    printd("[Cppinabox] [Cmd]   return("+cmd+") = " + str(rst))
    if rst == '':
        # sublime.status_message("[Cppinabox] Cannot do "+cmd)
        # print("[Cppinabox] Cannot do "+cmd)
        callbackFail()

    data = json.loads(rst)
    # row = data.get('line_num', 1) - 1
    # col = data.get('column_num', 1) - 1
    # filepath = data.get('filepath', '')
    callback(data)


class CustomBaseCommandCommand(sublime_plugin.TextCommand):

    '''
    CustomBaseCommandCommand
    '''
    command = ""

    def run(self, edit):
        if not getServer().configured:
            printd("[Cppinabox] [Cmd] "+self.command+" - test if configured and enabled - NO")
            return
        printd("[Cppinabox] [Cmd] "+self.command+" - test if configured and enabled - YES")

        # prepare parameters
        row, col = get_row_col(self.view)
        filepath = get_file_path(self.view.file_name())
        contents = self.view.substr(sublime.Region(0, self.view.size()))

        # start goto thread
        t = Thread(None, goto_func, 'GotoAsync',
                   [getServer(), filepath, contents, row, col, self.onSuccess, 
                   self.onFail, self.command])
        t.daemon = True
        sublime.status_message("[Cppinabox] Request "+self.command+" sent ... ")
        t.start()

    def is_enabled(self):
        '''
        Determine if this command is enabled or not
        '''
        return is_cpp(self.view)

    def _goto(self, data):
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
        printd("[Cppinabox]  [Cmd]GOTO file: {}, row: {}, col: {}".format(filepath, row, col))
        sublime.active_window().open_file('{}:{}:{}'.format(filepath, row, col),
                                          sublime.ENCODED_POSITION)

    def onSuccess(self, data):
        print("[Cppinabox] [Cmd] "+self.command+" onSuccess - not implemented")

    def onFail(self):
        print("[Cppinabox] [Cmd] "+self.command+" onFail - not implemented")


class CppycmgotoCommand(CustomBaseCommandCommand):
    command = "GoTo"

    def onSuccess(self, data):
        row = data.get('line_num', 1)
        col = data.get('column_num', 1)
        # filepath = get_file_path(data.get('filepath', self.view.file_name()), reverse=True)
        filepath = data.get('filepath', self.view.file_name())
        printd("[Cppinabox] [Cmd] "+self.command+" file: {}, row: {}, col: {}".format(filepath, row, col))
        sublime.active_window().open_file('{}:{}:{}'.format(filepath, row, col),
                                          sublime.ENCODED_POSITION)
        print("[Cppinabox] "+self.command+" success")
        sublime.status_message("[Cppinabox] "+self.command+" success")

    def onFail(self):
        print("[Cppinabox] [Cmd] "+self.command+" failed")
        sublime.status_message("[Cppinabox] "+self.command+" failed")


class CppycmgotodeclarationCommand(CppycmgotoCommand):
    command = "GoToDeclaration"

class CppycmgotodefinitionCommand(CppycmgotoCommand):
    command = "GoToDefinition"


class CppycmgotoimpreciseCommand(CppycmgotoCommand):
    command = "GoToImprecise"





class CppycmgetparentCommand(CustomBaseCommandCommand):
    command = "GetParent"

    def onSuccess(self, data):
        print("[Cppinabox] "+self.command+" success")
        sublime.status_message("[Cppinabox] "+self.command+" success")

    def onFail(self):
        print("[Cppinabox] [Cmd] "+self.command+" failed")
        sublime.status_message("[Cppinabox] "+self.command+" failed")

