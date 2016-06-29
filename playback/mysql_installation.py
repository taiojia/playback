from fabric.api import *
from fabric.contrib import files
from playback.templates.galera_list import conf_galera_list_trusty, conf_galera_list_xenial

class MysqlInstallation(object):
    """Install Galera Cluster for MySQL"""

    def __init__(self, hosts, user='ubuntu', key_filename='~/.ssh/id_rsa', parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        self.key_filename = key_filename
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel
        env.key_filename = self.key_filename
        env.abort_on_prompts = False

    def _enable_repo(self):
        with settings(hide('running', 'commands', 'stdout', 'stderr')):
            result = sudo('lsb_release -cs')
            if result == 'xenial':
                conf_galera_list = conf_galera_list_xenial
        sudo('apt-key adv --recv-keys --keyserver keyserver.ubuntu.com BC19DDBA')
        with cd('/etc/apt/sources.list.d/'):
            sudo('rm -rf galera.list', warn_only=True)
            files.append('galera.list', conf_galera_list, use_sudo=True)
        sudo('apt-get update')
    
    def _install(self):
        sudo('DEBIAN_FRONTEND=noninteractive apt-get install -y --force-yes galera-3 galera-arbitrator-3 mysql-wsrep-5.6')