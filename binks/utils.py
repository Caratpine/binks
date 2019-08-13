# coding=utf-8

import sys
import logging

logger = logging.getLogger('Binks')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)s:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
