from fabric.api import *
from fabric.tasks import Task
from playback import common

class MysqlManage(common.Common):
    """Manage Galera Cluster for MySQL"""

    def _start_wsrep_new_cluster(self):
        if self._release() == 'xenial':
            sudo('systemctl stop mysql', warn_only=True)
            result = sudo('service mysql bootstrap', warn_only=True)
            if result.failed:
                sudo('systemctl start mysql')
        else:
            sudo('service mysql start --wsrep-new-cluster')

    def _start_mysql(self):     
        if self._release() == 'xenial':
            sudo('systemctl restart mysql')
        else:
            sudo('service mysql restart')

    def _stop_mysql(self):
        if self._release() == 'xenial':
            sudo('systemctl stop mysql')
        else:
            sudo('service mysql stop')

    def _change_root_password(self, pwd):
        sudo('mysqladmin -uroot password %s' % pwd)

    def _show_cluster_status(self, root_db_pass):
        sudo("mysql -uroot -p{root_db_pass} -e \"SHOW STATUS LIKE 'wsrep_%';\"".format(root_db_pass=root_db_pass), shell=False)
