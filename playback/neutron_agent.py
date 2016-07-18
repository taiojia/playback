from fabric.api import *
from fabric.contrib import files
from fabric.tasks import Task
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.templates.neutron_conf_for_agent import conf_neutron_conf
from playback.templates.linuxbridge_agent_ini_for_agent import conf_linuxbridge_agent_ini
from playback import __version__
from playback import common

class NeutronAgent(common.Common):
    """
    Deploy neutron agent
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """

    def _install(self, rabbit_hosts, rabbit_user, rabbit_pass, auth_uri, auth_url, neutron_pass, public_interface, local_ip, memcached_servers):
        print red(env.host_string + ' | Install the components')
        sudo('apt-get update')
        # conntrack deprecated in mitaka
        #sudo('apt-get -y install neutron-plugin-linuxbridge-agent conntrack')
        sudo('apt-get -y install neutron-linuxbridge-agent')

        print red(env.host_string + ' | Update /etc/neutron/neutron.conf')
        with open('tmp_neutron_conf_' + env.host_string, 'w')as f:
            f.write(conf_neutron_conf)
        files.upload_template(filename='tmp_neutron_conf_' + env.host_string,
                              destination='/etc/neutron/neutron.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'rabbit_hosts': rabbit_hosts,
                                       'rabbit_user': rabbit_user, 
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'neutron_pass': neutron_pass, 
                                       'memcached_servers': memcached_servers})
        os.remove('tmp_neutron_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/plugins/ml2/linuxbridge_agent.ini')
        with open('tmp_linuxbridge_agent_ini_' + env.host_string, 'w')as f:
            f.write(conf_linuxbridge_agent_ini)
        files.upload_template(filename='tmp_linuxbridge_agent_ini_' + env.host_string,
                              destination='/etc/neutron/plugins/ml2/linuxbridge_agent.ini',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'public_interface': public_interface,
                                       'local_ip': local_ip})
        os.remove('tmp_linuxbridge_agent_ini_' + env.host_string)

        print red(env.host_string + ' | Restart Services')
        sudo('service nova-compute restart')
        sudo('service neutron-linuxbridge-agent restart')

    def install(self, *args, **kwargs):
        """
        Install neutron agent

        :param rabbit_hosts: rabbit hosts e.g. `CONTROLLER1,CONTROLLER2`
        :param rabbit_user: the user of rabbit, e.g. `openstack`
        :param rabbit_pass: the password of `rabbit_user`
        :param auth_uri: keystone internal endpoint e.g. `http://CONTROLLER_VIP:5000`
        :param auth_url: keystone admin endpoint e.g. `http://CONTROLLER_VIP:35357`
        :param neutron_pass: the password of `neutron` user
        :param public_interface: public interface e.g. `eth1`
        :param local_ip: underlying physical network interface that handles overlay networks(uses the management interface IP)
        :param memcached_servers: memcached servers e.g. `CONTROLLER1:11211,CONTROLLER2:11211`
        :returns: None
        """
        return execute(self._install, *args, **kwargs)

