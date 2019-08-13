# coding=utf-8

import socket

from client import Client
from utils import logger
from loop import (
    BaseLoop,
    MODE_IN,
)


class Server(object):
    def __init__(self, address: tuple, loop: BaseLoop = None, app=None):
        self._loop = loop
        self._address = address
        self._app = app

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(False)
        self._socket.bind(address)

    def listen(self, backlog: int = 128):
        self._loop.add_callback(self._socket.fileno(), MODE_IN, self.accept_callback)
        self._socket.listen(backlog)
        logger.info(f'Listening {self._address}...')

    def accept_callback(self):
        client_socket, addr = self._socket.accept()
        logger.debug(f'client socket: {client_socket.fileno()} {addr}')
        client = Client(client_socket, loop=self._loop, app=self._app)
        self._loop.add_callback(client.fd, MODE_IN, client.read_callback)
