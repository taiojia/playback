from fabric.api import *
from fabric.contrib import files
from playback.templates.galera_list import conf_galera_list_trusty, conf_galera_list_xenial

class MysqlInstallation(object):
    """Install Galera Cluster for MySQL"""

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

    def _release(self):
        release = sudo('lsb_release -cs')
        return release

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
    
    def _install(self):
        if self._release() == 'trusty':
            sudo('DEBIAN_FRONTEND=noninteractive apt-get install -y --force-yes galera-3 mysql-wsrep-5.6')
        if self._release() == 'xenial':
            sudo('DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-downgrades --allow-remove-essential --allow-change-held-packages mariadb-client-10.2 mariadb-server-10.2 galera-3')