from fabric.api import *
from fabric.contrib import files
from playback.templates.galera_list import conf_galera_list_trusty
from playback import common

class MysqlInstallation(common.Common):
    """Install Galera Cluster for MySQL"""

    def _enable_repo(self):
        if self._release() == 'trusty':
            conf_galera_list = conf_galera_list_trusty
            sudo('apt-key adv --recv-keys --keyserver keyserver.ubuntu.com BC19DDBA')
            with cd('/etc/apt/sources.list.d/'):
                sudo('rm -rf galera.list', warn_only=True)
                files.append('galera.list', conf_galera_list, use_sudo=True)
                sudo('apt-get update')
    
    def _install(self):
        if self._release() == 'trusty':
            sudo('DEBIAN_FRONTEND=noninteractive apt-get install -y --force-yes galera-3 mysql-wsrep-5.6')
            sudo('service mysql stop', warn_only=True)
        if self._release() == 'xenial':
            sudo('apt install -y mariadb-server python-pymysql galera-3')
            sudo('systemctl stop mysql', warn_only=True)