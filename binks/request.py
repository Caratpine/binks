# coding=utf-8

import werkzeug_raw


class Request(object):
    def __init__(self, buffers):
        self._buffers = buffers
        self.response_status = ''
        self.response_headers = {}

    @property
    def environs(self):
        return werkzeug_raw.environ(self._buffers)

    def start_response(self, status, response):
        self.response_status = status
