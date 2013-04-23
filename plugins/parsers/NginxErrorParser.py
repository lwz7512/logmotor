__author__ = 'lwz'

import re

from plugins.base import AlertMetricObject, LogsterParser, LogsterParsingException
from plugins.util import string_toTimestamp


class NginxErrorParser(LogsterParser):

    def __init__(self, host):
        """
        Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.
        """
        self.levels = {'alert': '1', 'crit': '2', 'error': '3', 'warn': '4', 'notice': '5'}

        self.host = host

        self.datetime = None
        self.errortype = None
        self.errormessage = None
        self.client = None
        self.request = None
        self.domain = None

        self.reg = re.compile("""(?P<datetime>.*?)\s
                                \[(?P<errortype>.+)\]\s.*?:\s
                                (?P<errormessage>.+),\s
                                client:\s(?P<client>.+),\s
                                server:\s(?P<server>.+),\s
                                request:\s\"(?P<request>.+)\",\s
                                host:\s\"(?P<domain>.+)\"
                                """, re.X)

    def parse_line(self, line):
        """
        This function should digest the contents of one line at a time, updating
       object's state variables. Takes a single argument, the line to be parsed.
        """

        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                results = regMatch.groupdict()
                self.datetime = results.get('datetime', '')
                self.errortype = results.get('errortype', '')
                self.errormessage = results.get('errormessage', '')
                self.client = results.get('client', '')
                self.request = results.get('request', '')
                self.domain = results.get('domain', '')

                return regMatch
            else:
                raise LogsterParsingException("regmatch failed to match")

        except Exception, e:
            raise LogsterParsingException("regmatch or contents failed with %s" % e)

    def get_state(self, filter=True):
        """ Run any necessary calculations on the data collected from the logs
        :param filter:
        and return a list of metric objects.
        """
        error_metric = AlertMetricObject('nginx.error.%s' % self.host,
                                         self.levels[self.errortype],
                                         self.errormessage,
                                         self.request,
                                         string_toTimestamp(self.datetime, '%Y/%m/%d %H:%M:%S'),
                                         self.client)
        # Return a list of metrics objects
        return [error_metric]