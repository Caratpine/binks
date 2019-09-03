# coding=utf-8

import os
import sys
import errno
import signal
from socket import socket

from binks.utils import logger, SIGNALS
from binks.loop import (
    BaseLoop,
    EventLoop,
    MODE_IN,
    MODE_OUT
)
from binks.request import Request
from binks.response import Response

BUF_SIZE = 4096


class Client(object):
    def __init__(self, sock: socket, loop: BaseLoop = None, app=None):
        self._socket = sock
        self.fd = sock.fileno()
        self.loop = loop
        self.app = app
        self.request: Request = None
        self.response: Response = None
        self._socket.setblocking(False)

    def read_callback(self) -> None:
        logger.debug(f'read fd: {self.fd}, pid: {os.getpid()}')
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
        logger.debug(f'write fd: {self.fd}, pid: {os.getpid()}')
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
        response_list = self.app(self.request.environs, self.request.start_response)
        self.response = Response(response_list, request=self.request)
        self.write()

    def __repr__(self):
        return f'<Client fd:{self.fd}>'


class Worker(object):
    def __init__(self, sock: socket, app=None):
        self._socket = sock
        self.app = app
        self.loop = EventLoop()
        self.register_signals()

    def register_signals(self):
        signal.signal(signal.SIGQUIT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def handle_exit(self, signum, frame):
        pid = os.getpid()
        logger.info(f'Worker {pid} receive {SIGNALS[signum]}, exit...')
        sys.exit(0)

    def accept_callback(self):
        try:
            client_socket, addr = self._socket.accept()
            logger.debug(f'client socket: {client_socket.fileno()} {addr}')
            client = Client(client_socket, loop=self.loop, app=self.app)
            self.loop.add_callback(client.fd, MODE_IN, client.read_callback)
            logger.debug(f'Server loop : {self.loop._fds_to_handlers}')
        except BlockingIOError as e:
            logger.debug(f'blocking error {e}')

    def run(self):
        self.loop.add_callback(self._socket.fileno(), MODE_IN, self.accept_callback)
        try:
            self.loop.run()
        except SystemExit:
            return
        except Exception:
            raise
