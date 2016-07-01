from fabric.api import *
from fabric.tasks import Task
from playback import common

class MysqlManage(Task, common.Common):
    """Manage Galera Cluster for MySQL"""

    def __init__(self, user, hosts=None, key_filename=None, password=None, parallel=True, *args, **kwargs):
        super(MysqlManage, self).__init__(*args, **kwargs)
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
        if self._release() == 'xenial':
            sudo('systemctl start mysql --wsrep-new-cluster')

    def _start_mysql(self):
        sudo('service mysql start')
        if self._release() == 'xenial':
            sudo('systemctl start mysql')

    def _stop_mysql(self):
        sudo('service mysql stop')
        if self._release() == 'xenial':
            sudo('systemctl stop mysql')

    def _change_root_password(self, pwd):
        sudo('mysqladmin -uroot password %s' % pwd)

