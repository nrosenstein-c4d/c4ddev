# -*- coding: utf8 -*-
#
# Copyright (C) 2014  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = 'Niklas Rosenstein <rosensteinniklas (at) gmail.com>'
__version__ = '1.0'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                    Shared Code (SocketFile wrapper class)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import sys
if sys.version_info[0] < 3:
    try: from cStringIO import StringIO as BytesIO
    except ImportError: from StringIO import StringIO as BytesIO
else:
    from io import BytesIO

class SocketFile(object):
    """
    File-like wrapper for reading socket objects.
    """

    def __init__(self, socket, encoding=None):
        super(SocketFile, self).__init__()
        self._socket = socket
        self._buffer = BytesIO()
        self.encoding = encoding

    def _append_buffer(self, data):
        pos = self._buffer.tell()
        self._buffer.seek(0, 2)
        self._buffer.write(data)
        self._buffer.seek(pos)

    def bind(self, *args, **kwargs):
        return self._socket.bind(*args, **kwargs)

    def connect(self, *args, **kwargs):
        return self._socket.connect(*args, **kwargs)

    def read(self, length, blocking=True):
        data = self._buffer.read(length)
        delta = length - len(data)
        if delta > 0:
            self._socket.setblocking(blocking)
            try:
                data += self._socket.recv(delta)
            except socket.error:
                pass
        return data

    def readline(self):
        parts = []
        while True:
            # Read the waiting data from the socket.
            data = self.read(1024, blocking=False)

            # If it contains a line-feed character, we add it
            # to the result list and append the rest of the data
            # to the buffer.
            if b'\n' in data:
                left, right = data.split(b'\n', 1)
                parts.append(left + b'\n')
                self._append_buffer(right)
                break

            else:
                if data:
                    parts.append(data)

                # Read a blocking byte for which we will get an empty
                # bytes object if the socket is closed-
                byte = self.read(1, blocking=True)
                if not byte:
                    break

                # Add the byte to the buffer. Stop here if it is a
                # newline character.
                parts.append(byte)
                if byte == b'\n':
                    break

        return b''.join(parts)

    def write(self, data):
        if isinstance(data, str):
            if not self.encoding:
                raise ValueError('got str object and no encoding specified')
            data = data.encode(self.encoding)

        return self._socket.send(data)

    def close(self):
        return self._socket.close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Communication with code reciever server
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import socket
import hashlib

def parse_credentials(creds):
    """
    Parses a credentials string. The first part is the password which
    is separated by a forward-slash to the host-name. The host-name is
    separated by a double-colon to the port-name.

    Returns a tuple of ``(password, host, port)``. A *ValueError* is
    raised if the format is invalid. The password is optional and
    None is returned if it is not specified.
    """

    password, _, creds = creds.rpartition('/')
    if not password:
        password = None

    host, _, creds = creds.rpartition(':')
    if not host:
        raise ValueError('no host')

    if not creds:
        raise ValueError('no port')
    try:
        port = int(creds)
    except ValueError:
        raise ValueError('invalid port')

    return (password, host, port)

def send_code(filename, code, encoding, password, host, port, origin):
    """
    Sends Python code to Cinema 4D running at the specified location
    using the supplied password.

    :raise ConnectionRefusedError:
    """

    client = SocketFile(socket.socket())
    client.connect((host, port)) #! ConnectionRefusedError

    if isinstance(code, str):
        code = code.encode(encoding)

    client.encoding = 'ascii'
    client.write("Content-length: {0}\n".format(len(code)))
    # The Python instance on the other end will check for a coding
    # declaration or otherwise raise a SyntaxError if an invalid
    # character was found.
    client.write("Encoding: binary\n")
    client.write("Filename: {0}\n".format(filename))
    client.write("Origin: {0}\n".format(origin))

    if password:
        passhash = hashlib.md5(password.encode('utf8')).hexdigest()
        client.write("Password: {0}\n".format(passhash))
    client.write('\n') # end headers

    client.encoding = None
    client.write(code)

    # Read the response from the server.
    result = client.readline().decode('ascii')
    client.close()

    status = result.partition(':')[2].strip()
    if status == 'ok':
        return None
    return status # error code

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                          Sublime Integration
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os, json
import traceback
import sublime, sublime_plugin
settings_filename = os.path.join(os.path.dirname(__file__), 'store.json')

def show_console():
    window = sublime.active_window()
    window.run_command('show_panel', {'panel': 'console'})

def default_settings():
    return {
        'credentials': 'alpine/localhost:2900',
        }

def load_settings():
    data = default_settings()

    try:
        with open(settings_filename) as fp:
            json_data = json.load(fp)
    except (IOError, ValueError) as exc:
        pass
    else:
        if isinstance(json_data, dict):
            data.update(json_data)

    return data

def save_settings():
    global settings
    try:
        with open(settings_filename, 'w') as fp:
            json.dump(settings, fp)
    except (IOError, OSError) as exc:
        print("RemoteCodeRunner: could not save settings")
        print(exc)
        print()
        show_console()

settings = load_settings()
assert isinstance(settings, dict)

class SetPythonCodeDestinationCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        credentials = settings['credentials']
        window = sublime.active_window()
        window.show_input_panel("Set Python Code send credentials:", credentials, self.on_done, None, None)

    def on_done(self, text):
        try:
            password, host, port = parse_credentials(text)
        except ValueError as exc:
            sublime.status_message('Credentials format is invalid, must be like "password/host:port"')
            return

        settings['credentials'] = text
        save_settings()
        sublime.status_message('Credentials saved.')

class SendPythonCodeCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        global settings
        credentials = settings['credentials']

        view = sublime.active_window().active_view()
        code = view.substr(sublime.Region(0, view.size()))
        filename = view.file_name() or 'untitled'
        encoding = view.encoding()
        if encoding == 'Undefined':
            encoding = 'UTF-8'

        try:
            password, host, port = parse_credentials(credentials)
        except ValueError as exc:
            sublime.status_message('Invalid credentials saved.')
            return

        try:
            error = send_code(filename, code, encoding, password, host, port, 'Sublime Text')
        except ConnectionRefusedError as exc:
            sublime.status_message('Could not connect to {0}:{1}'.format(host, port))
            return
        except socket.error as exc:
            sublime.status_message('socket.error occured, see console')
            show_console()
            traceback.print_exc()
            return

        if error == 'invalid-password':
            sublime.status_message('Password was not accepted by the Remote Code Executor Server at {0}:{1}'.format(host, port))
        elif error == 'invalid-request':
            sublime.status_message('Request was invalid, maybe this plugin is outdated?')
        elif error is not None:
            sublime.status_message('error (unexpected): {0}'.format(error))
        else:
            sublime.status_message('Code sent to {0}:{1}'.format(host, port))

