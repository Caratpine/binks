# coding=utf-8

import sys
import signal
import logging
import importlib

from typing import Callable

logger = logging.getLogger('Binks')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] pid: %(process)d %(levelname)s:%(filename)s:%(lineno)s:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


SIGNALS = {
    signal.SIGINT: 'SIGINT',
    signal.SIGTERM: 'SIGTERM',
    signal.SIGQUIT: 'SIGQUIT',
    signal.SIGCHLD: 'SIGCHLD',
    signal.SIGUSR1: 'SIGUSR1'
}


def import_app(module: str) -> Callable:
    module_name, app_name = module.rsplit(':')
    module = importlib.import_module(module_name)
    try:
        obj = getattr(module, app_name)
    except AttributeError:
        raise ImportError(f'Failed to find application object: {app_name}.')
    if not callable(obj):
        raise TypeError('Application object must be callable.')
    return obj
