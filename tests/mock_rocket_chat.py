#!/usr/bin/env python3

"""Module contains implementation of Rocket.Chat mock server for tests. """

import argparse
import json
import re
import socket
import subprocess
import sys
import time
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
from os.path import abspath, dirname, join

from tests.exceptions import MockServerFailed
from tests.server_responses import *


class MockRocketChat(BaseHTTPRequestHandler):
    """Mock Rocket.Chat server for tests. """

    def _check_endpoint(self, endpoint):
        """Check if endpoint is available for request to mock server. """

        if re.match(f'^{endpoint}', self.path):
            return True

        return False

    def _send_headers(self):
        """Add headers to request body. """

        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _send_response(self, response, status_code=200):
        """Responds to requests for server. """

        self.send_response(status_code)
        self._send_headers()
        self.wfile.write(json.dumps(response, indent=4).encode(encoding='utf_8'))

    def do_GET(self):  # pylint: disable=invalid-name
        """Handles GET requests to mock web server. """

        endpoints = {
            '/groups.members/': lambda: self._send_response(GROUPS_MEMBERS_GET_SUCCESS_RESPONSE),
            '/hello/': lambda: self._send_response({'Hello': 'World!'}),
            '/rooms.get/': lambda: self._send_response(ROOMS_GET_SUCCESS_RESPONSE),
            '/users.info/': lambda: self._send_response(USER_INFO_GET_SUCCESS_RESPONSE),
            '/users.list/': lambda: self._send_response(USERS_LIST_GET_SUCCESS_RESPONSE),
            '/users.list_without_permissons/': lambda: self._send_response(
                USERS_LIST_GET_SUCCESS_RESPONSE_WITHOUT_BOT_PERMISSIONS,
            ),
            '/users.list_500/': lambda: self._send_response(
                INTERNAL_SERVER_ERROR_RESPONSE,
                status_code=500,
            ),
        }

        for endpoint, process_request in endpoints.items():
            if self._check_endpoint(endpoint):
                process_request()
                return

        self.send_response(404)
        self._send_headers()

    def do_POST(self):  # pylint: disable=invalid-name
        """Handles POST requests to mock web server. """

        endpoints = {
            '/chat.postMessage/': lambda: self._send_response(CHAT_POST_MESSAGE_SUCCESS_RESPONSE),
            '/chat.react/': lambda: self._send_response(CHAT_REACT_POST_SUCCESS_RESPONSE),
            '/groups.create/': lambda: self._send_response(GROUPS_CREATE_POST_SUCCESS_RESPONSE),
            '/groups.delete/': lambda: self._send_response(GROUPS_DELETE_POST_SUCCESS_RESPONSE),
            '/groups.invite/': lambda: self._send_response(GROUPS_INVITE_POST_SUCCESS_RESPONSE),
        }

        for endpoint, process_request in endpoints.items():
            if self._check_endpoint(endpoint):
                process_request()
                return

        self.send_response(404)
        self._send_headers()


def main():
    """Entry point. """

    parser = argparse.ArgumentParser(description='Mock server Rocket.Chat')
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        help='port that mock web server will listen on',
    )
    args = parser.parse_args()

    hostname = 'localhost'
    server = HTTPServer((hostname, args.port), MockRocketChat)
    sys.stderr.write(f'The server is available at http://{hostname}:{args.port}\n')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    sys.stderr.write('Server stopped\n')


def _allocate_port():
    """Allocates free port. """

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(('', 0))

        return sock.getsockname()[1]


def run_mock_server():
    """Starts Rocket.Chat mock server and returns its process and address,
    on which server running.
    """

    port = _allocate_port()
    base_dir = dirname(abspath(__file__))
    proc = subprocess.Popen([  # pylint: disable=consider-using-with
        join(base_dir, 'mock_rocket_chat.py'),
        str(port),
    ])

    # Waiting for the server to start
    for _ in range(60):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            res = sock.connect_ex(('127.0.0.1', port))
            if res == 0:
                break

        time.sleep(1)
    else:
        raise MockServerFailed('Failed to start mock server Rocket.Chat')

    return f'http://localhost:{port}', proc


if __name__ == '__main__':
    main()
