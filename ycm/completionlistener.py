import sublime
import sublime_plugin
import json
from threading import Thread

from .server import *
from .utils import *
from ..lib.settings import Settings
from ..lib.settings import printd


def complete_func(server, filepath, contents, row, col, callback):
    '''
    Thread that send completion request
    '''

    rst = server.server.SendCodeCompletionRequest(filepath=filepath,
                                           contents=contents,
                                           filetype='cpp',
                                           line_num=row,
                                           column_num=col)
    printd("[Cppinabox]   return = " + str(rst))
    if rst == '':
        return

    completions = json.loads(rst)['completions']

    data = []
    for comp in completions:
        for detailed_info in comp.get('detailed_info', '').strip().split('\n'):
            data.append(
                (
                    '{}\t{}'.format(detailed_info,
                                    comp.get('kind', '').lower()
                                    ),
                    comp.get('insertion_text', '')
                )
            )
    callback(data)


class CppYCMCompletionsListener(sublime_plugin.EventListener):

    def __init__(self):
        self.completions = []
        self.ready_from_defer = False
        self.view_cache = dict()
        self.view_line = dict()
        self.extra_conf_loaded = False

    def on_query_completions(self, view, prefix, locations):
        '''
        Sublime Text autocompletion event handler.
        '''
        printd("[Cppinabox] Completions start, test if cpp")
        if not is_cpp(view) or view.is_scratch():
            return
        printd("[Cppinabox]              YES")

        printd("[Cppinabox] Completions - test if enabled")
        if not Settings.get(view, 'enable', False):
            return
        printd("[Cppinabox]              YES")

        # if completion should begin
        leftchar = view.substr(locations[0] - 2)
        thischar = view.substr(locations[0] - 1)
        if thischar == '>' and leftchar != '-':
            return
        if thischar == ':' and leftchar != ':':
            return

        printd("[Cppinabox] Start completing." + str(self.ready_from_defer))

        if self.ready_from_defer is True:
            cpl = self.completions
            self.completions = []
            self.ready_from_defer = False
            return (cpl, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        filepath = get_file_path(view.file_name())
        contents = view.substr(sublime.Region(0, view.size()))

        # get 1-based location
        row, col = get_row_col(view, locations[0])

        # start code-completion thread
        t = Thread(None, complete_func, 'CompleteAsync',
                   [getServer(view), filepath, contents, row, col, self._complete])
        t.daemon = True
        printd("[Cppinabox] Starting daemon")
        t.start()

    def _complete(self, proposals):
        if len(proposals):
            active_view().run_command("hide_auto_complete")
            self.completions = proposals
            self.ready_from_defer = True
            self._run_auto_complete()
        else:
            sublime.status_message("[Cppinabox] Completion not available")
            print("[Cppinabox] Completion not available")

    def _run_auto_complete(self):
        active_view().run_command("auto_complete", {
            'disable_auto_insert': True,
            'next_completion_if_showing': False,
            'auto_complete_commit_on_tab': True,
        })
