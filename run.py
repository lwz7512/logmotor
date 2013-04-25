# -*- coding: utf-8 -*-
__author__ = 'lwz'

import os
import time
import logging
import ConfigParser

from watchdog.observers import Observer
from plugins.base import LogMotorException

# global dictionary to save the collector,parser,handler instance...
workers = dict()


def main():
    print 'starting logmotor agent...'

    cfg = load_config()
    event_handlers = load_plugins(cfg)
    logging.debug('plugins initialized!')

    observer = Observer()
    # TODO, TO ADD MULTIPLE EVENT HANDLERS...
    # 2013/04/17
    observer.schedule(event_handlers[0], cfg['log_dir'], recursive=True)
    observer.start()
    logging.debug('log motor running...')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def load_config():
    localDir = os.path.dirname(__file__)
    srvConf = os.path.join(localDir, 'agent.conf')

    configObj = ConfigParser.ConfigParser()
    configObj.read(srvConf)

    log_level = configObj.get('trace', 'level')
    if log_level == 'debug':
        level = logging.DEBUG
    else:
        level = logging.WARN
    logging.basicConfig(level=level, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('agent config file loaded!')
    cfg = dict()

    cfg['local_ip'] = configObj.get('local', 'ip')
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
    # a parse principle list:
    # key: service.logtype
    # value: collector,parser,handler
    mappings = cfg['mapping']
    offset_dir = cfg['cursor_dir']
    host = cfg['local_ip']

    collectors = []

    for key, value in mappings:
        col_par_han = value.split(',')
        col_module = __import__('plugins.collectors.%s' % col_par_han[0], fromlist=[col_par_han[0]])
        col_inst = getattr(col_module, col_par_han[0])(offset_dir, on_logfile_changed)
        par_module = __import__('plugins.parsers.%s' % col_par_han[1], fromlist=[col_par_han[1]])
        par_inst = getattr(par_module, col_par_han[1])(host)
        han_module = __import__('plugins.handlers.%s' % col_par_han[2], fromlist=[col_par_han[2]])
        han_inst = getattr(han_module, col_par_han[2])(cfg)

        workers[key] = (col_inst, par_inst, han_inst)  # cache the parsers and handlers for later use...
        collectors.append(col_inst)
    # return event handlers for observer use...
    return collectors


def on_logfile_changed(logfile, lines):
    """
    callback method for collector, params delivered by collector.on_modified method

    :param logfile: the log file path, separated by /
    :param lines: the log file changed contents, if multi-line, separated by \n
    """
    file_matched = False
    for key, value in workers.iteritems():
        service_logfile = key.split('.')
        logfile_seg = logfile.split('/')
        # find the service name in log file directory, and find the log type in log file name...
        if service_logfile[0] in logfile_seg and service_logfile[1] in logfile_seg[-1]:
            file_matched = True
            logging.debug('processing line with: %s' % key)
            try:
                workers[key][1].parse_lines(lines)  # call parser method
                workers[key][2].handle(workers[key][1].get_states())  # call handler method use parser results
            except LogMotorException, e:
                logging.error('processing line error: %s' % e)
                break
            else:
                logging.debug('One line handled successfully using config of: %s' % key)
                break

    if file_matched is False:
        logging.warning('Not found the corresponding parser/handler for: %s' % logfile)


# ------------- main entrance -------------------------------
if __name__ == "__main__":
    main()