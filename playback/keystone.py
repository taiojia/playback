from fabric.api import *
from fabric.contrib import files
import os
import argparse
import sys
from playback.cli import cli_description
from playback import __version__
from playback.keystone_conf import conf_keystone_conf, conf_wsgi_keystone_conf, conf_keystone_paste_ini

parser = argparse.ArgumentParser(description=cli_description+'this command used for provision Keystone')
parser.add_argument('-v', '--version',
                   action='version',
                   version=__version__)
parser.add_argument('--user', 
                    help='the target user', 
                    action='store', 
                    default='ubuntu', 
                    dest='user')
parser.add_argument('--hosts', 
                    help='the target address', 
                    action='store', 
                    dest='hosts')
subparsers = parser.add_subparsers(dest="subparser_name")
create_keystone_db = subparsers.add_parser('create-keystone-db',
                                           help='create the keystone database', )
create_keystone_db.add_argument('--root-db-pass', 
                    help='the openstack database root passowrd',
                   action='store', 
                   default=None, 
                   dest='root_db_pass')
create_keystone_db.add_argument('--keystone-db-pass', 
                    help='keystone db passowrd',
                    action='store', 
                    default=None, 
                    dest='keystone_db_pass')

install = subparsers.add_parser('install',
                                help='install keystone')
install.add_argument('--admin_token',
                    help='define the value of the initial administration token',
                    action='store',
                    default=None,
                    dest='admin_token')
install.add_argument('--connection',
                    help='database connection string e.g. mysql+pymysql://keystone:PASS@CONTROLLER_VIP/keystone',
                    action='store',
                    default=None,
                    dest='connection')
install.add_argument('--memcache_servers',
                    help='memcached servers. e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                    action='store',
                    default=None,
                    dest='memcache_servers')
install.add_argument('--populate',
                    help='populate the keystone database',
                    action='store_true',
                    default=False,
                    dest='populate')

create_entity_and_endpoint = subparsers.add_parser('create-entity-and-endpoint',
                                                   help='create the service entity and API endpoints',)
create_entity_and_endpoint.add_argument('--os-token',
                                        help='the admin token',
                                        action='store',
                                        default=None,
                                        dest='os_token')
create_entity_and_endpoint.add_argument('--os-url',
                                        help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                                        action='store',
                                        default=None,
                                        dest='os_url')
create_entity_and_endpoint.add_argument('--public-endpoint',
                                        help='the public endpoint e.g. http://CONTROLLER_VIP:5000/v2.0',
                                        action='store',
                                        default=None,
                                        dest='public_endpoint')
create_entity_and_endpoint.add_argument('--internal-endpoint',
                                        help='the internal endpoint e.g. http://CONTROLLER_VIP:5000/v2.0',
                                        action='store',
                                        default=None,
                                        dest='internal_endpoint')
create_entity_and_endpoint.add_argument('--admin-endpoint',
                                        help='the admin endpoint e.g. http://CONTROLLER_VIP:35357/v2.0',
                                        action='store',
                                        default=None,
                                        dest='admin_endpoint')

create_projects_users_roles = subparsers.add_parser('create-projects-users-roles',
                                                    help='create an administrative and demo project, user, and role for administrative and testing operations in your environment')
create_projects_users_roles.add_argument('--os-token',
                                        help='the admin token',
                                        action='store',
                                        default=None,
                                        dest='os_token')
create_projects_users_roles.add_argument('--os-url',
                                        help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                                        action='store',
                                        default=None,
                                        dest='os_url')
create_projects_users_roles.add_argument('--admin-pass',
                                        help='passowrd for admin user',
                                        action='store',
                                        default=None,
                                        dest='admin_pass')
create_projects_users_roles.add_argument('--demo-pass',
                                        help='passowrd for demo user',
                                        action='store',
                                        default=None,
                                        dest='demo_pass')


class Keystone(object):
    def __init__(self, user, hosts=None, parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    @serial
    def _create_keystone_db(self, root_db_pass, keystone_db_pass):
        sudo("mysql -uroot -p{root_db_pass} -e \"CREATE DATABASE keystone;\"".format(root_db_pass=root_db_pass), shell=False)
        sudo("mysql -uroot -p{root_db_pass} -e \"GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '{keystone_db_pass}';\"".format(root_db_pass=root_db_pass, 
                                                                                                                                                            keystone_db_pass=keystone_db_pass), shell=False)
        sudo("mysql -uroot -p{root_db_pass} -e \"GRANT ALL PRIVILEGES ON keystone.* TO 'keystone\'@\'%\' IDENTIFIED BY \'{keystone_db_pass}';\"".format(root_db_pass=root_db_pass, 
                                                                                                                                                        keystone_db_pass=keystone_db_pass), shell=False)
    def _install_keystone(self, admin_token, connection, memcache_servers):
        # Disable the keystone service from starting automatically after installation
        sudo('echo "manual" > /etc/init/keystone.override')
        
        sudo("apt-get update")
        sudo("apt-get install keystone apache2 libapache2-mod-wsgi memcached python-memcache -y")

        # Configure /etc/keysone/keystone.conf
        with open('tmp_keystone_conf','w') as f:
            f.write(conf_keystone_conf)
        files.upload_template(filename='tmp_keystone_conf',
                              destination='/etc/keystone/keystone.conf',
                              context={'admin_token': admin_token,
                              'connection': connection,
                              'memcache_servers': memcache_servers,},
                              use_jinja=True,
                              use_sudo=True)
        os.remove('tmp_keystone_conf')

        # Populate the Identity service database
        if args.populate:
            sudo('su -s /bin/sh -c "keystone-manage db_sync" keystone', shell=False)

        # Configure /etc/apache2/sites-available/wsgi-keystone.conf
        with open('tmp_wsgi_keystone_conf', 'w') as f:
            f.write(conf_wsgi_keystone_conf)
        files.upload_template(filename='tmp_wsgi_keystone_conf',
                              destination='/etc/apache2/sites-available/wsgi-keystone.conf',
                              use_sudo=True)
        os.remove('tmp_wsgi_keystone_conf')

        # Enable the Identity service virtual hosts
        sudo('ln -s /etc/apache2/sites-available/wsgi-keystone.conf /etc/apache2/sites-enabled')

        # Add ServerName to apache configuration
        files.append('/etc/apache2/apache2.conf', 'ServerName localhost', use_sudo=True)
        # Restart the Apache HTTP server
        sudo('service apache2 restart')
        
        # Remove the SQLite database file
        sudo('rm -f /var/lib/keystone/keystone.db')

    # Create the service entity and API endpoints
    def _create_entity_and_endpoint(self, os_token, os_url, public_endpoint, internal_endpoint, admin_endpoint):
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} service create --name keystone --description "OpenStack Identity" identity'.format(os_token=os_token, 
                                                                                                                                                   os_url=os_url))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} endpoint create --region RegionOne identity public {public_endpoint}'.format(os_token=os_token, 
                                                                                                                             os_url=os_url, 
                                                                                                                             public_endpoint=public_endpoint))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} endpoint create --region RegionOne identity internal {internal_endpoint}'.format(os_token=os_token, 
                                                                                                                                 os_url=os_url, 
                                                                                                                                 internal_endpoint=internal_endpoint))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} endpoint create --region RegionOne identity admin {admin_endpoint}'.format(os_token=os_token, 
                                                                                                                           os_url=os_url, 
        
                                                                                                                       admin_endpoint=admin_endpoint))

    # Create projects, users, and roles
    def _create_projects_users_roles(self, os_token, os_url, admin_pass, demo_pass):
        # For admin
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} project create --domain default --description "Admin Project" admin'.format(os_token=os_token,
                                                                                                    os_url=os_url))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} user create --domain default --password {admin_pass} admin'.format(os_token=os_token,
                                                                                                    os_url=os_url,
                                                                                                    admin_pass=admin_pass))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role create admin'.format(os_token=os_token,
                                                                                                                      os_url=os_url))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role add --project admin --user admin admin'.format(os_token=os_token,
                                                                                                                                                os_url=os_url))

        # For service
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} project create --domain default --description "Service Project" service'.format(os_token=os_token,
                                                                                                                                                                            os_url=os_url))
        # For demo
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} project create --domain default --description "Demo Project" demo'.format(os_token=os_token,
                                                                                                                                                                      os_url=os_url))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} user create --domain default --password {demo_pass} demo'.format(os_token=os_token,
                                                                                                                                                             os_url=os_url,
                                                                                                                                                             demo_pass=demo_pass))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role create user'.format(os_token=os_token,
                                                                                                                     os_url=os_url))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role add --project demo --user demo user'.format(os_token=os_token,
                                                                                                                                             os_url=os_url))

    def _update_keystone_paste_ini(self):
        """remove admin_token_auth from the [pipeline:public_api], 
        [pipeline:admin_api], and [pipeline:api_v3] sections"""
        with open('tmp_keystone_paste_ini', 'w') as f:
            f.write(conf_keystone_paste_ini)
        files.upload_template(filename='tmp_keystone_paste_ini',
                              destination='/etc/keystone/keystone-paste.ini',
                              use_sudo=True)
        os.remove('tmp_keystone_paste_ini')


def main():
    try:
        target = Keystone(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        parser.print_help()
        sys.exit(1)

    if args.subparser_name == 'create-keystone-db':
        execute(target._create_keystone_db, 
                args.root_db_pass, 
                args.keystone_db_pass)
    if args.subparser_name == 'install':
        execute(target._install_keystone, 
                args.admin_token, 
                args.connection, 
                args.memcache_servers)
    if args.subparser_name == 'create-entity-and-endpoint':
        execute(target._create_entity_and_endpoint, 
                args.os_token,
                args.os_url,
                args.public_endpoint,
                args.internal_endpoint,
                args.admin_endpoint)
    if args.subparser_name == 'create-projects-users-roles':
        execute(target._create_projects_users_roles,
                args.os_token,
                args.os_url,
                args.admin_pass,
                args.demo_pass)
        execute(target._update_keystone_paste_ini)

if __name__ == '__main__':
    main()