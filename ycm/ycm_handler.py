import collections
import hashlib
import hmac
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import sublime
import traceback

from base64 import b64encode, b64decode
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlencode
from urllib.error import HTTPError
import urllib

from .utils import *
from ..lib.settings import Settings
from ..lib.settings import printd
# from .msgs import MsgTemplates




HMAC_HEADER = 'X-Ycm-Hmac'
HMAC_SECRET_LENGTH = 16
SERVER_IDLE_SUICIDE_SECONDS = 3600
MAX_SERVER_WAIT_TIME_SECONDS = 10

# Set this to True to see ycmd's output interleaved with the client's
INCLUDE_YCMD_OUTPUT = True
DEFINED_SUBCOMMANDS_HANDLER = '/defined_subcommands'
CODE_COMPLETIONS_HANDLER = '/completions'
COMPLETER_COMMANDS_HANDLER = '/run_completer_command'
EVENT_HANDLER = '/event_notification'
EXTRA_CONF_HANDLER = '/load_extra_conf_file'

# Wrapper around ycmd's HTTP+JSON API

class MsgTemplates:
    # COMPLETION_ERROR_MSG = "[Cppinabox][Completion] Error {}"
    # COMPLETION_NOT_AVAILABLE_MSG = "[Cppinabox] No completion available"
    # ERROR_MESSAGE_TEMPLATE = "[{kind}] {text}"
    # GET_PATH_ERROR_MSG = "[Cppinabox][Path] Failed to replace '{}' -> '{}'"
    # NO_HMAC_MESSAGE = "[Cppinabox] You should generate HMAC throug the menu before using plugin"
    # NOTIFY_ERROR_MSG = "[Cppinabox][Notify] Error {}"
    # PRINT_ERROR_MESSAGE_TEMPLATE = "[Cppinabox] > {} ({},{})\n"
    # LOAD_EXTRA_CONF_FINISHED = '[Cppinabox] Finished loading extra configuration.'
    # LOAD_SERVER_FINISHED = '[Cppinabox] Ycmd server registered, location: {}'
    # SERVER_NOT_LOADED = '[Cppinabox] Ycmd server is not loaded.'
    pass

class Event(object):
    # FileReadyToParse = 1
    # BufferUnload = 2
    # BufferVisit = 3
    # InsertLeave = 4
    # CurrentIdentifierFinished = 5
    FileReadyToParse = 'FileReadyToParse'
    BufferUnload = 'BufferUnload'
    BufferVisit = 'BufferVisit'
    InsertLeave = 'InsertLeave'
    CurrentIdentifierFinished = 'CurrentIdentifierFinished'
    pass

class YcmdHandle(object):

    def __init__(self, popen_handle, port, hmac_secret):
        self._popen_handle = popen_handle
        self._port = port
        self._hmac_secret = hmac_secret  # bytes
        self._server_location = 'http://127.0.0.1:%d' % port

        proxy_handler = urllib.request.ProxyHandler({})
        self.proxyLessUrlOpen = urllib.request.build_opener(proxy_handler)
        

    @classmethod
    def StartYcmdAndReturnHandle(cls):
        prepared_options = DefaultSettings()

        # generate random hmac secrete
        hmac_secret = os.urandom(HMAC_SECRET_LENGTH)
        prepared_options['hmac_secret'] = b64encode(
            hmac_secret).decode('utf-8')

        # The temp options file is deleted by ycmd during startup
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as options_file:
            json.dump(prepared_options, options_file)
            options_file.flush()
            server_port = GetUnusedLocalhostPort()
            ycmd_args = [convertPathToMSYS(get_python_path()),
                         convertPathToMSYS(Settings.getYcmdPath()),
                         '--port={0}'.format(server_port),
                         '--options_file={0}'.format(convertPathToMSYS(options_file.name)),
                         '--idle_suicide_seconds={0}'.format(
                             SERVER_IDLE_SUICIDE_SECONDS)]

            if Settings.getMSYSPRECommand() != "":
                ycmd_args = [Settings.getMSYSPRECommand()] + ycmd_args


            std_handles = None if INCLUDE_YCMD_OUTPUT else subprocess.PIPE
            printd("Run command: " + str(ycmd_args))
            child_handle = subprocess.Popen(ycmd_args,
                                            stdout=std_handles,
                                            stderr=std_handles)
            return cls(child_handle, server_port, hmac_secret)

    def IsAlive(self):
        returncode = self._popen_handle.poll()
        # When the process hasn't finished yet, poll() returns None.
        return returncode is None

    def IsReady(self, include_subservers=False):
        try:
            if not self.IsAlive():
                return False
        except:
            return False
        params = {'include_subservers': 1} if include_subservers else None
        resp = self.GetFromHandler('ready', params)
        return resp == 'true'

    def Shutdown(self):
        if self.IsAlive():
            self._popen_handle.terminate()

    def PostToHandler(self, handler, data):
        return self._CallHttp('post', handler, data)

    def GetFromHandler(self, handler, params=None):
        if isinstance(params, collections.Mapping):
            params = urlencode(params)
            return self._CallHttp('get', '%s?%s' % (handler, params))
        else:
            return self._CallHttp('get', handler)

    def SendDefinedSubcommandsRequest(self, completer_target):
        request_json = BuildRequestData(completer_target=completer_target)
        return self.PostToHandler(DEFINED_SUBCOMMANDS_HANDLER, request_json)

    def SendCodeCompletionRequest(self,
                                  filepath,
                                  contents,
                                  filetype,
                                  line_num,
                                  column_num):
        request_json = BuildRequestData(filepath=filepath,
                                        contents=contents,
                                        filetype=filetype,
                                        line_num=line_num,
                                        column_num=column_num)
        return self.PostToHandler(CODE_COMPLETIONS_HANDLER, request_json)

    def SendGoToRequest(self,
                        filepath,
                        contents,
                        filetype,
                        line_num,
                        column_num):
        request_json = BuildRequestData(filepath=filepath,
                                        contents=contents,
                                        command_arguments=['GoTo'],
                                        filetype=filetype,
                                        line_num=line_num,
                                        column_num=column_num)
        return self.PostToHandler(COMPLETER_COMMANDS_HANDLER, request_json)

    def SendRequest(self,
                        filepath,
                        contents,
                        filetype,
                        line_num,
                        column_num, 
                        reqcommand):
        request_json = BuildRequestData(filepath=filepath,
                                        contents=contents,
                                        command_arguments=[reqcommand],
                                        filetype=filetype,
                                        line_num=line_num,
                                        column_num=column_num)
        return self.PostToHandler(COMPLETER_COMMANDS_HANDLER, request_json)

  

    def SendEventNotification(self,
                              event_name,
                              filepath,
                              contents,
                              filetype,
                              line_num=1,  # just placeholder values
                              column_num=1,
                              extra_data=None):
        request_json = BuildRequestData(filepath=filepath,
                                        contents=contents,
                                        filetype=filetype,
                                        line_num=line_num,
                                        column_num=column_num)
        if extra_data:
            request_json.update(extra_data)
        request_json['event_name'] = event_name
        return self.PostToHandler(EVENT_HANDLER, request_json)

    def LoadExtraConfFile(self, extra_conf_path):
        request_json = {
            'filepath': extra_conf_path}
        return self.PostToHandler(EXTRA_CONF_HANDLER, request_json)

    def WaitUntilReady(self, include_subservers=False):
        total_slept = 0
        time.sleep(0.5)
        total_slept += 0.5
        while total_slept < MAX_SERVER_WAIT_TIME_SECONDS:
            printd("trying to connect")
            try:
                if self.IsReady(include_subservers):
                    return
            except urllib.error.URLError as err:
                print('[Cppinabox] URLError Reason: ' + str(err.reason))
            except:
                printd("[Cppinabox] Exception in WaitUntilReady: " + traceback.format_exc())
            finally:
                time.sleep(0.2)
                total_slept += 0.2
        raise RuntimeError('waited for the server for {0} seconds, aborting'.format(MAX_SERVER_WAIT_TIME_SECONDS))

    def _BuildUri(self, handler):
        return urljoin(self._server_location, handler)

    def _CallHttp(self, method, handler, data=''):
        method = method.upper()
        req = Request(self._BuildUri(handler), method=method)
        if isinstance(data, collections.Mapping):
            req.add_header('content-type', 'application/json')
            data = json.dumps(data, ensure_ascii=False)
        data = data.encode('utf-8')
        request_hmac = self._HmacForBody(b''.join([
            self._HmacForBody(method.encode('utf-8')),
            self._HmacForBody(urljoin('/', handler).encode('utf-8')),
            self._HmacForBody(data),
        ]), to_base64=True)
        req.add_header(HMAC_HEADER, request_hmac)

        req.data = data
        try:
            resp = self.proxyLessUrlOpen.open(req)
        except HTTPError as err:
            print('[Cppinabox] HTTP Error ' + str( err.code ) )
            try:
                readData = err.read().decode('utf-8')
                print('                   Error from ycmd server: {}'.format(
                    json.loads(readData).get('message', '')))
            except:
                pass
                    
            return ''

        readData = resp.read()
        self._ValidateResponseObject(
            readData, resp.getheader(HMAC_HEADER).encode('utf-8'))

        return readData.decode('utf-8')

    def _HmacForBody(self, request_body, to_base64=False):
        '''
        @return bytes
        bytes request_body
        bool to_base64
        '''
        ret = CreateHexHmac(request_body, self._hmac_secret)
        return b64encode(ret) if to_base64 else ret

    def _ValidateResponseObject(self, content, hmac_header):
        '''
        @return bool
        bytes content
        bytes hmac_header
        '''
        if not ContentHexHmacValid(content, self._hmac_secret, b64decode(hmac_header)):
            raise RuntimeError('Received invalid HMAC for response!')
        return True


def CreateHexHmac(content, hmac_secret):
    '''
    @return bytes
    bytes content
    bytes hmac_secret
    '''
    # Must ensure that hmac_secret is bytes and not unicode
    return hmac.new(hmac_secret,
                    msg=content,
                    digestmod=hashlib.sha256).digest()


def ContentHexHmacValid(content, hmac_secret, hmac_str):
    '''
    @return bool
    bytes content
    bytes hmac_secret
    bytes hmac_str
    '''
    return hmac.compare_digest(CreateHexHmac(content, hmac_secret), hmac_str)


def DefaultSettings():
    # default_options_path = os.path.join(Settings.getYcmdPath(),
    #                                     'default_settings.json')
    # with open(default_options_path, 'rb') as f:
    #     return json.loads(f.read().decode('utf-8'))
    return dict(default_data_json)

def GetUnusedLocalhostPort():
    sock = socket.socket()
    # This tells the OS to give us any free port in the range [1024 - 65535]
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def BuildRequestData(filepath=None,
                     contents=None,
                     filetype=None,
                     line_num=None,
                     column_num=None,
                     command_arguments=None,
                     completer_target=None):
    # Normally, this would be the contents of the file as loaded in the editor
    # (possibly unsaved data).
    data = {
        'line_num': line_num,
        'column_num': column_num,
        'filepath': filepath or '',
        'file_data': {
            filepath: {
                'filetypes': [filetype],
                'contents': contents or ''
            }
        }
    }

    if command_arguments:
        data['command_arguments'] = command_arguments
    if completer_target:
        data['completer_target'] = completer_target

    return data


def CppSemanticCompletionResults(server):
    # TODO: document this better
    server.LoadExtraConfFile()

    # NOTE: The server will return diagnostic information about an error in the
    # some_cpp.cpp file that we placed there intentionally (as an example).
    # Clang will recover from this error and still manage to parse the file
    # though.
    server.SendEventNotification(event_name=Event.FileReadyToParse,
                                 filepath='some_cpp.cpp',
                                 filetype='cpp')

    server.SendCodeCompletionRequest(filepath='some_cpp.cpp',
                                     filetype='cpp',
                                     line_num=25,
                                     column_num=7)


def CppGotoDeclaration(server):
    # NOTE: No need to load extra conf file or send FileReadyToParse event, it was
    # already done in CppSemanticCompletionResults.

    server.SendGoToRequest(filepath='some_cpp.cpp',
                           filetype='cpp',
                           line_num=23,
                           column_num=4)



default_data_json = {
  "filepath_completion_use_working_dir": 0,
  "auto_trigger": 1,
  "min_num_of_chars_for_completion": 2,
  "min_num_identifier_candidate_chars": 0,
  "semantic_triggers": {},
  "filetype_specific_completion_to_disable": {
    "gitcommit": 1
  },
  "seed_identifiers_with_syntax": 0,
  "collect_identifiers_from_comments_and_strings": 0,
  "collect_identifiers_from_tags_files": 0,
  "max_num_identifier_candidates": 10,
  "extra_conf_globlist": [],
  "global_ycm_extra_conf": "",
  "confirm_extra_conf": 1,
  "complete_in_comments": 0,
  "complete_in_strings": 1,
  "max_diagnostics_to_display": 30,
  "filetype_whitelist": {
    "*": 1
  },
  "filetype_blacklist": {
    "tagbar": 1,
    "qf": 1,
    "notes": 1,
    "markdown": 1,
    "unite": 1,
    "text": 1,
    "vimwiki": 1,
    "pandoc": 1,
    "infolog": 1,
    "mail": 1
  },
  "auto_start_csharp_server": 1,
  "auto_stop_csharp_server": 1,
  "use_ultisnips_completer": 1,
  "csharp_server_port": 0,
  "hmac_secret": "",
  "server_keep_logfiles": 0,
  "gocode_binary_path": ""
}
