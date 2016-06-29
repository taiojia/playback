from fabric.api import *

class Cmd(object):
    """Run command line on the target host"""

    def __init__(self, user, hosts, parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def cmd(self, command_line):
        sudo(command_line, warn_only=True)
