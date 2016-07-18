from fabric.api import *
from fabric.tasks import Task
from fabric.colors import red
from playback import common
import sys

class MysqlManage(common.Common):
    """
    Manage Galera Cluster for MySQL
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """

    def _start_wsrep_new_cluster(self):
        if self._release() == 'xenial':
            sudo('systemctl stop mysql', warn_only=True, shell=False)
            #sudo('service mysql bootstrap', shell=False) #this will invoke joiner failed
            xenial_warning = """Please bootstrap the new cluster node manually on Xenial with MariaDB 10.0.\nRun: 'sudo service mysql bootstrap' on remote server.\n"""
            sys.stdout.write(red(xenial_warning))
        else:
            sudo('service mysql start --wsrep-new-cluster')

    def start_wsrep_new_cluster(self):
        """
        Initialize the primary component on one cluster node

        :returns: None
        """
        return execute(self._start_wsrep_new_cluster)

    def _start_mysql(self):     
        if self._release() == 'xenial':
            sudo('systemctl restart mysql', shell=False)
        else:
            sudo('service mysql restart')

    def start_mysql(self):
        """
        Start the database server to join the cluster

        :returns: None
        """
        return execute(self._start_mysql)

    def _stop_mysql(self):
        if self._release() == 'xenial':
            sudo('systemctl stop mysql', shell=False)
        else:
            sudo('service mysql stop')

    def stop_mysql(self):
        """
        Stop the mysql service

        :returns: None
        """
        return execute(self._stop_mysql)

    def _change_root_password(self, pwd):
        sudo('mysqladmin -uroot password %s' % pwd)

    def change_root_password(self, *args, **kwargs):
        """
        Change the mysql root password

        :param pwd: the new password of root user
        :returns: None
        """
        return execute(self._change_root_password, *args, **kwargs)

    def _show_cluster_status(self, root_db_pass):
        sudo("mysql -uroot -p{root_db_pass} -e \"SHOW STATUS LIKE 'wsrep_%';\"".format(root_db_pass=root_db_pass), shell=False)

    def show_cluster_status(self, *args, **kwargs):
        """
        Display the cluster status

        :param root_db_pass: the password of mysql root user
        :returns: None
        """
        return execute(self._show_cluster_status, *args, **kwargs)
