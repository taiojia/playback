from fabric.api import *


class HaproxyInstall(object):
    """HAProxy and Keepalived Installation"""
    def __init__(self, hosts, user='ubuntu', parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _install(self):
        sudo('apt-get update')
        sudo('apt-get install -y haproxy keepalived mysql-client')