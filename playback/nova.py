from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.templates.nova_conf import conf_nova_conf
from playback import __version__
from playback import common

class Nova(common.Common):
    """
    Deploy Nova

    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """
    @runs_once
    def _create_nova_db(self, root_db_pass, nova_db_pass):
        print red(env.host_string + ' | Create nova database')
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE nova;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, nova_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, nova_db_pass), shell=False)
        print red(env.host_string + ' | Create nova_api database')
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE nova_api;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, nova_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, nova_db_pass), shell=False)

    def create_nova_db(self, *args, **kwargs):
        """
        Create the nova and nova_api database and the user named nova

        :param root_db_pass: the password of mysql database root user
        :param nova_db_pass: the password of nova database user
        :returns: None
        """
        return execute(self._create_nova_db, *args, **kwargs)

    @runs_once
    def _create_service_credentials(self, os_password, os_auth_url, nova_pass, public_endpoint, internal_endpoint, admin_endpoint):
        with shell_env(OS_PROJECT_DOMAIN_NAME='default',
                       OS_USER_DOMAIN_NAME='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2'):
            print red(env.host_string + ' | Create the nova user')
            sudo('openstack user create --domain default --password {0} nova'.format(nova_pass))
            print red(env.host_string + ' | Add the admin role to the nova user and service project')
            sudo('openstack role add --project service --user nova admin')
            print red(env.host_string + ' | Create the nova service entity')
            sudo('openstack service create --name nova --description "OpenStack Compute" compute')
            print red(env.host_string + ' | Create the Compute service API endpoints')
            sudo('openstack endpoint create --region RegionOne compute public {0}'.format(public_endpoint))
            sudo('openstack endpoint create --region RegionOne compute internal {0}'.format(internal_endpoint))
            sudo('openstack endpoint create --region RegionOne compute admin {0}'.format(admin_endpoint))

    def create_service_credentials(self, *args, **kwargs):
        r"""
        Create the nova service credentials

        :param os_password: the password of openstack `admin` user
        :param os_auth_url: keystone endpoint url e.g. `http://CONTROLLER_VIP:35357/v3`
        :param nova_pass: passowrd of `nova` user
        :param public_endpoint: public endpoint for nova service e.g. `http://CONTROLLER_VIP:8774/v2.1/%\\(tenant_id\\)s`
        :param internal_endpoint: internal endpoint for nova service e.g. `http://CONTROLLER_VIP:8774/v2.1/%\\(tenant_id\\)s`
        :param admin_endpoint: admin endpoint for nova service e.g. `http://CONTROLLER_VIP:8774/v2.1/%\\(tenant_id\\)s`
        :returns: None
        """
        return execute(self._create_service_credentials, *args, **kwargs)

    def _install_nova(self, connection, api_connection, auth_uri, auth_url, nova_pass, my_ip, memcached_servers, rabbit_hosts, rabbit_user, rabbit_pass, glance_api_servers, neutron_endpoint, neutron_pass, metadata_proxy_shared_secret, populate):
        print red(env.host_string + ' | Install nova-api nova-cert nova-conductor nova-consoleauth nova-novncproxy nova-scheduler')
        sudo('apt-get update')
        # nova-cert deprecated in mitaka
        sudo('apt-get -y install nova-api nova-conductor nova-consoleauth nova-novncproxy nova-scheduler')

        print red(env.host_string + ' | Update configuration for /etc/nova/nova.conf')
        with open("tmp_nova_conf_" + env.host_string, "w") as f:
            f.write(conf_nova_conf)

        files.upload_template(filename='tmp_nova_conf_'+env.host_string,
                              destination='/etc/nova/nova.conf',
                              context={'connection': connection,
                                       'api_connection': api_connection,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': nova_pass,
                                       'my_ip': my_ip,
                                       'memcached_servers': memcached_servers,
                                       'rabbit_hosts': rabbit_hosts,
                                       'rabbit_user': rabbit_user,
                                       'rabbit_password': rabbit_pass,
                                       'api_servers': glance_api_servers,
                                       'url': neutron_endpoint,
                                       'neutron_pass': neutron_pass,
                                       'metadata_proxy_shared_secret': metadata_proxy_shared_secret
                                       },
                              use_jinja=True,
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_nova_conf_' + env.host_string)

        if populate and env.host_string == self.hosts[0]:
            print red(env.host_string + ' | Populate the nova_api database:')
            sudo('su -s /bin/sh -c "nova-manage api_db sync" nova', shell=False)
            print red(env.host_string + ' | Populate the nova database:')
            sudo('su -s /bin/sh -c "nova-manage db sync" nova', shell=False)

        print red(env.host_string + ' | Restart the Nova services')
        sudo('service nova-api restart')
        # nova-cert deprecated in mitaka
        #sudo('service nova-cert restart')
        sudo('service nova-consoleauth restart')
        sudo('service nova-scheduler restart')
        sudo('service nova-conductor restart')
        sudo('service nova-novncproxy restart')
         
        print red(env.host_string + ' | Remove the SQLite database file')
        sudo('rm -f /var/lib/nova/nova.sqlite')

    def install_nova(self, *args, **kwargs):
        """
        Install nova

        :param connection: mysql nova database connection string e.g. `mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova`
        :param api_connection: mysql nova_api database connection string e.g. `mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova_api`
        :param auth_uri: keystone internal endpoint e.g. `http://CONTROLLER_VIP:5000`
        :param auth_url: keystone admin endpoint e.g. `http://CONTROLLER_VIP:35357`
        :param nova_pass: passowrd of `nova` user
        :param my_ip: the host management ip
        :param memcached_servers: memcached servers e.g. `CONTROLLER1:11211,CONTROLLER2:11211`
        :param rabbit_hosts: rabbit hosts e.g. `CONTROLLER1,CONTROLLER2`
        :param rabbit_user: the user of rabbit e.g. `openstack`
        :param rabbit_pass: the password of `rabbit_user`
        :param glance_api_servers: glance host e.g. `http://CONTROLLER_VIP:9292`
        :param neutron_endpoint: neutron endpoint e.g. `http://CONTROLLER_VIP:9696`
        :param neutron_pass: the password of `neutron` user
        :param metadata_proxy_shared_secret: metadata proxy shared secret
        :param populate: populate the nova database
        :returns: None
        """
        return execute(self._install_nova, *args, **kwargs)

