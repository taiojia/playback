from fabric.api import *
from fabric.contrib import files

conf_external_interface = """# The external network interface
auto eth1
iface eth1 inet manual
up ip link set dev $IFACE up
down ip link set dev $IFACE down"""

class PrepareHost(object):
    """Prepare OpenStack physical hosts"""

    def __init__(self, user, hosts):
        self.user = user
        self.hosts = hosts
        env.user = self.user
        env.hosts = self.hosts

    def setup_external_interface(self):
        with cd('/etc/network'):
            files.append('interfaces', conf_external_interface, use_sudo=True)
        sudo('ifdown eth1', warn_only=True)
        sudo('ifup eth1', warn_only=True)
        # TODO: purge old eth1 configuration

    def setup_ntp(self):
        sudo('echo \'Asia/Shanghai\' > /etc/timezone')
        sudo('cat /usr/share/zoneinfo/Asia/Shanghai | tee /etc/localtime')
        sudo('apt-get install chrony -y')
        # TODO: setup ntp server and ntp client, current all are clients