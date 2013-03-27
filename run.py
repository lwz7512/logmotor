# -*- coding: utf-8 -*-
__author__ = 'lwz'

import sys
import os
import time
import logging
import ConfigParser
from socket import socket

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pygtail import Pygtail

from socketIO_client import SocketIO, BaseNamespace


# init in main
configObj = None

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 8000
NAME_SPACE = '/simplepush'


class TailContentHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self):
        pass

    def on_moved(self, event):
        super(TailContentHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        super(TailContentHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(TailContentHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(TailContentHandler, self).on_modified(event)

        # what = 'directory' if event.is_directory else 'file'
        # logging.info("Modified %s: %s", what, event.src_path)
        # split_path = None
        if sys.platform == "win32":
            split_path = "\\"
        else:
            split_path = "/"
        log_file = event.src_path.split(split_path)
        # get offset storage directory from config...
        offset_dir = configObj.get('local', 'cursor_dir')
        # prepare offset file directory
        if not os.path.exists(offset_dir):
            os.makedirs(offset_dir)
        offset_file = "%s/%s.os" % (offset_dir, log_file[-1])
        # offset file must separate with monitor directory, and is local variable...
        tailor = Pygtail(event.src_path, offset_file, paranoid=True)
        # must use gbk encoding...
        appended = tailor.read()
        if appended:
            decodeLog = appended.decode("gbk")
            logging.info("sending: %s", decodeLog)
            # sending to server...
            send_log_to_server(decodeLog)
        else:
            logging.info("empty content: %s", event.src_path)


# send metric to graphite...
# 2013/02/01
def send_metrix_to_server(log):
    message = create_alert(log)
    sock = socket()
    try:
        sock.connect((SERVER_ADDRESS, SERVER_PORT))
    except BaseException:
        print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" \
              % {'server': SERVER_ADDRESS, 'port': SERVER_PORT}
        return
    sock.sendall(message)
    sock.close()


# send log raw text to django-socketio server...
# 2013/03/25
def send_log_to_server(log):
    mainSocket = SocketIO(SERVER_ADDRESS, SERVER_PORT, BaseNamespace)
    newsSocket = mainSocket.connect(NAME_SPACE, BaseNamespace)
    newsSocket.message(log)
    # newsSocket.emit('event name', {'message': log})


# TODO, create metric by log string...
# use parser in config file to parse line...
def create_metric(log):
    return log


# TODO, create alert message(json string) by log string...
# use parser in config file to parse line...
def create_alert(line):
    return  line


# ------------- main entrance -------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    localDir = os.path.dirname(__file__)
    srvConf = os.path.join(localDir, 'server.conf')

    configObj = ConfigParser.ConfigParser()
    configObj.read(srvConf)

    path = configObj.get("local", "log_dir")
    logging.debug("monitoring dir: %s", path)

    SERVER_ADDRESS = configObj.get("remote", "ip")
    SERVER_PORT = int(configObj.get("remote", "port"))
    NAME_SPACE = configObj.get("remote", "namespace")
    logging.debug('prepare to send log to: %s:%d' % (SERVER_ADDRESS, SERVER_PORT))

    # TODO, Load log parser class in conf...

    event_handler = TailContentHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()