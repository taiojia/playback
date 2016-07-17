from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
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

    @runs_once
    def _create_neutron_db(self, root_db_pass, neutron_db_pass):
        print red(env.host_string + ' | Create neutron database')
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE neutron;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, neutron_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, neutron_db_pass), shell=False)

    def create_neutron_db(self, *args, **kwargs):
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
        return execute(self._install_self_service, *args, **kwargs)

