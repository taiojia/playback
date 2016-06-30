from fabric.api import *


class MysqlManage(object):
    """Manage Galera Cluster for MySQL"""

    def __init__(self, hosts, user='ubuntu', key_filename=None, password=None, parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        self.key_filename = key_filename
        self.password = password
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel
        env.key_filename = self.key_filename
        env.password = self.password
        env.abort_on_prompts = False

    def _start_wsrep_new_cluster(self):
        sudo('service mysql start --wsrep-new-cluster')

    def _start_mysql(self):
        sudo('service mysql start')

    def _stop_mysql(self):
        sudo('service mysql stop')

    def _change_root_password(self, pwd):
        sudo('mysqladmin -uroot password %s' % pwd)

