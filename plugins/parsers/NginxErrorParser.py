__author__ = 'lwz'

from base import LogsterParser, LogsterParsingException


class NginxErrorParser(LogsterParser):

    def __init__(self):
        self.reg = None

    def parse_line(self, line):
        pass

    def get_state(self, duration):
        pass