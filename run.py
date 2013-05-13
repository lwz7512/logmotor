# -*- coding: utf-8 -*-
__author__ = 'lwz'

import os
import time
import logging
import ConfigParser

from watchdog.observers import Observer
from plugins.base import LogMotorException
from plugins.collectors.TailContentCollector import TailContentCollector

# global dictionary to save the collector,parser,handler instance...
log_workers = dict()
pfm_workers = dict()


def main():
    print 'starting logmotor agent...'

    cfg = load_config()
    load_plugins(cfg)
    logging.debug('plugins initialized!')

    clear_offsets(cfg['cursor_dir'])
    event_handler = TailContentCollector(cfg['cursor_dir'], on_logfile_changed)

    observer = Observer()
    observer.schedule(event_handler, cfg['log_dir'], recursive=True)
    observer.start()
    logging.debug('log motor running...')
    try:
        while True:
            run_pfm_collect_minute()  # collect the performance every minute
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def clear_offsets(directory):
    os.chdir(directory)
    for f in os.listdir('.'):
        os.remove(f)


def load_config():
    localDir = os.path.dirname(__file__)
    srvConf = os.path.join(localDir, 'agent.conf')

    configObj = ConfigParser.ConfigParser()
    configObj.read(srvConf)

    log_level = configObj.get('trace', 'level')
    level_dict = {'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN, 'error': logging.ERROR}

    logging.basicConfig(level=level_dict[log_level], format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
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

    cfg['vislog'] = configObj.items('vislog')
    cfg['vispfm'] = configObj.items('vispfm')

    return cfg


def load_plugins(cfg):
    host = cfg['local_ip']
    vis_logs = cfg['vislog']
    vis_pfms = cfg['vispfm']

    for key, value in vis_logs:
        par_han = value.split(',')
        par_module = __import__('plugins.parsers.%s' % par_han[0], fromlist=[par_han[0]])
        par_inst = getattr(par_module, par_han[0])(host)
        han_module = __import__('plugins.handlers.%s' % par_han[1], fromlist=[par_han[1]])
        han_inst = getattr(han_module, par_han[1])(cfg)

        log_workers[key] = (par_inst, han_inst)  # cache the parsers and handlers for later use...

    for key, value in vis_pfms:
        col_han = value.split(',')
        col_module = __import__('plugins.collectors.%s' % col_han[0], fromlist=[col_han[0]])
        col_inst = getattr(col_module, col_han[0])(host)
        han_module = __import__('plugins.handlers.%s' % col_han[1], fromlist=[col_han[1]])
        han_inst = getattr(han_module, col_han[1])(cfg)

        pfm_workers[key] = (col_inst, han_inst)


def run_pfm_collect_minute():
    """
    doing performance check every second, but only doing real works in 0 second !
    """
    if time.localtime()[5] == 0:  # every minute to do collect works
        for key, col_han in pfm_workers.iteritems():
            col_han[1].handle(col_han[0].collect())


def on_logfile_changed(logfile, lines):
    """
    callback method for collector, params delivered by collector.on_modified method

    :param logfile: the log file path, separated by /
    :param lines: the log file changed contents, if multi-line, separated by \n
    """
    file_matched = False
    for key, par_han in log_workers.iteritems():
        service_logfile = key.split('.')
        logfile_seg = logfile.split('/')
        # find the service name in log file directory, and find the log type in log file name...
        if service_logfile[0] in logfile_seg and service_logfile[1] in logfile_seg[-1]:
            file_matched = True
            logging.debug('processing line with: %s' % key)
            try:
                # FIXME, to specify the max number of lines fetched each startup
                # 2013/05/06
                par_han[0].parse_lines(lines, 100)  # call parser method
                par_han[1].handle(par_han[0].get_states())  # call handler method use parser results
            except LogMotorException, e:
                logging.error('processing line error: %s' % e)
                break
            else:
                # logging.debug('One line handled successfully using config of: %s' % key)
                break

    if file_matched is False:
        logging.warning('Not found the corresponding parser/handler for: %s' % logfile)


# ------------- main entrance -------------------------------
if __name__ == "__main__":
    main()