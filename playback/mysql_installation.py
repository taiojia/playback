from fabric.api import *
from fabric.contrib import files
from playback.templates.galera_list import conf_galera_list

class MysqlInstallation(object):
    """Install Galera Cluster for MySQL"""

    def __init__(self, hosts, user='ubuntu', parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _enable_repo(self):
        sudo('apt-key adv --recv-keys --keyserver keyserver.ubuntu.com BC19DDBA')
        with cd('/etc/apt/sources.list.d/'):
            files.append('galera.list', conf_galera_list, use_sudo=True)
        sudo('apt-get update')
        # TODO: Purge old galera.list
    
    def _install(self):
        sudo('DEBIAN_FRONTEND=noninteractive apt-get install -y --force-yes galera-3 mysql-wsrep-5.6')