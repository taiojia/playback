from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.templates.nova_conf_for_compute import conf_nova_conf
from playback.templates.nova_compute_conf import conf_nova_compute_conf
from playback.templates.libvirt_bin import conf_libvirt_bin
from playback.templates.libvirtd_conf import conf_libvirtd_conf

from playback import __version__
from playback import common

class NovaCompute(common.Common):
    """
    Deploy Nova compute

    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """
    def _install(self, my_ip, rabbit_hosts, rabbit_user, rabbit_pass, auth_uri, auth_url, nova_pass, novncproxy_base_url, glance_api_servers, neutron_endpoint, neutron_pass, rbd_secret_uuid, memcached_servers):
        print red(env.host_string + ' | Install nova-compute sysfsutils')
        sudo('apt-get update')
        sudo('apt-get -y install nova-compute sysfsutils')

        print red(env.host_string + ' | Update /etc/nova/nova.conf')
        with open('tmp_nova_conf_' + env.host_string, 'w') as f:
            f.write(conf_nova_conf)

        files.upload_template(filename='tmp_nova_conf_'+env.host_string,
                              destination='/etc/nova/nova.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'my_ip': my_ip,
                                       'rabbit_hosts': rabbit_hosts,
                                       'rabbit_user': rabbit_user, 
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': nova_pass,
                                       'novncproxy_base_url': novncproxy_base_url,
                                       'api_servers': glance_api_servers,
                                       'url': neutron_endpoint,
                                       'neutron_password': neutron_pass,
                                       'memcached_servers': memcached_servers})
        os.remove('tmp_nova_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/nova/nova-compute.conf')
        with open('tmp_nova_compute_conf_' + env.host_string, 'w') as f:
            f.write(conf_nova_compute_conf)

        files.upload_template(filename='tmp_nova_compute_conf_'+env.host_string,
                              destination='/etc/nova/nova-compute.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'rbd_secret_uuid': rbd_secret_uuid})

        os.remove('tmp_nova_compute_conf_' + env.host_string)

        print red(env.host_string + ' | Restart Compute service')
        sudo('service nova-compute restart')
        print red(env.host_string + ' |  Remove the SQLite database file')
        sudo('rm -f /var/lib/nova/nova.sqlite')

        print red(env.host_string + ' | Enable libvirt listen on 16509')
        print red(env.host_string + ' | Update /etc/default/libvirt-bin')
        with open('tmp_libvirt_bin_' + env.host_string, 'w') as f:
            f.write(conf_libvirt_bin)
        files.upload_template(filename='tmp_libvirt_bin_' + env.host_string,
                              destination='/etc/default/libvirt-bin',
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_libvirt_bin_' + env.host_string)
        print red(env.host_string + ' | Update /etc/libvirt/libvirtd.conf')
        with open('tmp_libvirtd_conf_' + env.host_string, 'w') as f:
            f.write(conf_libvirtd_conf)
        files.upload_template(filename='tmp_libvirtd_conf_' + env.host_string,
                              destination='/etc/libvirt/libvirtd.conf',
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_libvirtd_conf_' + env.host_string)
        sudo('service libvirt-bin restart')

    def install(self, *args, **kwargs):
        """
        Install nova compute

        :param my_ip: the host management ip
        :param rabbit_hosts: rabbit hosts e.g. `CONTROLLER1,CONTROLLER2`
        :param rabbit_user: the user of rabbit, e.g. `openstack`
        :param rabbit_pass: the password of `rabbit_user`
        :param auth_uri: keystone internal endpoint e.g. `http://CONTROLLER_VIP:5000`
        :param auth_url: keystone admin endpoint e.g. `http://CONTROLLER_VIP:35357`
        :param nova_pass: passowrd of `nova` user
        :param novncproxy_base_url: nova vnc proxy base url e.g. `http://CONTROLLER_VIP:6080/vnc_auto.html`
        :param glance_api_servers: glance host e.g. `http://CONTROLLER_VIP:9292`
        :param neutron_endpoint: neutron endpoint e.g. `http://CONTROLLER_VIP:9696`
        :param neutron_pass: the password of `neutron` user
        :param rbd_secret_uuid: ceph rbd secret for nova libvirt , generated by `uuidgen`
        :param memcached_servers: memcached servers e.g. `CONTROLLER1:11211,CONTROLLER2:11211`
        :returns: None
        """
        return execute(self._install, *args, **kwargs)

