# created at 2013/05/03, just for agent log test without send to server
__author__ = 'lwz'

from json import dumps


class ConsoleHandler(object):

    def __init__(self, cfg):
        pass

    def handle(self, obj_list):
        jsons = []
        # print 'console handler receive obj_list: %s' % obj_list
        if obj_list is None or not hasattr(obj_list, "__iter__"):
            return

        for nm in obj_list:
            jsons.append(dumps(nm.to_dict()))  # serialized to json

        print 'console handler receive logs: %s' % dumps(jsons)