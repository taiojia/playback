from fabric.api import *

class Cmd(object):
    """Run command line on the target host"""

    def __init__(self, user, hosts, key_filename=None, password=None, parallel=True):
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

    def cmd(self, command_line):
        sudo(command_line, warn_only=True)
