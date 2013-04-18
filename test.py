__author__ = 'lwz'

# from plugins.collectors.TailContentCollector import TailContentCollector

# 2013/04/18
collector_module = __import__('plugins.collectors.TailContentCollector', fromlist=['TailContentCollector'])
print collector_module.__name__, 'module imported!'
collector_ins = getattr(collector_module, 'TailContentCollector')('the log path', lambda x: x)
collector_ins.mock()
print 'class instanced!'