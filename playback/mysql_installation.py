from fabric.api import *
from fabric.contrib import files
from playback.templates.galera_list import conf_galera_list_trusty, conf_galera_list_xenial
from playback import common

class MysqlInstallation(common.Common):
    """
    Install Galera Cluster for MySQL
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """


    def _enable_repo(self):
        if self._release() == 'trusty':
            conf_galera_list = conf_galera_list_trusty
            sudo('apt-key adv --recv-keys --keyserver keyserver.ubuntu.com BC19DDBA')
        if self._release() == 'xenial':
            conf_galera_list = conf_galera_list_xenial
            sudo('apt-key adv --recv-keys --keyserver keyserver.ubuntu.com F1656F24C74CD1D8')
        
        with cd('/etc/apt/sources.list.d/'):
            sudo('rm -rf galera.list', warn_only=True)
            files.append('galera.list', conf_galera_list, use_sudo=True)
            sudo('apt-get update')
    
    def enable_repo(self):
        """
        Setup repository for trusty only
        
        :returns: None
        """
        return execute(self._enable_repo)
    
    def _install(self):
        if self._release() == 'trusty':
            sudo('DEBIAN_FRONTEND=noninteractive apt-get install -y --force-yes galera-3 mysql-wsrep-5.6')
        if self._release() == 'xenial':
            sudo('DEBIAN_FRONTEND=noninteractive apt install -y --allow-downgrades --allow-remove-essential --allow-change-held-packages mariadb-client mariadb-galera-server galera rsync')

    def install(self):
        """
        Install Galera Cluster for MySQL if trusty, install MariaDB Galera Cluster if xenial

        :returns: None
        """
        return execute(self._install)