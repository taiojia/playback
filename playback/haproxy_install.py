from fabric.api import *
from playback import common


class HaproxyInstall(common.Common):
    """HAProxy and Keepalived Installation"""

    def _install(self):
        sudo('apt-get update')
        sudo('apt-get install -y haproxy keepalived mysql-client')
    
    def install(self):
        return execute(self._install)
        