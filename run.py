# -*- coding: utf-8 -*-
__author__ = 'lwz'

import os
import time
import logging
import ConfigParser

from watchdog.observers import Observer

# global dictionary to save the collector,parser,handler instance...
workers = None


def main():
    cfg = load_config()

    event_handlers = load_plugins(cfg)

    observer = Observer()
    # TODO, TO ADD MULTIPLE EVENT HANDLERS...
    # 2013/04/17
    observer.schedule(event_handlers[0], cfg['log_dir'], recursive=True)
    observer.start()

    logging.debug('log motor started...')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def load_config():
    localDir = os.path.dirname(__file__)
    srvConf = os.path.join(localDir, 'server.conf')

    configObj = ConfigParser.ConfigParser()
    configObj.read(srvConf)

    log_level = configObj.get('trace', 'level')
    if log_level == 'debug':
        level = logging.DEBUG
    else:
        level = logging.WARN
    logging.basicConfig(level=level, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    cfg = dict

    cfg['log_dir'] = configObj.get('local', 'log_dir')
    cfg['cursor_dir'] = configObj.get('local', 'cursor_dir')
    cfg['graphite_ip'] = configObj.get('graphite', 'ip')
    cfg['graphite_port'] = configObj.get('graphite', 'port')
    cfg['graphite_namespace'] = configObj.get('graphite', 'namespace')
    cfg['carbon_ip'] = configObj.get('carbon', 'ip')
    cfg['carbon_port'] = configObj.get('carbon', 'port')

    cfg['mapping'] = configObj.items('mapping')

    return cfg


def load_plugins(cfg):
    mappings = cfg['mapping']
    offset_dir = cfg['cursor_dir']

    # Figure out where we are and start looking for plugins
    current_file = os.path.abspath(__file__)
    current_directory = os.path.abspath(os.path.join(current_file, os.path.pardir))
    plugins_directory = current_directory + "/plugins"

    for key, value in mappings:
        cph = value.split(',')
        col_module = __import__('plugins.collectors.%s' % cph[0], globals(), locals(), [cph[0]])
        col_inst = getattr(col_module, cph[0])(offset_dir, on_logfile_change)
    #     TODO, IMPORT OTHER MODULE AND CREATE INSTANCE...LAST TO SAVE A TUPLE..

    return []


def on_logfile_change(logfile, line):
    pass


# ------------- main entrance -------------------------------
if __name__ == "__main__":
    main()