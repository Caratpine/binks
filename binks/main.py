# coding=utf-8

from flask import Flask

from server import Server
from loop import SelectLoop
from utils import logger


app = Flask(__name__)


@app.route('/')
def index():
    return 'hello world'


def main():
    logger.info('start...')
    loop = SelectLoop()
    server = Server(('0.0.0.0', 8484), loop=loop, app=app)
    server.listen()
    loop.run()


if __name__ == '__main__':
    main()
