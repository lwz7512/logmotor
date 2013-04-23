__author__ = 'lwz'

import re

from plugins.parsers.NginxAccessParser import NginxAccessParser
from plugins.parsers.NginxErrorParser import NginxErrorParser
from plugins.util import time_local_to_timestamp

import unittest


class TestLineParsers(unittest.TestCase):

    def test_nginx_access_parser(self):
        print '------------ TEST NGINX ACCESS PARSER --------------'
        timed_combined_log_sample = '66.249.71.173 - - [08/Nov/2010:14:16:18 -0600] "GET /blog/2010/apr/30/installing-geodjango-dependencies-homebrew/ HTTP/1.1" 200 6569 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" 0.640 0.640 .'
        main_log_sample = '220.181.89.166 - - [18/Apr/2013:03:26:11 +0800] "GET / HTTP/1.1" 200 7512 "-" "Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)" "-"'

        access_parser = NginxAccessParser('localhost')
        matched = access_parser.parse_line(timed_combined_log_sample)
        # matched = access_parser.parse_line(main_log_sample)

        print 'nginx access parse matched!'
        print 'remote_addr: %s' % access_parser.remote_addr
        print 'remote_user: %s' % access_parser.remote_user
        print 'time_local: %s' % access_parser.time_local
        print 'time_local_stamp: %s' % access_parser.time_local
        print 'request_url: %s' % access_parser.request_url
        print 'request_time: %s' % access_parser.request_time
        print 'upstream_response_time: %s' % access_parser.upstream_response_time
        print 'user_agent: %s' % access_parser.user_agent

        self.assertIsNotNone(matched)

    def test_nginx_error_parser(self):
        print '------------ TEST NGINX ERROR PARSER --------------'
        log_sample = '2013/04/18 04:24:08 [error] 533#0: *1116 open() "/usr/share/nginx/html/logtoeye/robots.txt" failed (2: No such file or directory), client: 157.55.35.34, server: logtoeye.com, request: "GET /robots.txt HTTP/1.1", host: "ipintu.com"'
        # matched = re.match('(?P<datetime>.*?)\s', '2013/04/18 04:24:08 ')
        error_parser = NginxErrorParser('localhost')
        matched = error_parser.parse_line(log_sample)

        print 'nginx error parse matched!'
        print 'datetime: %s' % error_parser.datetime
        print 'errortype: %s' % error_parser.errortype
        print 'errormessage: %s' % error_parser.errormessage
        print 'client: %s' % error_parser.client
        print 'request: %s' % error_parser.request
        print 'domain: %s' % error_parser.domain

        self.assertIsNotNone(matched)


if __name__ == '__main__':
    unittest.main()