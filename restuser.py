"""Simple REST service for creating users with useradd"""

from __future__ import print_function

import json
import os
import sys
from pwd import getpwnam
from subprocess import Popen, PIPE

from tornado import gen, web
from tornado.log import app_log
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.netutil import bind_unix_socket
from tornado.options import define, parse_command_line, options

class UserHandler(web.RequestHandler):
    
    def get_user(self, name):
        """Get a user struct by name, None if no such user"""
        try:
            return getpwnam(name)
        except KeyError:
            return None
    
    def write_error(self, status_code, **kwargs):
        """Simple (not html) errors"""
        exc = kwargs['exc_info'][1]
        self.write(exc.log_message or str(error))

    def get(self, name):
        obj = self.get_user(name)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({
            'username': obj.pw_name,
            'uid': obj.pw_uid,
            'gid': obj.pw_gid
        })+ "\n")


def main():
    define('ip', default=None, help='IP to listen on')
    define('port', default=None, help='port to listen on')
    define('socket', default=None, help='unix socket path to bind (instead of ip:port)')
    
    parse_command_line()
    
    if not options.socket and not (options.port):
        options.socket = '/var/run/restuser.sock'
    
    app = web.Application([(r'/([^/]+)', UserHandler)])
    if options.socket:
        socket = bind_unix_socket(options.socket, mode=0o600)
        server = HTTPServer(app)
        server.add_socket(socket)
    else:
        app.listen(options.port, options.ip)
    try:
        IOLoop.current().start()
    except KeyboardInterrupt:
        print("\ninterrupted\n", file=sys.stderr)
        return


if __name__ == '__main__':
    main()
