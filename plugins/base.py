__author__ = 'lwz'

from time import time


class ResMetricObject(object):
    """
    extended metric object: for each metric name has many corresponding resources, such as:
    the metric nginx.access as many url requested, server use request time for each url to draw a ranking list
    """
    def __init__(self, name, value, resource, timestamp):
        self.name = name
        self.value = value
        self.resource = resource
        self.timestamp = timestamp


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


class LogsterParsingException(Exception):
    """Raise this exception if the parse_line function wants to
        throw a 'recoverable' exception - i.e. you want parsing
        to continue but want to skip this line and log a failure."""
    pass