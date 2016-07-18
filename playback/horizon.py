from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.templates.local_settings_py import conf_local_settings_py
from playback import __version__
from playback import common

class Horizon(common.Common):
    """
    Install horizon
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """

    def _install(self, openstack_host, memcached_servers, time_zone):
        print red(env.host_string + ' | Install the packages')
        sudo('apt-get update')
        sudo('apt-get -y install openstack-dashboard')

        print red(env.host_string + ' | Update /etc/openstack-dashboard/local_settings.py')
        with open('tmp_local_settings_py_' + env.host_string, 'w') as f:
            f.write(conf_local_settings_py)
        files.upload_template(filename='tmp_local_settings_py_' + env.host_string,
                              destination='/etc/openstack-dashboard/local_settings.py',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'openstack_host': openstack_host,
                                       'memcached_servers': memcached_servers,
                                       'time_zone': time_zone})
        os.remove('tmp_local_settings_py_' + env.host_string)

    def install(self, *args, **kwargs):
        """
        Install horizon

        :param openstack_host: configure the dashboard to use OpenStack services on the controller node e.g. `CONTROLLER_VIP`
        :param memcached_servers: django memcache e.g. `CONTROLLER1:11211,CONTROLLER2:11211`
        :param time_zone: the timezone of the server. This should correspond with the timezone of your entire OpenStack installation e.g. `America/New_York`
        :returns: None
        """
        return execute(self._install, *args, **kwargs)

