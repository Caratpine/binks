# coding=utf-8

import errno
from socket import socket

from utils import logger
from loop import (
    BaseLoop,
    MODE_IN,
    MODE_OUT
)
from request import Request
from response import Response

BUF_SIZE = 4096


class Client(object):
    def __init__(self, sock: socket, loop: BaseLoop = None, app=None):
        self._socket = sock
        self.fd = sock.fileno()
        self.loop = loop
        self._app = app
        self.request: Request = None
        self.response: Response = None
        self._socket.setblocking(False)

    def read_callback(self) -> None:
        logger.debug(f'read fd: {self.fd}')
        cache = []
        while True:
            try:
                data = self._socket.recv(BUF_SIZE)
                if not data:
                    break
                cache.append(data)
            except OSError as e:
                if e.args[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    break
                raise
        if cache:
            data = b''.join(cache)
            self.handle_request(data)
        self.loop.remove_callback(self.fd, MODE_IN, self.read_callback)

    def write(self) -> None:
        self.loop.add_callback(self.fd, MODE_OUT, self.write_callback)

    def write_callback(self) -> None:
        logger.debug(f'write fd: {self.fd}')
        buffers = self.response.buffers
        while len(buffers) > 0:
            try:
                bytes = self._socket.send(buffers)
                if bytes < len(buffers):
                    buffers = buffers[bytes:]
                    continue
                break
            except OSError as e:
                if e.args[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    break
                raise
        self.loop.remove_callback(self.fd, MODE_OUT, self.write_callback)
        self._socket.close()

    def handle_request(self, data: bytes) -> None:
        self.request = Request(data)
        response_list = self._app(self.request.environs, self.request.start_response)
        self.response = Response(response_list, request=self.request)
        self.write()

    def __repr__(self):
        return f'<Client fd:{self.fd}>'

