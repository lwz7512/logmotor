# created at 2013/04/26
__author__ = 'lwz'


class CPUUsageCollector(object):
    """
    this collector is just a wrapper of other open source performance collector,
    such as Diamond collector,also it can implement itself collect method , this logic
    controlled by solo flag

    there principles:
    1. pure python
    2. simple implementation
    3. integrated as many as possible third part collectors
    """
    def __init__(self, solo=True):
        self.solo = solo  # if true, use this collector itself method

    def collect(self):
        """
        use my own method or third part method to get the metric
        """
        print 'Collecting CPU metric...'
        if self.solo:
            pass  # TODO, IMPLEMENT A SIMPLE COLLECT METHOD
        else:
            pass  # TODO, CALL THE THIRD PART COLLECT COLLECTOR

        return None