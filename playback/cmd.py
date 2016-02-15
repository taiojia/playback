from fabric.api import *

class Cmd(object):
    """Run command line on the target host"""

    def __init__(self, user, hosts):
        self.user = user
        self.hosts = hosts
        env.user = self.user
        env.hosts = self.hosts

    def cmd(self, command_line):
        sudo(command_line, warn_only=True)
