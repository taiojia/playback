from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
from playback.templates.nova_conf import conf_nova_conf
from playback import __version__
from playback import common

class Nova(common.Common):

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
        return execute(self._install_nova, *args, **kwargs)

def create_nova_db_subparser(s):
    create_nova_db_parser = s.add_parser('create-nova-db',
                                        help='create the nova and nova_api database')
    create_nova_db_parser.add_argument('--root-db-pass', 
                                        help='the MySQL database root passowrd',
                                        action='store', 
                                        default=None, 
                                        dest='root_db_pass')
    create_nova_db_parser.add_argument('--nova-db-pass', 
                                        help='nova and nova_api database passowrd',
                                        action='store', 
                                        default=None, 
                                        dest='nova_db_pass')
    return create_nova_db_parser

def create_service_credentials_subparser(s):
    create_service_credentials_parser = s.add_parser('create-service-credentials', help='create the nova service credentials',)
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
    create_service_credentials_parser.add_argument('--nova-pass',
                                                    help='passowrd for nova user',
                                                    action='store',
                                                    default=None,
                                                    dest='nova_pass')
    create_service_credentials_parser.add_argument('--public-endpoint',
                                                    help=r'public endpoint for nova service e.g. "http://CONTROLLER_VIP:8774/v2.1/%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='public_endpoint')
    create_service_credentials_parser.add_argument('--internal-endpoint',
                                                    help=r'internal endpoint for nova service e.g. "http://CONTROLLER_VIP:8774/v2.1/%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='internal_endpoint')
    create_service_credentials_parser.add_argument('--admin-endpoint',
                                                    help=r'admin endpoint for nova service e.g. "http://CONTROLLER_VIP:8774/v2.1/%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='admin_endpoint')
    return create_service_credentials_parser
    
def install_subparser(s):
    install_parser = s.add_parser('install',help='install nova')
    install_parser.add_argument('--connection',
                                help='mysql nova database connection string e.g. mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova',
                                action='store',
                                default=None,
                                dest='connection')
    install_parser.add_argument('--api-connection',
                                help='mysql nova_api database connection string e.g. mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova_api',
                                action='store',
                                default=None,
                                dest='api_connection')
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
    install_parser.add_argument('--nova-pass',
                                help='passowrd for nova user',
                                action='store',
                                default=None,
                                dest='nova_pass')
    install_parser.add_argument('--my-ip',
                                help='the host management ip',
                                action='store',
                                default=None,
                                dest='my_ip')
    install_parser.add_argument('--memcached-servers',
                                help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                                action='store',
                                default=None,
                                dest='memcached_servers')
    install_parser.add_argument('--rabbit-hosts',
                                help='rabbit hosts e.g. CONTROLLER1,CONTROLLER2',
                                action='store',
                                default=None,
                                dest='rabbit_hosts')
    install_parser.add_argument('--rabbit-user',
                                help='the user for rabbit openstack user, default openstack',
                                action='store',
                                default='openstack',
                                dest='rabbit_user')
    install_parser.add_argument('--rabbit-pass',
                                help='the password for rabbit openstack user',
                                action='store',
                                default=None,
                                dest='rabbit_pass')
    install_parser.add_argument('--glance-api-servers',
                                help='glance host e.g. http://CONTROLLER_VIP:9292',
                                action='store',
                                default=None,
                                dest='glance_api_servers')
    install_parser.add_argument('--neutron-endpoint',
                                help='neutron endpoint e.g. http://CONTROLLER_VIP:9696',
                                action='store',
                                default=None,
                                dest='neutron_endpoint')
    install_parser.add_argument('--neutron-pass',
                                help='the password for neutron user',
                                action='store',
                                default=None,
                                dest='neutron_pass')
    install_parser.add_argument('--metadata-proxy-shared-secret',
                                help='metadata proxy shared secret',
                                action='store',
                                default=None,
                                dest='metadata_proxy_shared_secret')
    install_parser.add_argument('--populate',
                                help='Populate the nova database',
                                action='store_true',
                                default=False,
                                dest='populate')
    return install_parser
    
def make_target(args):
    try:
        target = Nova(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    return target
    
def create_nova_db(args):
    target = make_target(args)
    target.create_nova_db(args.root_db_pass, args.nova_db_pass)

def create_service_credentials(args):
    target = make_target(args)
    target.create_service_credentials(args.os_password, 
            args.os_auth_url, args.nova_pass, 
            args.public_endpoint, args.internal_endpoint, 
            args.admin_endpoint)

def install(args):
    target = make_target(args)
    target.install_nova(args.connection, args.api_connection, args.auth_uri, args.auth_url,
            args.nova_pass, args.my_ip, args.memcached_servers, args.rabbit_hosts, args.rabbit_user, 
            args.rabbit_pass, args.glance_api_servers, args.neutron_endpoint, args.neutron_pass,
            args.metadata_proxy_shared_secret, args.populate)
        
def parser():
    p = argparse.ArgumentParser(prog='nova-deploy', description=cli_description+'this command used for provision Nova')
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

    s = p.add_subparsers(dest="subparser_name")
    
    def create_nova_db_f(args):
        create_nova_db(args)
    create_nova_db_parser = create_nova_db_subparser(s)
    create_nova_db_parser.set_defaults(func=create_nova_db_f)
    
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