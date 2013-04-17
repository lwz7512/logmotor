__author__ = 'lwz'

# from plugins.collectors.TailContentCollector import TailContentCollector

collector_module = __import__('plugins.collectors.TailContentCollector', globals(), locals(), ['TailContentCollector'])
print 'module imported!'
collector_ins = getattr(collector_module, 'TailContentCollector')('the log path', lambda x: x)
collector_ins.mock()
print 'class instanced!'