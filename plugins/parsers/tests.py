__author__ = 'lwz'

from unittest import TestCase

from NginxAccessParser import NginxAccessParser
from NginxErrorParser import NginxErrorParser
from plugins.util import time_local_to_timestamp


# noinspection PyCallingNonCallable
class TestLineParsers(TestCase):

    def test_nginx_access_parser(self):
        access_log = '/home/lwz/logparse/logsamples/nginx/access.log'
        timed_combined_log_sample = '66.249.71.173 - - [08/Nov/2010:14:16:18 -0600] "GET /blog/2010/apr/30/installing-geodjango-dependencies-homebrew/ HTTP/1.1" 200 6569 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" 0.640 0.640 .'
        main_log_sample = '220.181.89.166 - - [18/Apr/2013:03:26:11 +0800] "GET / HTTP/1.1" 200 7512 "-" "Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)" "-"'

        matched = access_parser = NginxAccessParser('localhost')
        # access_parser.parse_line(timed_combined_log_sample)
        access_parser.parse_line(main_log_sample)

        self.assertIsNotNone(matched)
        print 'nginx access parse matched!'
        print 'remote_addr: %s' % access_parser.remote_addr
        print 'remote_user: %s' % access_parser.remote_user
        print 'time_local: %s' % access_parser.time_local
        print 'time_local_stamp: %s' % time_local_to_timestamp(access_parser.time_local)
        print 'request_url: %s' % access_parser.request_url
        print 'request_time: %s' % access_parser.request_time
        print 'upstream_response_time: %s' % access_parser.upstream_response_time

    def test_nginx_error_parser(self):
        error_log = '/home/lwz/logparse/logsamples/nginx/error.log'
