__author__ = 'lwz'

import time
from socket import socket


class CarbonAggreHandler(object):

    def __init__(self, carbon_server, carbon_port):
        """
        save the server config..
        """
        self.carbon_server = carbon_server
        self.carbon_port = carbon_port

    def handle(self, metrics):
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

    # TODO, create metric by log string...
    # use parser in config file to parse line...
    def create_metric_str(metrics):
        now = int(time.time())
        lines = []
        #We're gonna report all three loadavg values
        test_value = 1
        lines.append("logmotor.test_metric %s %d" % (test_value, now))
        # lines.append("logmotor.other_metric %s %d" % (test_value,now))
        message = '\n'.join(lines) + '\n'  # all lines must end in a newline
        print "sending message\n"
        print '-' * 80
        print message
        print
        return message
