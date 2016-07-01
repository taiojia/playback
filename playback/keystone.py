from fabric.api import *
from fabric.contrib import files
from fabric.colors import red
from fabric.network import disconnect_all
import os
import argparse
import sys
from playback.cli import cli_description
from playback import __version__
from playback.templates.keystone_conf import conf_keystone_conf
from playback.templates.wsgi_keystone_conf import conf_wsgi_keystone_conf
from playback.templates.keystone_paste_ini import conf_keystone_paste_ini
from playback.templates.memcached_conf import conf_memcached_conf
from playback import common

class Keystone(common.Common):

    @runs_once
    def _create_keystone_db(self, root_db_pass, keystone_db_pass):
        sudo("mysql -uroot -p{root_db_pass} -e \"CREATE DATABASE keystone;\"".format(root_db_pass=root_db_pass), shell=False)
        sudo("mysql -uroot -p{root_db_pass} -e \"GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '{keystone_db_pass}';\"".format(root_db_pass=root_db_pass, 
                                                                                                                                                            keystone_db_pass=keystone_db_pass), shell=False)
        sudo("mysql -uroot -p{root_db_pass} -e \"GRANT ALL PRIVILEGES ON keystone.* TO 'keystone\'@\'%\' IDENTIFIED BY \'{keystone_db_pass}';\"".format(root_db_pass=root_db_pass, 
                                                                                                                                                        keystone_db_pass=keystone_db_pass), shell=False)
    def _install_keystone(self, admin_token, connection, memcached_servers, populate):
        # Disable the keystone service from starting automatically after installation
        sudo('echo "manual" > /etc/init/keystone.override')
        
        sudo("apt-get update")
        sudo("apt-get install keystone apache2 libapache2-mod-wsgi memcached python-memcache -y")

        if self._release() == 'xenial':
            sudo('systemctl stop keystone')
            sudo('update-rc.d keystone disable')

        # Configure /etc/keysone/keystone.conf
        with open('tmp_keystone_conf_'+env.host_string,'w') as f:
            f.write(conf_keystone_conf)
        files.upload_template(filename='tmp_keystone_conf_'+env.host_string,
                              destination='/etc/keystone/keystone.conf',
                              context={'admin_token': admin_token,
                              'connection': connection,
                              'memcached_servers': memcached_servers,},
                              use_jinja=True,
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_keystone_conf_'+env.host_string)

        # Configure /etc/memcached.conf to listen 0.0.0.0
        with open('tmp_memcached_conf_'+env.host_string, 'w') as f:
            f.write(conf_memcached_conf)
        files.upload_template(filename='tmp_memcached_conf_'+env.host_string,
                                destination='/etc/memcached.conf',
                                use_sudo=True,
                                backup=True)
        os.remove('tmp_memcached_conf_'+env.host_string)
        sudo('service memcached restart')

        # Populate the Identity service database
        if populate:
            sudo('su -s /bin/sh -c "keystone-manage db_sync" keystone', shell=False)
            # Initialize Fernet Keys
            sudo('keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone', shell=False)
        


        # Configure /etc/apache2/sites-available/wsgi-keystone.conf
        with open('tmp_wsgi_keystone_conf_'+env.host_string, 'w') as f:
            f.write(conf_wsgi_keystone_conf)
        files.upload_template(filename='tmp_wsgi_keystone_conf_'+env.host_string,
                              destination='/etc/apache2/sites-available/wsgi-keystone.conf',
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_wsgi_keystone_conf_'+env.host_string)

        # Enable the Identity service virtual hosts
        sudo('ln -s /etc/apache2/sites-available/wsgi-keystone.conf /etc/apache2/sites-enabled')

        # Add ServerName to apache configuration
        files.append('/etc/apache2/apache2.conf', 'ServerName localhost', use_sudo=True)
        # Restart the Apache HTTP server
        sudo('service apache2 restart')
        
        # Remove the SQLite database file
        sudo('rm -f /var/lib/keystone/keystone.db')

    # Create the service entity and API endpoints
    @runs_once
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
    @runs_once
    def _create_projects_users_roles(self, os_token, os_url, admin_pass, demo_pass):
        # Create the default domain
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} domain create --description "Default Domain" default'.format(os_token=os_token,
                                                                                                                                                        os_url=os_url))
        # Create the admin project
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} project create --domain default --description "Admin Project" admin'.format(os_token=os_token,
                                                                                                                                                                        os_url=os_url))
        # Create the admin user
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} user create --domain default --password {admin_pass} admin'.format(os_token=os_token,
                                                                                                                                                                os_url=os_url,
                                                                                                                                                                admin_pass=admin_pass))
        # Create the admin role
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role create admin'.format(os_token=os_token,
                                                                                                                      os_url=os_url))
        # Add the admin role to the admin project and user
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role add --project admin --user admin admin'.format(os_token=os_token,
                                                                                                                                                os_url=os_url))

        # Create the service project
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} project create --domain default --description "Service Project" service'.format(os_token=os_token,
                                                                                                                                                                            os_url=os_url))
        # Create the demo project
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} project create --domain default --description "Demo Project" demo'.format(os_token=os_token,
                                                                                                                                                                      os_url=os_url))
        # Create the demo user
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} user create --domain default --password {demo_pass} demo'.format(os_token=os_token,
                                                                                                                                                             os_url=os_url,
                                                                                                                                                             demo_pass=demo_pass))
        # Create the user role
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role create user'.format(os_token=os_token,
                                                                                                                     os_url=os_url))
        # Add the user role to the demo project and user
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role add --project demo --user demo user'.format(os_token=os_token,
                                                                                                                                             os_url=os_url))
    def _update_keystone_paste_ini(self):
        """remove admin_token_auth from the [pipeline:public_api], 
        [pipeline:admin_api], and [pipeline:api_v3] sections"""
        with open('tmp_keystone_paste_ini_'+env.host_string, 'w') as f:
            f.write(conf_keystone_paste_ini)
        files.upload_template(filename='tmp_keystone_paste_ini_'+env.host_string,
                              destination='/etc/keystone/keystone-paste.ini',
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_keystone_paste_ini_'+env.host_string)

def make_target(args):
    try:
        target = Keystone(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        err_hosts = red('No hosts found. Please using --hosts param.')
        sys.stderr.write(err_hosts)
        sys.exit(1)
    
    return target

def create_keystone_db(args):
    target = make_target(args)
    execute(target._create_keystone_db, 
            args.root_db_pass, 
            args.keystone_db_pass)

def install(args):
    target = make_target(args)
    execute(target._install_keystone, 
            args.admin_token, 
            args.connection, 
            args.memcached_servers,
            args.populate)

def create_entity_and_endpoint(args):
    target = make_target(args)
    execute(target._create_entity_and_endpoint, 
        args.os_token,
        args.os_url,
        args.public_endpoint,
        args.internal_endpoint,
        args.admin_endpoint)

def create_projects_users_roles(args):
    target = make_target(args)
    execute(target._create_projects_users_roles,
        args.os_token,
        args.os_url,
        args.admin_pass,
        args.demo_pass)
    execute(target._update_keystone_paste_ini)

def create_keystone_db_subparser(s):
    create_keystone_db_parser = s.add_parser('create-keystone-db', help='create the keystone database', )
    create_keystone_db_parser.add_argument('--root-db-pass', 
                                           help='the openstack database root passowrd',
                                           action='store', 
                                           default=None, 
                                           dest='root_db_pass')
    create_keystone_db_parser.add_argument('--keystone-db-pass', 
                                           help='keystone db passowrd',
                                           action='store', 
                                           default=None, 
                                           dest='keystone_db_pass')
    return create_keystone_db_parser

def install_subparser(s):
    install_parser = s.add_parser('install', help='install keystone')
    install_parser.add_argument('--admin-token',
                                help='define the value of the initial administration token',
                                action='store',
                                default=None,
                                dest='admin_token')
    install_parser.add_argument('--connection',
                                help='database connection string e.g. mysql+pymysql://keystone:PASS@CONTROLLER_VIP/keystone',
                                action='store',
                                default=None,
                                dest='connection')
    install_parser.add_argument('--memcached-servers',
                                help='memcached servers. e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                                action='store',
                                default=None,
                                dest='memcached_servers')
    install_parser.add_argument('--populate',
                                help='populate the keystone database',
                                action='store_true',
                                default=False,
                                dest='populate')
    return install_parser

def create_entity_and_endpoint_subparser(s):
    create_entity_and_endpoint_parser = s.add_parser('create-entity-and-endpoint',
                                                       help='create the service entity and API endpoints',)
    create_entity_and_endpoint_parser.add_argument('--os-token',
                                                    help='the admin token',
                                                    action='store',
                                                    default=None,
                                                    dest='os_token')
    create_entity_and_endpoint_parser.add_argument('--os-url',
                                                    help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                                                    action='store',
                                                    default=None,
                                                    dest='os_url')
    create_entity_and_endpoint_parser.add_argument('--public-endpoint',
                                                    help='the public endpoint e.g. http://CONTROLLER_VIP:5000/v3',
                                                    action='store',
                                                    default=None,
                                                    dest='public_endpoint')
    create_entity_and_endpoint_parser.add_argument('--internal-endpoint',
                                                    help='the internal endpoint e.g. http://CONTROLLER_VIP:5000/v3',
                                                    action='store',
                                                    default=None,
                                                    dest='internal_endpoint')
    create_entity_and_endpoint_parser.add_argument('--admin-endpoint',
                                                    help='the admin endpoint e.g. http://CONTROLLER_VIP:35357/v3',
                                                    action='store',
                                                    default=None,
                                                    dest='admin_endpoint')
    return create_entity_and_endpoint_parser

def create_projects_users_roles_subparser(s):
    create_projects_users_roles_parser = s.add_parser('create-projects-users-roles',
                                                        help='create an administrative and demo project, user, and role for administrative and testing operations in your environment')
    create_projects_users_roles_parser.add_argument('--os-token',
                                                    help='the admin token',
                                                    action='store',
                                                    default=None,
                                                    dest='os_token')
    create_projects_users_roles_parser.add_argument('--os-url',
                                                    help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                                                    action='store',
                                                    default=None,
                                                    dest='os_url')
    create_projects_users_roles_parser.add_argument('--admin-pass',
                                                    help='passowrd for admin user',
                                                    action='store',
                                                    default=None,
                                                    dest='admin_pass')
    create_projects_users_roles_parser.add_argument('--demo-pass',
                                                    help='passowrd for demo user',
                                                    action='store',
                                                    default=None,
                                                    dest='demo_pass')
    return create_projects_users_roles_parser

def parser():
    p = argparse.ArgumentParser(prog='keystone-deploy',description=cli_description+'this command used for provision Keystone')
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

    def create_keystone_db_f(args):
        create_keystone_db(args)
    create_keystone_db_parser = create_keystone_db_subparser(s)
    create_keystone_db_parser.set_defaults(func=create_keystone_db_f)

    def install_f(args):
        install(args)
    install_parser = install_subparser(s)
    install_parser.set_defaults(func=install_f)

    def create_entity_and_endpoint_f(args):
        create_entity_and_endpoint(args)
    create_entity_and_endpoint_parser = create_entity_and_endpoint_subparser(s)
    create_entity_and_endpoint_parser.set_defaults(func=create_entity_and_endpoint_f)

    def create_projects_users_roles_f(args):
        create_projects_users_roles(args)
    create_projects_users_roles_parser = create_projects_users_roles_subparser(s)
    create_projects_users_roles_parser.set_defaults(func=create_projects_users_roles_f)

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
            sys.exit(1)
    return 1

if __name__ == '__main__':
    main()