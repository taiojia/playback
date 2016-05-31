from fabric.api import *


class MysqlManage(object):
    """Manage Galera Cluster for MySQL"""

    def __init__(self, hosts, user='ubuntu', parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    @runs_once
    @serial
    def _start_wsrep_new_cluster(self):
        sudo('service mysql start --wsrep-new-cluster')

    @runs_once
    def _start_mysql(self):
        sudo('service mysql start')

    @runs_once
    def _stop_mysql(self):
        sudo('service mysql stop')

    @runs_once
    def _change_root_password(self, pwd):
        sudo('mysqladmin -uroot password %s' % pwd)

