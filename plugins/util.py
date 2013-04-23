__author__ = 'lwz'

from datetime import datetime
import time

# for all the format see:
# http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior


# '2013-04-22 15:39:00'
def simple_dateformat_to_datetime(date_str):
    return datetime.fromtimestamp(time.mktime(time.strptime(date_str, "%Y-%m-%d %H:%M:%S")))


# time_local: 18/Apr/2013:03:26:11
def time_local_to_timestamp(string):
    return string_toTimestamp(string, '%d/%b/%Y:%H:%M:%S')


def datetime_toString(dt):
    return dt.strftime(format)


def string_toDatetime(string, format):
    return datetime.strptime(string, format)


def string_toTimestamp(strTime, format):
    return time.mktime(string_toDatetime(strTime, format).timetuple())


def timestamp_toString(stamp, format):
    return time.strftime(format, time.localtime(stamp))


def datetime_toTimestamp(dateTim):
    return time.mktime(dateTim.timetuple())