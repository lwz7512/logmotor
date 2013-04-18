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
        self.socketIO = None
        self.channel = None

    def handle(self, non_metrics):
        self.socketIO = SocketIO(self.server_address, self.server_port, BaseNamespace)
        self.channel = self.socketIO.connect(self.namespace, BaseNamespace)
        self.channel.emit('alert', non_metrics, self.on_response)

    def on_response(self, *args):
        self.channel.disconnect()
        print 'emit non metrics success!'