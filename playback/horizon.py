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
        return execute(self._install, *args, **kwargs)

