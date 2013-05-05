__author__ = 'lwz'

import re

from plugins.base import ResMetricObject, LogsterParser, LogMotorException
from plugins.util import time_local_to_timestamp


class NginxAccessParser(LogsterParser):

    def __init__(self, host):
        """
        Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.

        :rtype : None
        :param host: where this agent live/exist

        default nginx access config:
        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

        custom access log format: one blank after [$time_local]
        log_format timed_combined '$remote_addr - $remote_user [$time_local] '
                                '"$request" $status $body_bytes_sent '
                                '"$http_referer" "$http_user_agent" '
                                '$request_time $upstream_response_time $pipe';

        *** CAUTION HERE:***
        In this parser, I used the log_format timed_combined borrowed from:
        http://articles.slicehost.com/2010/8/27/customizing-nginx-web-logs
        http://lincolnloop.com/blog/2010/nov/9/tracking-application-response-time-nginx/

        But, I made a small modification after [$time_local], I delete one blank to their timed_combined format.
        There has only ONE blank between [$time_local] and "$request".
        I use this modified timed_combined format in my nginx config file,
        so, the corresponding regular expression is: [(?P<time_local>.*?)\]\s

        If you copy the timed_combined format directly from that pages and paste to you config file,
        then, in order to make this parser work successfully, you need to APPEND \s AFTER (?P<time_local>.*?)\]\s
        THAT IS: (?P<time_local>.*?)\]\s\s
        See details blow in: self.reg

        """
        self.spiders = ['Sogou web spider', 'Baiduspider', 'bingbot',
                        'EasouSpider', 'JikeSpider', 'msnbot', 'SurveyBot']
        self.spider_visit_url = '/robots.txt'

        self.host = host  # host machine ip that log file reside in

        self.remote_addr = None
        self.remote_user = None
        self.time_local = None
        self.request_url = None
        # $request_time, request processing time in seconds with a milliseconds resolution;
        # time elapsed between the first bytes were read from the client
        # and the log write after the last bytes were sent to the client
        self.request_time = None
        # $upstream_response_time, Response time of upstream server(s) in seconds,
        # with an accuracy of milliseconds.
        self.upstream_response_time = None
        self.user_agent = None

        # for nginx/1.4.0
        self.reg = re.compile("""(?P<remote_addr>\S*)\s-\s(?P<remote_user>\S*)\s\[(?P<time_local>.*?)\]\s
                                \"(?P<request_method>\S*)\s*(?P<request_url>\S*)\s*(HTTP\/)*(?P<http_version>\d\.\d)\"\s
                                (?P<status>\d{3})\s(?P<body_bytes_sent>\S*)\s\"(?P<http_referer>.+)\"\s
                                \"(?P<http_user_agent>.+)\"
                                """, re.X)

        # for nginx/0.8.54 log_format  main
        # self.reg = re.compile("""(?P<remote_addr>\S*)\s-\s(?P<remote_user>\S*)\s\[(?P<time_local>.*?)\]\s
        #                         \"(?P<request_method>\S*)\s*(?P<request_url>\S*)\s*(HTTP\/)*(?P<http_version>\d\.\d)\"\s
        #                         (?P<status>\d{3})\s(?P<body_bytes_sent>\S*)\s\"(?P<http_referer>.+)\"\s
        #                         \"(?P<http_user_agent>.+)\"\s\"(?P<http_x_forwarded_for>\S*)\"
        #                         """, re.X)

        # for timed_combined
        # self.reg = re.compile("""(?P<remote_addr>\S*)\s-\s(?P<remote_user>\S*)\s
        #                         \[(?P<time_local>.*?)\]\s  # one blank space here, may by you need addtional \s
        #                         \"(?P<request_method>\S*)\s*(?P<request_url>\S*)\s*(HTTP/)*(?P<http_version>\d\.\d)\"\s
        #                         (?P<status>\d{3})\s(?P<body_bytes_sent>\S*)\s\"(?P<http_referer>.+)\"\s
        #                         \"(?P<http_user_agent>.+)\"\s
        #                         (?P<request_time>\S*)\s
        #                         (?P<upstream_response_time>\S*)\s
        #                         (?P<pipe>\S*)""", re.X)
        # save the metrics or non-metrics
        self.states = None

    # parse the line separated by \n
    def parse_lines(self, lines, last=10):
        self.states = []
        splits = lines.split('\n')
        # ONLY GET THE LAST TEN LINES...
        for line in splits[-last:]:
            if len(line) == 0:
                continue
            self.parse_line(line)
            if self.get_state():
                self.states.append(self.get_state())

    # get the generated data...
    def get_states(self):
        return self.states

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
                self.remote_addr = results.get('remote_addr', '')
                self.remote_user = results.get('remote_user', '')
                self.time_local = results.get('time_local', 'xxxxxx')[:-6]  # remove +0800
                self.request_url = results.get('request_url', '')
                self.request_time = results.get('request_time', '')
                self.upstream_response_time = results.get('upstream_response_time', '')
                self.user_agent = results.get('http_user_agent', '')

                return regMatch
            else:
                raise LogMotorException("reg match failed to match, re-check the reg expression !")

        except Exception, e:
            raise LogMotorException("reg match or contents failed with %s" % e)

    def get_state(self, filter=True):
        """ Run any necessary calculations on the data collected from the logs
        :param filter: filter that don't needed data
        and return a list of metric objects.
        """
        # FILTER THE INVALID URL
        if self.request_url is self.spider_visit_url or self.request_url is '/':
            return None
        # FILTER THE REQUEST FROM SPIDER
        for spider in self.spiders:
            if spider in self.user_agent:
                return None
        # FILTER STATIC FILES USE REGULAR EXPRESSION...
        reg = '\.(htm|html|git|jpg|jpeg|png|bmp|ico|css|js|txt)$'
        match = re.search(reg, self.request_url)
        if match:
            return None

        # FIXME, TO FILTER THE INVALID VALUE...
        # if len(self.request_time) == 0 or float(self.request_time) == 0:
        #     return None

        timestamp = time_local_to_timestamp(self.time_local)
        res_metric = ResMetricObject('nginx.access.%s' % self.host,
                                     self.request_time,
                                     self.request_url,
                                     timestamp,
                                     self.remote_addr)
        # Return a list of metrics objects
        return res_metric