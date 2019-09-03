# coding=utf-8

from typing import List

from binks.request import Request
from binks.utils import logger


class Response(object):
    def __init__(self, response_list: List = None, request: Request = None):
        self.response_list = response_list
        self.response_headers: dict = request.response_headers or {}
        self.status = request.response_status

    @property
    def buffers(self) -> bytes:
        resp_list = list()
        resp_list.append(f'HTTP/1.1 {self.status}\r\n'.encode('utf-8'))
        resp_list.append(f'Server: Binks\r\n'.encode('utf-8'))
        resp_list.append('Connection: close\r\n'.encode('utf-8'))
        for key, value in self.response_headers.items():
            resp_list.append(f'{key}: {value}\r\n'.encode('utf-8'))
        resp_list.append('\r\n'.encode('utf-8'))
        for body in self.response_list:
            resp_list.append(body)
        logger.debug(resp_list)
        return b''.join(resp_list)
