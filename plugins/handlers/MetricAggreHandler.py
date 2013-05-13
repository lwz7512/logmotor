# created at 2013/04/17
__author__ = 'lwz'

import time
from socket import socket


class MetricAggreHandler(object):

    def __init__(self, cfg):
        """
        send metric to carbon server,and display in graphite
        """
        self.carbon_server = cfg['carbon_ip']
        self.carbon_port = cfg['carbon_port']

    def handle(self, metrics):
        print 'handle metric...'
        if metrics is None or len(metrics) == 0:
            return

        message = self.create_metric_str(metrics)
        sock = socket()
        try:
            sock.connect((self.carbon_server, self.carbon_port))
        except BaseException:
            print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" \
                  % {'server': self.carbon_server, 'port': self.carbon_port}
            return
        sock.sendall(message)
        sock.close()

    # use parser in config file to parse line...
    def create_metric_str(self, metrics):
        now = int(time.time())
        lines = []
        for m in metrics:
            lines.append("%s %s %d" % (m.name, m.value, m.timestamp))
        message = '\n'.join(lines) + '\n'  # all lines must end in a newline
        print "sending message\n"
        print '-' * 80
        print message
        print
        return message
