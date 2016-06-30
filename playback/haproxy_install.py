from fabric.api import *


class HaproxyInstall(object):
    """HAProxy and Keepalived Installation"""
    def __init__(self, hosts, user='ubuntu',key_filename=None, password=None, parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        self.key_filename = key_filename
        self.password = password
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel
        env.key_filename = key_filename
        env.password = password

    def _install(self):
        sudo('apt-get update')
        sudo('apt-get install -y haproxy keepalived mysql-client')