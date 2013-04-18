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

    def handle(self, non_metrics_json):
        mainSocket = SocketIO(self.server_address, self.server_port, BaseNamespace)
        newsSocket = mainSocket.connect(self.namespace, BaseNamespace)
        newsSocket.message(non_metrics_json)
        # newsSocket.emit('event name', {'message': log})