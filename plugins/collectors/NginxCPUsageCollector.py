# created at 2013/05/13
__author__ = 'lwz'

import subprocess
import shlex
import time

from plugins.base import MetricObject


class NginxCPUsageCollector(object):
    """
    collect the nginx worker process cpu time, use the first worker for sample
    """
    def __init__(self, host='localhost'):
        self.host = host
        self.nginx_pids = []

    def collect(self):
        print 'Collecting nginx cpu metric...'
        self.get_nginx_worker_pid()
        pre_nginx = self.get_nginx_time()
        pre_total = self.get_total_time()
        time.sleep(1)  # sleep for update
        pst_nginx = self.get_nginx_time()
        pst_total = self.get_total_time()

        nginx_cpu_diff = sum(pst_nginx) - sum(pre_nginx)
        total_diff = (pst_total[0]+pst_total[2]) - (pre_total[0]+pre_total[2])

        nginx_cpu_percent = nginx_cpu_diff*100.00/total_diff
        total_cpu_percent = (pst_total[0]+pst_total[2])*100/sum(pst_total)
        print 'nginx_cpu_percent: %s' % nginx_cpu_percent
        print 'total cpu percent: %s' % total_cpu_percent

        results = []
        metric = MetricObject('nginx.cputime.minute', nginx_cpu_percent, '%')

        return results.append(metric)

    def get_nginx_worker_pid(self):
        proc1 = subprocess.Popen(shlex.split('ps -ef'), stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(shlex.split('grep nginx'), stdin=proc1.stdout,
                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        proc1.stdout.close()  # Allow proc1 to receive a SIGPIPE if proc2 exits.
        out, err = proc2.communicate()

        for line in out.split('\n'):
            if line.startswith('www-data'):  # get worker process
                fields = line.split('   ')
                self.nginx_pids.append(fields[1])  # get pid field

    def get_nginx_time(self):
        child_proc_file = open('/proc/%s/stat' % self.nginx_pids[0], "r")  # use first work process for sample
        child_field_pre = child_proc_file.readline().split(' ')
        child_proc_file.close()
        return int(child_field_pre[13]), int(child_field_pre[14])  # usertime, systemtime

    def get_total_time(self):
        statFile = open('/proc/stat', "r")
        times = statFile.readline().split(" ")[2:6]  # user, nice, system, idle
        for i in range(len(times)):
            times[i] = int(times[i])
        statFile.close()
        return times
