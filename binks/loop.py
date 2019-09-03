# coding=utf -8

import select
from typing import Callable
from collections import defaultdict

from binks.utils import logger

MODE_NULL = 0x00
MODE_IN = 0x01
MODE_OUT = 0x04
MODE_ERR = 0x08
MODE_HUP = 0x10
MODE_NVAL = 0x20


class BaseLoop(object):
    def __init__(self):
        self._fds_to_handlers = defaultdict(list)

    def poll(self, timeout):
        raise NotImplementedError()

    def register(self, fd: int, mode: int):
        raise NotImplementedError()

    def unregister(self, fd: int):
        raise NotImplementedError()

    def modify(self, fd: int, mode: int):
        raise NotImplementedError()

    def add_callback(self, fd: int, mode: int, callback: Callable) -> None:
        handlers = self._fds_to_handlers[fd]
        handlers.append((mode, callback))
        self.register(fd, mode)

    def remove_callback(self, fd: int, mode: int, callback: Callable) -> None:
        handlers = self._fds_to_handlers[fd]
        handlers.remove((mode, callback))
        if len(handlers) == 0:
            logger.debug(f'remove fd: {fd}')
            self.unregister(fd)

    def run(self):
        while True:
            fds_ready = self.poll(1)
            logger.debug(f'fds_ready: {fds_ready}')
            for fd, mode in fds_ready:
                handlers = self._fds_to_handlers[fd]
                for m, callback in handlers:
                    if m & mode != 0:
                        callback()


class SelectLoop(BaseLoop):
    def __init__(self):
        super(SelectLoop, self).__init__()
        self._r_list = set()
        self._w_list = set()
        self._e_list = set()

    def poll(self, timeout: int = 0):
        r, w, e = select.select(self._r_list, self._w_list, self._e_list)
        results = defaultdict(lambda: MODE_NULL)
        for fds, mode in [(r, MODE_IN), (w, MODE_OUT), (e, MODE_ERR)]:
            for fd in fds:
                results[fd] |= mode
        return results.items()

    def register(self, fd: int, mode: int) -> None:
        if mode & MODE_IN:
            self._r_list.add(fd)
        if mode & MODE_OUT:
            self._w_list.add(fd)
        if mode & MODE_ERR:
            self._e_list.add(fd)

    def unregister(self, fd: int) -> None:
        if fd in self._r_list:
            self._r_list.remove(fd)
        if fd in self._w_list:
            self._w_list.remove(fd)
        if fd in self._e_list:
            self._e_list.remove(fd)

    def modify(self, fd: int, mode: int) -> None:
        self.unregister(fd)
        self.register(fd, mode)


class EpollLoop(BaseLoop):
    def __init__(self):
        super(EpollLoop, self).__init__()
        if hasattr(select, 'epoll'):
            self._epoll = select.epoll(flag=select.EPOLLIN | select.EPOLLET)  #: ET
        else:
            raise AttributeError('module "select" has no attribute "epoll"')

    def poll(self, timeout):
        return self._epoll.poll(timeout)

    def register(self, fd: int, mode: int):
        self._epoll.register(fd, mode)

    def unregister(self, fd: int):
        self._epoll.unregister(fd)

    def modify(self, fd: int, mode: int):
        self._epoll.modify(fd, mode)


if hasattr(select, 'epoll'):
    EventLoop = EpollLoop
else:
    EventLoop = SelectLoop
