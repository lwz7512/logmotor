__author__ = 'lwz'

import unittest

from anyjson import dumps

from plugins.parsers.NginxAccessParser import NginxAccessParser
from plugins.parsers.NginxErrorParser import NginxErrorParser
from plugins.base import MetricObject


class TestLineParsers(unittest.TestCase):

    def test_nginx_access_parser(self):
        print '------------ TEST NGINX ACCESS PARSER --------------'
        timed_combined_log_sample = '66.249.71.173 - - [08/Nov/2010:14:16:18 -0600] "GET /blog/2010/apr/30/installing-geodjango-dependencies-homebrew/ HTTP/1.1" 200 6569 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" 0.640 0.640 .'
        main_log_sample = '220.181.89.166 - - [18/Apr/2013:03:26:11 +0800] "GET / HTTP/1.1" 200 7512 "-" "Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)" "-"'
        nginx140 = '127.0.0.1 - - [03/May/2013:19:40:16 +0800] "GET /static/img/tag_icon.png HTTP/1.1" 304 0 "http://localhost/" "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11"'

        access_parser = NginxAccessParser('localhost')
        matched = access_parser.parse_line(nginx140)
        # matched = access_parser.parse_line(timed_combined_log_sample)
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
        nginx_error_085 = '2013/04/18 04:24:08 [error] 533#0: *1116 open() "/usr/share/nginx/html/logtoeye/robots.txt" failed (2: No such file or directory), client: 157.55.35.34, server: logtoeye.com, request: "GET /robots.txt HTTP/1.1", host: "ipintu.com"'
        # matched = re.match('(?P<datetime>.*?)\s', '2013/04/18 04:24:08 ')
        nginx_error_140 = '2013/05/06 11:56:08 [notice] 3836#0: signal process started'
        error_parser = NginxErrorParser('localhost')
        matched = error_parser.parse_line(nginx_error_140)

        print 'nginx error parse matched!'
        print 'datetime: %s' % error_parser.datetime
        print 'errortype: %s' % error_parser.errortype
        print 'errormessage: %s' % error_parser.errormessage
        print 'client: %s' % error_parser.client
        print 'request: %s' % error_parser.request
        print 'domain: %s' % error_parser.domain

        self.assertIsNotNone(matched)


class TestJsonDump(unittest.TestCase):

    def test_dict_list_serialize(self):
        print '---------- TEST METRIC LIST SERIALIZE ------'
        print 'serialized dic: %s' % dumps({'key': 0})
        print 'serialized array: %s' % dumps(['a', 'b', 1])

    def test_metric_serialize(self):
        print '---------- TEST METRIC SERIALIZE -----------'
        mo = MetricObject('test.metric', 0, 'm')
        print dumps(mo.to_dict())

    def test_dict_in_list_serialize(self):
        print '---------- TEST DIC IN LIST SERIALIZE ------'
        mo = MetricObject('test.metric', 0, 'm')
        mt = MetricObject('two.metric', 1, 's')
        print dumps([mo.to_dict(), mt.to_dict()])


if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestJsonDump)
    unittest.TextTestRunner(verbosity=2).run(suite)