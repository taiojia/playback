from fabric.api import *
from fabric.contrib import files
from playback.templates.external_interface import conf_external_interface

class PrepareHost(object):
    """Prepare OpenStack physical hosts"""

    def __init__(self, user, hosts=None, parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel
        
    def setup_external_interface(self):
        """host networking"""
        with cd('/etc/network'):
            files.append('interfaces', conf_external_interface, use_sudo=True)
        sudo('ifdown eth1', warn_only=True)
        sudo('ifup eth1', warn_only=True)
        # TODO: purge old eth1 configuration
        
    def setup_ntp(self):
        """network time protocal (ntp)"""
        sudo('echo \'Asia/Shanghai\' > /etc/timezone')
        sudo('cat /usr/share/zoneinfo/Asia/Shanghai | tee /etc/localtime')
        sudo('apt-get install chrony -y')
        # TODO: setup ntp server and ntp client, current all are clients

    def set_openstack_repository(self):
        """openstack packages"""
        sudo('apt-get update')
        sudo('apt-get install software-properties-common -y')
        sudo('add-apt-repository cloud-archive:mitaka -y')
        with prefix('sudo apt-get update'):
            sudo('DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade')
        
        print "[Playback] waiting for reboot\n"
        reboot(wait=600)
        with prefix('sudo apt-get update'):
            sudo('apt-get install python-openstackclient -y')
