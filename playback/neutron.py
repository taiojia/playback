from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.templates.neutron_conf import conf_neutron_conf
from playback.templates.ml2_conf_ini import conf_ml2_conf_ini
from playback.templates.linuxbridge_agent_ini import conf_linuxbridge_agent_ini
from playback.templates.l3_agent_ini import conf_l3_agent_ini
from playback.templates.dhcp_agent_ini import conf_dhcp_agent_ini
from playback.templates.dnsmasq_neutron_conf import conf_dnsmasq_neutron_conf
from playback.templates.metadata_agent_ini import conf_metadata_agent_ini
from playback import __version__
from playback import common

class Neutron(common.Common):
    """
    Deploy neutron
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    :examples:

        .. code-block:: python

            # create neutron instances
            neutron1 = Neutron(
                user='ubuntu',
                hosts=['controller1']
            )
            neutron2 = Neutron(
                user='ubuntu',
                hosts=['controller2']
            )

            # create neutron database
            neutron1.create_neutron_db(
                root_db_pass='changeme',
                neutron_db_pass='changeme'
            )

            # create service credentials
            neutron1.create_service_credentials(
                os_password='changeme',
                os_auth_url='http://192.168.1.1:35357/v3',
                neutron_pass='changeme',
                public_endpoint='http://192.168.1.1:9696',
                internal_endpoint='http://192.168.1.1:9696',
                admin_endpoint='http://192.168.1.1:9696'
            )

            # install neutron for self-service
            neutron1.install_self_service(
                connection='mysql+pymysql://neutron:changeme@192.168.1.1/neutron',
                rabbit_hosts='controller1,controller2',
                rabbit_user='openstack',
                rabbit_pass='changeme',
                auth_uri='http://192.168.1.1:5000',
                auth_url='http://192.168.1.1:35357',
                neutron_pass='changeme',
                nova_url='http://192.168.1.1:8774/v2.1',
                nova_pass='changeme',
                public_interface='eth1',
                local_ip='192.168.1.2',
                nova_metadata_ip='192.168.1.1',
                metadata_proxy_shared_secret='changeme-changeme-changeme-changeme',
                memcached_servers='controller1:11211,controller2:11211'
                populate=True
            )
            neutron2.install_self_service(
                connection='mysql+pymysql://neutron:changeme@192.168.1.1/neutron',
                rabbit_hosts='controller1,controller2',
                rabbit_user='openstack',
                rabbit_pass='changeme',
                auth_uri='http://192.168.1.1:5000',
                auth_url='http://192.168.1.1:35357',
                neutron_pass='changeme',
                nova_url='http://192.168.1.1:8774/v2.1',
                nova_pass='changeme',
                public_interface='eth1',
                local_ip='192.168.1.3',
                nova_metadata_ip='192.168.1.1',
                metadata_proxy_shared_secret='changeme-changeme-changeme-changeme',
                memcached_servers='controller1:11211,controller2:11211'
            )
    """

    @runs_once
    def _create_neutron_db(self, root_db_pass, neutron_db_pass):
        print red(env.host_string + ' | Create neutron database')
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE neutron;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, neutron_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, neutron_db_pass), shell=False)

    def create_neutron_db(self, *args, **kwargs):
        """
        Create the neutron database and the user named neutron

        :param root_db_pass: the password of openstack database `root` user
        :param neutron_db_pass: the password of `neutron` database user
        :returns: None
        """
        return execute(self._create_neutron_db, *args, **kwargs)

    @runs_once
    def _create_service_credentials(self, os_password, os_auth_url, neutron_pass, public_endpoint, internal_endpoint, admin_endpoint):
        with shell_env(OS_PROJECT_DOMAIN_NAME='default',
                       OS_USER_DOMAIN_NAME='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2'):
            print red(env.host_string + ' | Create the neutron user')
            sudo('openstack user create --domain default --password {0} neutron'.format(neutron_pass))
            print red(env.host_string + ' | Add the admin role to the neutron user and service project')
            sudo('openstack role add --project service --user neutron admin')
            print red(env.host_string + ' | Create the neutron service entity')
            sudo('openstack service create --name neutron --description "OpenStack Networking" network')
            print red(env.host_string + ' | Create the network service API endpoints')
            sudo('openstack endpoint create --region RegionOne network public {0}'.format(public_endpoint))
            sudo('openstack endpoint create --region RegionOne network internal {0}'.format(internal_endpoint))
            sudo('openstack endpoint create --region RegionOne network admin {0}'.format(admin_endpoint))
    
    def create_service_credentials(self, *args, **kwargs):
        """
        create the neutron service credentials

        :param os_password: the password of openstack `admin` user
        :param os_auth_url: keystone endpoint url e.g. `http://CONTROLLER_VIP:35357/v3`
        :param neutron_pass: the password of `neutron` user
        :param public_endpoint: public endpoint for neutron service e.g. `http://CONTROLLER_VIP:9696`
        :param internal_endpoint: internal endpoint for neutron service e.g. `http://CONTROLLER_VIP:9696`
        :param admin_endpoint: admin endpoint for neutron service e.g. `http://CONTROLLER_VIP:9696`
        :returns: None
        """
        return execute(self._create_service_credentials, *args, **kwargs)

    def _install_self_service(self, connection, rabbit_hosts, rabbit_user, rabbit_pass, auth_uri, auth_url, neutron_pass, nova_url, nova_pass, public_interface, local_ip, nova_metadata_ip, metadata_proxy_shared_secret, memcached_servers, populate):
        print red(env.host_string + ' | Install the components')
        sudo('apt-get update')
        # Remove neutron-plugin-linuxbridge-agent and conntrack
        #sudo('apt-get -y install neutron-server neutron-plugin-ml2 neutron-plugin-linuxbridge-agent neutron-l3-agent neutron-dhcp-agent neutron-metadata-agent python-neutronclient conntrack')
        sudo('apt-get -y install neutron-server neutron-plugin-ml2 neutron-linuxbridge-agent neutron-l3-agent neutron-dhcp-agent neutron-metadata-agent')

        print red(env.host_string + ' | Update /etc/neutron/neutron.conf')
        with open('tmp_neutron_conf_'+env.host_string, 'w') as f:
            f.write(conf_neutron_conf)
        files.upload_template(filename='tmp_neutron_conf_'+env.host_string,
                              destination='/etc/neutron/neutron.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'connection': connection,
                                       'rabbit_hosts': rabbit_hosts,
                                       'rabbit_user': rabbit_user, 
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'neutron_password': neutron_pass,
                                       'nova_url': nova_url,
                                       'password': nova_pass,
                                       'memcached_servers': memcached_servers})
        os.remove('tmp_neutron_conf_'+env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/plugins/ml2/ml2_conf.ini')
        with open('ml2_conf_ini_' + env.host_string, 'w') as f:
            f.write(conf_ml2_conf_ini)
        files.upload_template(filename='ml2_conf_ini_'+env.host_string,
                              destination='/etc/neutron/plugins/ml2/ml2_conf.ini',
                              use_sudo=True, backup=True)    
        os.remove('ml2_conf_ini_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/plugins/ml2/linuxbridge_agent.ini')
        with open('tmp_linuxbridge_agent_ini_' + env.host_string, 'w') as f:
            f.write(conf_linuxbridge_agent_ini)
        files.upload_template(filename='tmp_linuxbridge_agent_ini_'+env.host_string,
                              destination='/etc/neutron/plugins/ml2/linuxbridge_agent.ini',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'public_interface': public_interface,
                                       'local_ip': local_ip})
        os.remove('tmp_linuxbridge_agent_ini_'+env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/l3_agent.ini')
        with open('tmp_l3_agent_ini_' + env.host_string, 'w') as f:
            f.write(conf_l3_agent_ini)
        files.upload_template(filename='tmp_l3_agent_ini_' + env.host_string,
                              destination='/etc/neutron/l3_agent.ini',
                              backup=True,
                              use_sudo=True)
        os.remove('tmp_l3_agent_ini_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/dhcp_agent.ini')
        with open('tmp_dhcp_agent_ini_' + env.host_string, 'w') as f:
            f.write(conf_dhcp_agent_ini)
        files.upload_template(filename='tmp_dhcp_agent_ini_' + env.host_string,
                              destination='/etc/neutron/dhcp_agent.ini',
                              backup=True,
                              use_sudo=True)
        os.remove('tmp_dhcp_agent_ini_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/dnsmasq-neutron.conf')
        with open('tmp_dnsmasq_neutron_conf_' + env.host_string, 'w') as f:
            f.write(conf_dnsmasq_neutron_conf)
        files.upload_template(filename='tmp_dnsmasq_neutron_conf_' + env.host_string,
                              destination='/etc/neutron/dnsmasq-neutron.conf',
                              backup=True,
                              use_sudo=True)
        os.remove('tmp_dnsmasq_neutron_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/metadata_agent.ini')
        with open('tmp_metadata_agent_ini_' + env.host_string, 'w') as f:
            f.write(conf_metadata_agent_ini)
        files.upload_template(filename='tmp_metadata_agent_ini_' + env.host_string,
                              destination='/etc/neutron/metadata_agent.ini',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': neutron_pass,
                                       'nova_metadata_ip': nova_metadata_ip,
                                       'metadata_proxy_shared_secret': metadata_proxy_shared_secret})
        os.remove('tmp_metadata_agent_ini_' + env.host_string)

        if populate:
            print red(env.host_string + ' | Populate the database')
            sudo('su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron', shell=False)

        print red(env.host_string + ' | Restart services')
        sudo('service nova-api restart', warn_only=True)
        sudo('service neutron-server restart')
        sudo('service neutron-linuxbridge-agent restart')
        sudo('service neutron-dhcp-agent restart')
        sudo('service neutron-metadata-agent restart')
        sudo('service neutron-l3-agent restart')
        print red(env.host_string + ' | Remove the SQLite database file')
        sudo('rm -f /var/lib/neutron/neutron.sqlite', warn_only=True)

    def install_self_service(self, *args, **kwargs):
        """
        Install neutron for self-service

        :param connection: The SQLAlchemy connection string to use to connect to the database. (string value) e.g. `mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron`
        :param rabbit_hosts: RabbitMQ HA cluster host:port pairs. (list value) e.g. `CONTROLLER1,CONTROLLER2`
        :param rabbit_user: The RabbitMQ userid. (string value) e.g. `openstack`
        :param rabbit_pass: The RabbitMQ password. (string value)
        :param auth_uri: Complete public Identity API endpoint. (string value) e.g. `http://CONTROLLER_VIP:5000`
        :param auth_url: keystone admin endpoint e.g. `http://CONTROLLER_VIP:35357`
        :param neutron_pass: the password of `neutron` user
        :param nova_url: URL for connection to nova (Only supports one nova region currently) e.g. `http://CONTROLLER_VIP:8774/v2.1`
        :param nova_pass: passowrd of `nova` user
        :param public_interface: public interface e.g. `eth1`
        :param local_ip: underlying physical network interface that handles overlay networks(uses the management interface IP) (ip address value)
        :param nova_metadata_ip:  IP address used by Nova metadata server. (string value) e.g. `CONTROLLER_VIP`
        :param metadata_proxy_shared_secret: When proxying metadata requests, Neutron signs the Instance-ID header with a shared secret to prevent spoofing. You may select any string for a secret, but it must match here and in the configuration used by the Nova Metadata Server. NOTE: Nova uses the same config key, but in [neutron] section. (string value)
        :param memcached_servers: Optionally specify a list of memcached server(s) to use for caching. (list value) e.g. `CONTROLLER1:11211,CONTROLLER2:11211`
        :param populate: populate the neutron database
        :returns: None
        """
        return execute(self._install_self_service, *args, **kwargs)

