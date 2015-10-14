import sublime
import sublime_plugin
import json
from threading import Thread
from multiprocessing.pool import ThreadPool

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
        callbackFail()
        return

    try:
        data = json.loads(rst)
    except:
        printd(" EXCPETION reading json")
        callbackFail()
        return
        
    callback(data)


class CustomBaseCommandCommand(sublime_plugin.TextCommand):

    '''
    CustomBaseCommandCommand
    '''
    command = ""
    edit = None

    t = None

    def run2(self, row, col, filepath, contents):
        pass

    def run(self, edit):
        if not getServer().configured:
            printd("[Cppinabox] [Cmd] "+self.command+" - test if configured and enabled - NO")
            return
        printd("[Cppinabox] [Cmd] "+self.command+" - test if configured and enabled - YES")
        self.edit = edit

        # prepare parameters
        row, col = get_row_col(self.view)
        filepath = get_file_path(self.view.file_name())
        contents = self.view.substr(sublime.Region(0, self.view.size()))

        # start goto thread
        self.t = Thread(None, goto_func, 'GotoAsync',
                   [getServer(), filepath, contents, row, col, self.onSuccess, 
                   self.onFail, self.command])
        self.t.daemon = True
        sublime.status_message("[Cppinabox] Request "+self.command+" sent ... ")
        self.t.start()
        self.run2(row, col, filepath, contents)



    def is_enabled(self):
        '''
        Determine if this command is enabled or not
        '''
        return is_cpp(self.view)

    def onSuccess(self, data):
        print("[Cppinabox] [Cmd] "+self.command+" onSuccess - not implemented")

    def onFail(self):
        print("[Cppinabox] [Cmd] "+self.command+" onFail - not implemented")


class CppinaboxgotoCommand(CustomBaseCommandCommand):
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


class CppinaboxgotodeclarationCommand(CppinaboxgotoCommand):
    command = "GoToDeclaration"


class CppinaboxgotodefinitionCommand(CppinaboxgotoCommand):
    command = "GoToDefinition"


class CppinaboxgotoimpreciseCommand(CppinaboxgotoCommand):
    command = "GoToImprecise"



def displayResult(text):
    window = sublime.active_window()
    pt = window.create_output_panel("cppinaboxPanel")

    pt.set_read_only(False)
    pt.run_command('erase_view')
    pt.run_command('append', {'characters': text})
    pt.set_read_only(True)

    window.run_command("show_panel", {"panel": "output."+"cppinaboxPanel"})







class CppinaboxgetBaseMessageCommand(CustomBaseCommandCommand):
    command = "GetParent"
    whereDataAre = ""

    def onSuccess(self, data):
        sublime.status_message("[Cppinabox] "+self.command+" success")
        if self.whereDataAre in data:
            print("[Cppinabox] "+self.command+" success")
            displayResult(data[self.whereDataAre])

    def onFail(self):
        print("[Cppinabox] [Cmd] "+self.command+" failed")
        sublime.status_message("[Cppinabox] "+self.command+" failed")
        displayResult("nothing was found")




class CppinaboxgetparentCommand(CppinaboxgetBaseMessageCommand):
    command = "GetParent"
    whereDataAre = "message"


class CppinaboxgettypeCommand(CppinaboxgetBaseMessageCommand):
    command = "GetType"
    whereDataAre = "message"


class CppinaboxgetdocquickCommand(CppinaboxgetBaseMessageCommand):
    command = "GetDocQuick"
    whereDataAre = "detailed_info"


class CppinaboxgetdocCommand(CppinaboxgetBaseMessageCommand):
    command = "GetDoc"
    whereDataAre = "detailed_info"
    t2 = None

    gotoData = None
 
    def run2(self, row, col, filepath, contents):
        print("brekeke")
        self.t2 = Thread(None, goto_func, 'GoTo',
                   [getServer(), filepath, contents, row, col, self.onSuccessGOTO, 
                   self.onFailGOTO, 'GoTo'])
        self.t2.daemon = True
        sublime.status_message("[Cppinabox] Request "+self.command+" sent ... ")
        self.t2.start()


    def onSuccessGOTO(self, data):
        self.gotoData = data
        pass

    def onFailGOTO(self):
        self.gotoData = False
        pass

    def onFail(self):
        print("[Cppinabox] [Cmd] "+self.command+" failed")
        sublime.status_message("[Cppinabox] "+self.command+" failed")

        self.t2.join()

        if self.gotoData == None:
            printd("[Cppinabox] [Cmd] "+self.command+" self.gotoData == None")
        if self.gotoData == False:
            printd("[Cppinabox] [Cmd] "+self.command+" self.gotoData == False")
        else:
            printd("[Cppinabox] [Cmd] "+self.command+" self.gotoData ELSE" + str(self.gotoData))

            #{'line_num': 59, 'column_num': 13, 'filepath': 'C:\\Users\\cz2b11q9\\AppData\\Roaming\\Sublime Text 3\\Packages\\cppinabox\\test\\test.h'}
            ret = ""
            with open(self.gotoData["filepath"]) as source:
                linenum = 0
                targetLine = self.gotoData["line_num"]
                for line in source:
                    linenum += 1
                    if linenum > (targetLine-5) and linenum < (targetLine+7):
                        ret = ret + line
                    if linenum == targetLine:
                        ret = ret + "// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"

            self.onSuccess({"detailed_info":ret})
            return

        print("[Cppinabox] [Cmd] "+self.command+" failed")
        sublime.status_message("[Cppinabox] "+self.command+" failed")
        displayResult("nothing was found")











