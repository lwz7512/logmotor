__author__ = 'lwz'

from socketIO_client import SocketIO, BaseNamespace


class SocketIOHandler(object):

    def __init__(self, server_address, server_port, namespace):
        """
        save the server config..
        """
        self.server_address = server_address
        self.server_port = server_port
        self.namespace = namespace

    def handle(self, nonmetric):
        mainSocket = SocketIO(self.server_address, self.server_port, BaseNamespace)
        newsSocket = mainSocket.connect(self.namespace, BaseNamespace)
        newsSocket.message(nonmetric)
        # newsSocket.emit('event name', {'message': log})

