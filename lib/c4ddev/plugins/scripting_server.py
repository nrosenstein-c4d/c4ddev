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
#                      Shared Code (SocketFile wrapper class)
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
#                    Request Handling and Server thread
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import sys, os, codecs, socket, hashlib, threading

class SourceObject(object):
    """
    Represents source-code sent over from another machine or
    process which can be executed later.
    """

    def __init__(self, addr, filename, source, origin):
        super(SourceObject, self).__init__()
        self.host, self.port = addr
        self.filename = filename
        self.source = source
        self.origin = origin

    def __repr__(self):
        return '<SourceObject "{0}" sent from "{1}" @ {2}:{3}>'.format(
            self.filename, self.origin, self.host, self.port)

    def execute(self, scope):
        """
        Execute the source in the specified scope.
        """

        scope['__file__'] = self.filename
        dirname = os.path.dirname(self.filename)
        code = compile(self.source, self.filename, 'exec')
        exec code in scope

def parse_headers(fp):
    """
    Parses HTTP-like headers into a dictionary until an empty line
    is found. Invalid headers are ignored and if a header is found
    twice, it won't overwrite its previous value. Header-keys are
    converted to lower-case and stripped of whitespace at both ends.
    """

    headers = {}
    while True:
        line = fp.readline().strip()
        if not line: break

        key, _, value = line.partition(':')
        key = key.rstrip().lower()
        if key not in headers:
            headers[key] = value.lstrip()

    return headers

def parse_request(conn, addr, required_password):
    """
    Communicates with the client parsing the headers and source
    code that is to be queued to be executed any time soon.

    Writes on of these lines back to the client:

    - status: invalid-password
    - status: invalid-request
    - status: encoding-error
    - status: ok

    :pass conn: The socket to the client.
    :pass addr: The client address tuple.
    :pass required_password: The password that must match the
        password sent with the "Password" header (as encoded
        utf8 converted to md5). Will be converted to md5 by
        this function.
    :return: :class:`SourceObject` or None
    """

    client = SocketFile(conn, encoding='utf8')
    headers = parse_headers(client)

    # Get the password and validate it.
    if required_password is not None:
        passhash = hashlib.md5(required_password.encode('utf8')).hexdigest()
        if passhash != headers['password']:
            client.write('status: invalid-password')
            return None

    # Get the content-length of the request.
    content_length = headers.get('content-length', None)
    if content_length is None:
        client.write('status: invalid-request')
        return None
    try:
        content_length = int(content_length)
    except ValueError as exc:
        client.write('status: invalid-request')
        return None

    # Get the encoding, default to binary.
    encoding = headers.get('encoding', None)
    if encoding is None:
        encoding = 'binary'
    else:
        # default to binary if the encoding does not exist.
        try: codecs.lookup(encoding)
        except LookupError as exc:
            encoding = 'binary'

    # Get the filename, origin and source code.
    origin = headers.get('origin', 'unknown')
    filename = headers.get('filename', 'untitled')
    try:
        source = client.read(content_length)
        if encoding != 'binary':
            source = source.decode(encoding)
    except UnicodeDecodeError as exc:
        client.write('status: encoding-error')
        return None

    client.write('status: ok')
    return SourceObject(addr, filename, source, origin)

class ServerThread(threading.Thread):
    """
    When the thread is started, the thread binds a server to the
    specified host and port accepting incoming source code, optionally
    password protected, and appends it to the specified queue. A lock
    for synchronization must be passed along with the queue.
    """

    def __init__(self, queue, queue_lock, host, port, password=None):
        super(ServerThread, self).__init__()
        self._queue = queue
        self._queue_lock = queue_lock
        self._socket = None
        self._addr = (host, port)
        self._running = False
        self._lock = threading.Lock()
        self._password = password

    @property
    def running(self):
        with self._lock:
            return self._running

    @running.setter
    def running(self, value):
        with self._lock:
            self._running = value

    def run(self):
        try:
            while self.running:
                source = self.handle_request()
                if source:
                    with self._queue_lock:
                        self._queue.append(source)
        finally:
            self._socket.close()

    def start(self):
        self._socket = socket.socket()
        self._socket.bind(self._addr)
        self._socket.listen(5)
        self._socket.settimeout(0.5)
        self.running = True
        return super(ServerThread, self).start()

    def handle_request(self):
        conn = None
        try:
            conn, addr = self._socket.accept()
            source = parse_request(conn, addr, self._password)
            return source
        except socket.timeout:
            return None
        finally:
            if conn:
                conn.close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Cinema 4D integration
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import c4d, collections, traceback

class Server(c4d.plugins.MessageData):

    PLUGIN_ID = 1033731
    PLUGIN_NAME = "C4DDev Scripting Server"

    def __init__(self, host='localhost', port=2900, password='alpine'):
        super(Server, self).__init__()
        self.queue = collections.deque()
        self.queue_lock = threading.Lock()
        self.host = host
        self.port = port
        self.password = password
        self.thread = None

    def register(self):
        return c4d.plugins.RegisterMessagePlugin(
            self.PLUGIN_ID, self.PLUGIN_NAME, 0, self)

    @property
    def running(self):
        if self.thread:
            return self.thread.is_alive()
        return False

    def start(self):
        if self.running:
            raise RuntimeError("already running")
        print "Binding C4DDev Scripting Server to {0}:{1} ...".format(self.host, self.port)
        self.thread = ServerThread(self.queue, self.queue_lock, self.host,
                self.port, self.password)
        try:
            self.thread.start()
        except socket.error as exc:
            print "Failed to bind to {0}:{1}".format(host, port)
            self.thread = None

    def stop(self):
        if not self.running:
            raise RuntimeError("not running")
        print "Shutting down C4DDev Scripting Server thread ..."
        self.thread.running = False
        self.thread.join()
        self.thread = None

    def get_scope(self):
        doc = c4d.documents.GetActiveDocument()
        op = doc.GetActiveObject()
        mat = doc.GetActiveMaterial()
        return {'__name__': '__main__', 'doc': doc, 'op': op, 'mat': mat}

    def on_shutdown(self):
        if self.thread and self.running:
            self.stop()

    def GetTimer(self):
        if self.thread:
            return 500
        return 0

    def CoreMessage(self, kind, bc):
        # Execute source code objects while they're available.
        while True:
            with self.queue_lock:
                if not self.queue: break
                source = self.queue.popleft()
            try:
                # For more verbose printing replace next line with: "ScriptServer: running", source
                print "C4DDev Scripting Server: running"
                scope = self.get_scope()
                source.execute(scope)
            except Exception as exc:
                traceback.print_exc()
        return True

class ServerToggle(c4d.plugins.CommandData):

    def __init__(self, server):
        super(ServerToggle, self).__init__()
        self.server = server

    def register(self):
        info = c4d.PLUGINFLAG_HIDEPLUGINMENU
        icon = None
        help = "Enables/disables the C4DDev Scripting Server"
        c4d.plugins.RegisterCommandPlugin(
            1039246, "Scripting Server", info, icon, help, self)

    def Execute(self, doc):
        if self.server.running:
            self.server.stop()
        else:
            self.server.start()
        return True

    def GetState(self, doc):
        flags = c4d.CMD_ENABLED
        if self.server.running:
            flags |= c4d.CMD_VALUE
        return flags

server = Server()
server.register()
ServerToggle(server).register()

def PluginMessage(kind, data):
    if kind in [c4d.C4DPL_ENDACTIVITY, c4d.C4DPL_RELOADPYTHONPLUGINS]:
        if server.running:
            server.stop()
    return True
