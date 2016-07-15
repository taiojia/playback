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

def create_neutron_db_subparser(s):
    create_neutron_db_parser = s.add_parser('create-neutron-db',
                                            help='create the neutron database')
    create_neutron_db_parser.add_argument('--root-db-pass', 
                                            help='the openstack database root passowrd',
                                            action='store', 
                                            default=None, 
                                            dest='root_db_pass')
    create_neutron_db_parser.add_argument('--neutron-db-pass', 
                                            help='neutron db passowrd',
                                            action='store', 
                                            default=None, 
                                            dest='neutron_db_pass')
    return create_neutron_db_parser
    
def create_service_credentials_subparser(s):
    create_service_credentials_parser = s.add_parser('create-service-credentials',
                                                            help='create the neutron service credentials')
    create_service_credentials_parser.add_argument('--os-password',
                                                    help='the password for admin user',
                                                    action='store',
                                                    default=None,
                                                    dest='os_password')
    create_service_credentials_parser.add_argument('--os-auth-url',
                                                    help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                                                    action='store',
                                                    default=None,
                                                    dest='os_auth_url')
    create_service_credentials_parser.add_argument('--neutron-pass',
                                                    help='the password for neutron user',
                                                    action='store',
                                                    default=None,
                                                    dest='neutron_pass')
    create_service_credentials_parser.add_argument('--public-endpoint',
                                                    help='public endpoint for neutron service e.g. http://CONTROLLER_VIP:9696',
                                                    action='store',
                                                    default=None,
                                                    dest='public_endpoint')
    create_service_credentials_parser.add_argument('--internal-endpoint',
                                                    help='internal endpoint for neutron service e.g. http://CONTROLLER_VIP:9696',
                                                    action='store',
                                                    default=None,
                                                    dest='internal_endpoint')
    create_service_credentials_parser.add_argument('--admin-endpoint',
                                                    help='admin endpoint for neutron service e.g. http://CONTROLLER_VIP:9696',
                                                    action='store',
                                                    default=None,
                                                    dest='admin_endpoint')
    return create_service_credentials_parser

def install_subparser(s):
    install_parser = s.add_parser('install', help='install neutron for self-service')
    install_parser.add_argument('--connection',
                        help='mysql database connection string e.g. mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron',
                        action='store',
                        default=None,
                        dest='connection')
    install_parser.add_argument('--auth-uri',
                        help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                        action='store',
                        default=None,
                        dest='auth_uri')
    install_parser.add_argument('--auth-url',
                        help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                        action='store',
                        default=None,
                        dest='auth_url')
    install_parser.add_argument('--rabbit-hosts',
                        help='rabbit hosts e.g. controller1,controller2',
                        action='store',
                        default=None,
                        dest='rabbit_hosts')
    install_parser.add_argument('--rabbit-user',
                        help='the user for rabbit, default openstack',
                        action='store',
                        default='openstack',
                        dest='rabbit_user')
    install_parser.add_argument('--rabbit-pass',
                        help='the password for rabbit openstack user',
                        action='store',
                        default=None,
                        dest='rabbit_pass')
    install_parser.add_argument('--neutron-pass',
                        help='the password for neutron user',
                        action='store',
                        default=None,
                        dest='neutron_pass')
    install_parser.add_argument('--nova-url',
                        help='URL for connection to nova (Only supports one nova region currently) e.g. http://CONTROLLER_VIP:8774/v2.1',
                        action='store',
                        default=None,
                        dest='nova_url')
    install_parser.add_argument('--nova-pass',
                        help='passowrd for nova user',
                        action='store',
                        default=None,
                        dest='nova_pass')
    install_parser.add_argument('--public-interface',
                        help='public interface e.g. eth1',
                        action='store',
                        default=None,
                        dest='public_interface')
    install_parser.add_argument('--local-ip',
                        help=' underlying physical network interface that handles overlay networks(uses the management interface IP)',
                        action='store',
                        default=None,
                        dest='local_ip')
    install_parser.add_argument('--nova-metadata-ip',
                        help='IP address used by Nova metadata server e.g. CONTROLLER_VIP',
                        action='store',
                        default=None,
                        dest='nova_metadata_ip')
    install_parser.add_argument('--metadata-proxy-shared-secret',
                        help='metadata proxy shared secret',
                        action='store',
                        default=None,
                        dest='metadata_proxy_shared_secret')
    install_parser.add_argument('--memcached-servers',
                        help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                        action='store',
                        default=None,
                        dest='memcached_servers')
    install_parser.add_argument('--populate',
                        help='Populate the neutron database',
                        action='store_true',
                        default=False,
                        dest='populate')
    return install_parser

def make_target(args):
    try:
        target = Neutron(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    return target
    
def create_neutron_db(args):
    target = make_target(args)
    target.create_neutron_db(args.root_db_pass, args.neutron_db_pass)

def create_service_credentials(args):
    target = make_target(args)
    target.create_service_credentials(
            args.os_password,
            args.os_auth_url,
            args.neutron_pass,
            args.public_endpoint,
            args.internal_endpoint,
            args.admin_endpoint)
            
def install(args):
    target = make_target(args)
    target.install_self_service(
            args.connection, 
            args.rabbit_hosts, 
            args.rabbit_user, 
            args.rabbit_pass, 
            args.auth_uri, 
            args.auth_url, 
            args.neutron_pass, 
            args.nova_url, 
            args.nova_pass, 
            args.public_interface, 
            args.local_ip, 
            args.nova_metadata_ip, 
            args.metadata_proxy_shared_secret, 
            args.memcached_servers,
            args.populate)
            
def parser():
    p = argparse.ArgumentParser(prog='neutron-deploy', description=cli_description+'this command used for provision Neutron')
    p.add_argument('-v', '--version',
                    action='version',
                    version=__version__)
    p.add_argument('--user', 
                    help='the target user', 
                    action='store', 
                    default='ubuntu', 
                    dest='user')
    p.add_argument('--hosts', 
                    help='the target address', 
                    action='store', 
                    dest='hosts')
    p.add_argument('-i', '--key-filename', help='referencing file paths to SSH key files to try when connecting', action='store', dest='key_filename', default=None)
    p.add_argument('--password', help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password', default=None)

    s = p.add_subparsers(dest='subparser_name')
    
    def create_neutron_db_f(args):
        create_neutron_db(args)
    create_neutron_db_parser = create_neutron_db_subparser(s)
    create_neutron_db_parser.set_defaults(func=create_neutron_db_f)
    
    def create_service_credentials_f(args):
        create_service_credentials(args)
    create_service_credentials_parser = create_service_credentials_subparser(s)
    create_service_credentials_parser.set_defaults(func=create_service_credentials_f)

    def install_f(args):
        install(args)
    install_parser = install_subparser(s)
    install_parser.set_defaults(func=install_f)
    
    return p
    
def main():
    p = parser()
    args = p.parse_args()
    if not hasattr(args, 'func'):
        p.print_help()
    else:
        # XXX on Python 3.3 we get 'args has no func' rather than short help.
        try:
            args.func(args)
            disconnect_all()
            return 0
        except Exception as e:
            sys.stderr.write(e.message)
    return 1

if __name__ == '__main__':
    main()