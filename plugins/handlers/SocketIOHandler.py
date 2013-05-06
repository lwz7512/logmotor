# created at 2013/04/17
__author__ = 'lwz'

import logging
from socketIO_client import SocketIO, BaseNamespace
from anyjson import dumps


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
        if len(non_metrics) == 0:
            logging.debug('No metrics be handled!')
            return

        nm_list = []
        for nm in non_metrics:
            nm_list.append(dumps(nm.to_dict()))  # serialized to json
        msg_type = non_metrics[0].type
        self.socketIO = SocketIO(self.server_address, self.server_port, BaseNamespace)
        self.channel = self.socketIO.connect(self.namespace, BaseNamespace)
        self.channel.emit(msg_type, nm_list, self.on_response)  # send to server
        self.socketIO.wait(forCallbacks=True)
        logging.debug('SokcetIOHandler emitting %s to sever:\n %s' % (msg_type, dumps(nm_list)))

    def on_response(self, *args):
        # is it necessary?
        self.socketIO.disconnect()
        logging.debug('emit non metrics success!')