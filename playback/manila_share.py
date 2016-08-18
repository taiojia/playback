from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback import __version__
from playback import common
from playback.templates.manila_conf_for_share import conf_manila_conf

class ManilaShare(common.Common):
    """
    Install manila share service
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    :examples:

        .. code-block:: python

            # create manila share instances
            manila_share1 = ManilaShare(user='ubuntu', hosts=['controller1'])
            manila_share2 = ManilaShare(user='ubuntu', hosts=['controller2'])

            # install manila share service the same as manila service nodes
            manila_share1.install_manila_share(
                connection='mysql+pymysql://manila:changeme@192.168.1.1/manila',
                auth_uri='http://192.168.1.1:5000',
                auth_url='http://192.168.1.1:35357',
                manila_pass='changeme',
                my_ip='192.168.1.2',
                memcached_servers='192.168.1.2:11211,192.168.1.3:11211',
                rabbit_hosts='192.168.1.2,192.168.1.3',
                rabbit_user='openstack',
                rabbit_pass='changeme',
                neutron_endpoint='http://192.168.1.1:9696',
                neutron_pass='changeme',
                nova_pass='changeme',
                cinder_pass='changeme'
            )
            manila_share2.install_manila_share(
                connection='mysql+pymysql://manila:changeme@192.168.1.1/manila',
                auth_uri='http://192.168.1.1:5000',
                auth_url='http://192.168.1.1:35357',
                manila_pass='changeme',
                my_ip='192.168.1.3',
                memcached_servers='192.168.1.2:11211,192.168.1.3:11211',
                rabbit_hosts='192.168.1.2,192.168.1.3',
                rabbit_user='openstack',
                rabbit_pass='changeme',
                neutron_endpoint='http://192.168.1.1:9696',
                neutron_pass='changeme',
                nova_pass='changeme',
                cinder_pass='changeme'
            )

            # create the service image for manila
            http://docs.openstack.org/mitaka/install-guide-ubuntu/launch-instance-manila.html

            # create shares with share servers management support
            http://docs.openstack.org/mitaka/install-guide-ubuntu/launch-instance-manila-dhss-true-option2.html
    """

    def _install_manila_share(self, connection, auth_uri, auth_url, manila_pass, my_ip, memcached_servers, rabbit_hosts, rabbit_user, rabbit_pass, neutron_endpoint, neutron_pass, nova_pass, cinder_pass):
        sys.stdout.write(red(env.host_string + ' | Install manila-share python-pymysql and neutron-plugin-linuxbridge-agent\n'))
        sudo('apt update')
        sudo('apt install manila-api manila-share python-pymysql neutron-plugin-linuxbridge-agent -y')

        sys.stdout.write(red(env.host_string + ' | Update /etc/manila/manila.conf\n'))
        with open('tmp_manila_conf_' + env.host_string ,'w') as f:
            f.write(conf_manila_conf)
        files.upload_template(filename='tmp_manila_conf_' + env.host_string,
                                destination='/etc/manila/manila.conf',
                                use_jinja=True,
                                use_sudo=True,
                                backup=True,
                                context={
                                    'connection': connection,
                                    'rabbit_hosts': rabbit_hosts,
                                    'rabbit_userid': rabbit_user,
                                    'rabbit_password': rabbit_pass,
                                    'memcached_servers': memcached_servers,
                                    'auth_uri': auth_uri,
                                    'auth_url': auth_url,
                                    'manila_pass': manila_pass,
                                    'my_ip': my_ip,
                                    'neutron_endpoint': neutron_endpoint,
                                    'neutron_pass': neutron_pass,
                                    'nova_pass': nova_pass,
                                    'cinder_pass': cinder_pass
                                })
        os.remove('tmp_manila_conf_' + env.host_string)
        
        sys.stdout.write(red(env.host_string + ' | Restart the Share File Systems service including its dependencies\n'))
        finalize = sudo('systemctl restart manila-share')
        if finalize.failed or self._release == 'trusty':
            sudo('service manila-share restart')

    def install_manila_share(self, *args, **kwargs):
        """
        Install manila share service

        :param connection: The SQLAlchemy connection string to use to connect to the database. (string value) e.g. `mysql+pymysql://manila:MANILA_PASS@CONTROLLER_VIP/manila`
        :param auth_uri: Complete public Identity API endpoint. (string value) e.g. `http://CONTROLLER_VIP:5000`
        :param auth_url: Authentication URL (unknown value) e.g. `http://CONTROLLER_VIP:35357`
        :param manila_pass: passowrd of `manila` user
        :param my_ip: IP address of this host. (string value)
        :param memcached_servers: Memcached servers or None for in process cache. (list value) e.g. `CONTROLLER1:11211,CONTROLLER2:11211`
        :param rabbit_hosts: RabbitMQ HA cluster host:port pairs. (list value) e.g. `CONTROLLER1,CONTROLLER2`
        :param rabbit_user: The RabbitMQ userid. (string value) e.g. openstack
        :param rabbit_pass: The RabbitMQ password. (string value)
        :param neutron_endpoint: neutron endpoint e.g. `http://CONTROLLER_VIP:9696`
        :param neutron_pass: the password of `neutron` user
        :param nova_pass: the passowrd of `nova` user
        :param cinder_pass: the passowrd of `cinder` user
        :returns: None
        """
        return execute(self._install_manila_share, *args, **kwargs)

