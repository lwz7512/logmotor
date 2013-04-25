__author__ = 'lwz'

from time import time


class AlertMetricObject(object):
    """
    Non-Metric data, be sent to socket-io-server

    """
    def __init__(self, name, level, message, cause, timestamp, original=None):
        self.name = name  # metric name to specify the service and host, such as: nginx.error.localhost
        self.level = level  # 1:alert, 2:crit, 3:error, 4:warn, 5:notice
        self.message = message  # alert message text describe the problem
        self.cause = cause  # something that cause the problem
        self.timestamp = timestamp  # milliseconds when this event occurred
        self.original = original  # who invoke this problem


class ResMetricObject(object):
    """
    Non-Metric data, be sent to socket-io-server

    extended metric object: for each metric name has many corresponding resources, such as:
    the metric nginx.access as many url requested, server use request time for each url to draw a ranking list
    """
    def __init__(self, name, value, resource, timestamp, original=None):
        self.name = name  # metric name to specify the service and host, such as: nginx.access.localhost
        self.value = value  # metric value, a int/float number
        self.resource = resource  # target or sub object to correspond the value created by service/host
        self.timestamp = timestamp  # milliseconds when the value created
        self.original = original  # the sponsor that cause this event/data, such as client visit...


class MetricObject(object):
    """General representation of a metric that can be used in many contexts"""
    def __init__(self, name, value, units='', type='float', timestamp=int(time())):
        self.name = name
        self.value = value
        self.units = units
        self.type = type
        self.timestamp = timestamp


class LogsterParser(object):
    """Base class for logster parsers"""
    def parse_line(self, line):
        """Take a line and do any parsing we need to do. Required for parsers"""
        raise RuntimeError("Implement me!")

    def get_state(self, duration):
        """Run any calculations needed and return list of metric objects"""
        raise RuntimeError("Implement me!")


class LogMotorException(Exception):
    """
    Raise this exception if sending metric or non-metric to server
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg