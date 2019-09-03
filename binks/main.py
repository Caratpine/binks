# coding=utf-8

import os
import sys
import argparse

from binks.server import Server
from binks.utils import import_app


def command():
    parser = argparse.ArgumentParser(description='hello world')
    parser.add_argument('--host', default='127.0.0.1', help='Host to listen on.')
    parser.add_argument('--port', '-p', default=8080, type=int, help='Port to listen on.')
    parser.add_argument('--workers', '-w', default=5, type=int, help='Number of workers to spawn.')
    parser.add_argument('--app', dest='module', required=True, help='Web application')
    return parser


def main():
    parser = command()
    args = parser.parse_args()
    sys.path.insert(0, os.getcwd())
    app = import_app(args.module)
    server = Server((args.host, args.port), app=app, worker_num=args.workers)
    server.run()


if __name__ == '__main__':
    main()
