from fabric.api import *
from fabric.contrib import files
from fabric.colors import red
import os
from playback.templates.external_interface import conf_external_interface

class PrepareHost(object):
    """Prepare OpenStack physical hosts"""

    def __init__(self, user, hosts=None, key_filename=None, password=None, parallel=True):
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
        
    def setup_external_interface(self, public_interface):
        """host networking"""
        print red(env.host_string + ' | Setup public interface')
        with open('tmp_public_interface_cfg_'+env.host_string, 'w') as f:
            f.write(conf_external_interface)
        files.upload_template(filename='tmp_public_interface_cfg_'+env.host_string,
                                destination='/etc/network/interfaces.d/public_interface.cfg',
                                use_jinja=True,
                                use_sudo=True,
                                backup=True,
                                context={
                                    public_interface: public_interface
                                })
        os.remove('tmp_public_interface_cfg_'+env.host_string)

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
