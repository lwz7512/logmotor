__author__ = 'lwz'

from socketIO_client import SocketIO, BaseNamespace


class SocketIOHandler(object):

    def __init__(self, cfg):
        """
        save the server config..
        """
        self.server_address = cfg['graphite_ip']
        self.server_port = cfg['graphite_port']
        self.namespace = cfg['graphite_namespace']

    def handle(self, non_metrics):
        mainSocket = SocketIO(self.server_address, self.server_port, BaseNamespace)
        channel = mainSocket.connect(self.namespace, BaseNamespace)
        channel.emit('alert', non_metrics, self.on_response)

    def on_response(*args):
        print 'emit non metrics success!'