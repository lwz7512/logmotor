__author__ = 'lwz'

import re

from plugins.base import ResMetricObject, LogsterParser, LogsterParsingException
from plugins.util import time_local_to_timestamp


class NginxAccessParser(LogsterParser):

    def __init__(self, host):
        """
        Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.

        :rtype : None
        :param host: where this agent live/exist

        default access config:
        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

        custom access log format:
        log_format timed_combined '$remote_addr - $remote_user [$time_local] '
                                '"$request" $status $body_bytes_sent '
                                '"$http_referer" "$http_user_agent" '
                                '$request_time $upstream_response_time $pipe';
        """
        self.host = host

        self.remote_addr = None
        self.remote_user = None
        self.time_local = None
        self.request_url = None
        self.request_time = None  # the time it took nginx to work on the request
        self.upstream_response_time = None

        self.reg = re.compile("""(?P<remote_addr>\S*)\s-\s(?P<remote_user>\S*)\s\[(?P<time_local>.*?)\]\s
                                \"(?P<request_method>\S*)\s*(?P<request_url>\S*)\s*(HTTP\/)*(?P<http_version>\d\.\d)\"\s
                                (?P<status>\d{3})\s(?P<body_bytes_sent>\S*)\s\"(?P<http_referer>[^\"]*)\"\s
                                \"(?P<http_user_agent>[^\"]*)\"\s\"(?P<http_x_forwarded_for>\S*)\"
                                """, re.X)

        # for timed_combined
        # self.reg = re.compile("""(?P<remote_addr>\S*)\s-\s(?P<remote_user>\S*)\s\[(?P<time_local>.*?)\]\s
        #                          \"(?P<request_method>\S*)\s*(?P<request_url>\S*)\s*(HTTP\/)*(?P<http_version>\d\.\d)\"\s
        #                          (?P<status>\d{3})\s(?P<body_bytes_sent>\S*)\s\"(?P<http_referer>[^\"]*)\"\s
        #                          \"(?P<http_user_agent>[^\"]*)\"\s
        #                          (?P<request_time>\S*)\s  # $request_time, request processing time in seconds with a milliseconds resolution; time elapsed between the first bytes were read from the client and the log write after the last bytes were sent to the client
        #                          (?P<upstream_response_time>\S*)\s  # $upstream_response_time, Response time of upstream server(s) in seconds, with an accuracy of milliseconds.
        #                          (?P<pipe>\S*)""", re.X)

    def parse_line(self, line):
        """
        This function should digest the contents of one line at a time, updating
       object's state variables. Takes a single argument, the line to be parsed.
        """
        # TODO, FIRST NEED TO RE INIT THE __init__ VALUES, EXCEPT THE REG..

        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                results = regMatch.groupdict()
                self.remote_addr = results.get('remote_addr', '')
                self.remote_user = results.get('remote_user', '')
                self.time_local = results.get('time_local', 'xxxxxx')[:-6]  # remove +0800
                self.request_url = results.get('request_url', '')
                self.request_time = results.get('request_time', '')
                self.upstream_response_time = results.get('upstream_response_time', '')

                return  regMatch
            else:
                raise LogsterParsingException, "regmatch failed to match"

        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e

    def get_state(self, duration):
        """ Run any necessary calculations on the data collected from the logs
        :param duration:
        and return a list of metric objects.
        """
        timestamp = time_local_to_timestamp(self.time_local)
        res_metric = ResMetricObject('nginx.access.%s' % self.host,
                                    self.request_time,
                                    self.request_url,
                                    timestamp)
        # Return a list of metrics objects
        return [res_metric]