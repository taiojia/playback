from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
from playback import __version__
from playback.templates.glance_api_conf import conf_glance_api_conf
from playback.templates.glance_registry_conf import conf_glance_registry_conf
from playback import common

class Glance(common.Common):

    @runs_once
    def _create_glance_db(self, root_db_pass, glance_db_pass):
        """Create the glance database"""
        print red(env.host_string + ' | Create glance database')
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE glance;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, glance_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, glance_db_pass), shell=False)

    def create_glance_db(self, *args, **kwargs):
        execute(self._create_glance_db, *args, **kwargs)

    @runs_once
    def _create_service_credentials(self, os_password, os_auth_url, glance_pass, public_endpoint, internal_endpoint, admin_endpoint):
        with shell_env(OS_PROJECT_DOMAIN_NAME='default',
                       OS_USER_DOMAIN_NAME='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2'):
            print red(env.host_string + ' | Create the glance user')
            sudo('openstack user create --domain default --password {0} glance'.format(glance_pass))
            print red(env.host_string + ' | Add the admin role to the glance user and service project')
            sudo('openstack role add --project service --user glance admin')
            print red(env.host_string + ' | Create the glance service entity')
            sudo('openstack service create --name glance --description "OpenStack Image service" image')
            print red(env.host_string + ' | Create the Image service API endpoints')
            sudo('openstack endpoint create --region RegionOne image public {0}'.format(public_endpoint))
            sudo('openstack endpoint create --region RegionOne image internal {0}'.format(internal_endpoint))
            sudo('openstack endpoint create --region RegionOne image admin {0}'.format(admin_endpoint))

    def create_service_credentials(self, *args, **kwargs):
        execute(self._create_service_credentials, *args, **kwargs)

    def _install_glance(self, connection, auth_uri, auth_url, glance_pass, swift_store_auth_address, memcached_servers, populate):
        print red(env.host_string + ' | Install glance')
        sudo('apt-get update')
        sudo('apt-get -y install glance')

        print red(env.host_string + ' | Update configuration for /etc/glance/glance-api.conf')
        with open("tmp_glance_api_conf_" + env.host_string, "w") as f:
            f.write(conf_glance_api_conf)

        files.upload_template(filename='tmp_glance_api_conf_'+env.host_string,
                              destination='/etc/glance/glance-api.conf',
                              context={'connection': connection,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': glance_pass,
                                       'swift_store_auth_address': swift_store_auth_address,
                                       'swift_store_key': glance_pass,
                                       'memcached_servers': memcached_servers},
                              use_jinja=True,
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_glance_api_conf_' + env.host_string)

        print red(env.host_string + ' | Update configuration for /etc/glance/glance-registry.conf')
        with open('tmp_glance_registry_conf_' + env.host_string, 'w') as f:
            f.write(conf_glance_registry_conf)
        
        files.upload_template(filename='tmp_glance_registry_conf_'+env.host_string,
                              destination='/etc/glance/glance-registry.conf',
                              context={'connection': connection,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': glance_pass,
                                       'memcached_servers': memcached_servers},
                              use_jinja=True,
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_glance_registry_conf_' + env.host_string)
   
        if populate:
            print red(env.host_string + ' | Populate the Image service database')
            sudo('su -s /bin/sh -c "glance-manage db_sync" glance', shell=False)

        
        print red(env.host_string + ' | Restart the Image services')
        sudo('service glance-registry restart')
        sudo('service glance-api restart')

        print red(env.host_string + ' | Remove the SQLite database file')
        sudo('rm -f /var/lib/glance/glance.sqlite')

    def install_glance(self, *args, **kwargs):
        execute(self._install_glance, *args, **kwargs)

def make_target(user, hosts, key_filename, password):
    """
    The deployment instance
    param::
    user: str
    hosts: list
    """
    try:
        target = Glance(user, hosts, key_filename, password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)

    return target

def create_glance_db(args):
    target = make_target(args.user, args.hosts.split(','), args.key_filename, args.password)
    target.create_glance_db(
            args.root_db_pass, 
            args.glance_db_pass)

def create_service_credentials(args):
    target = make_target(args.user, args.hosts.split(','), args.key_filename, args.password)
    target.create_service_credentials(
            args.os_password, 
            args.os_auth_url, 
            args.glance_pass, 
            args.public_endpoint,
            args.internal_endpoint,
            args.admin_endpoint)

def install(args):
    target = make_target(args.user, args.hosts.split(','), args.key_filename, args.password)
    target.install_glance(
            args.connection, 
            args.auth_uri, 
            args.auth_url, 
            args.glance_pass,
            args.swift_store_auth_address,
            args.memcached_servers,
            args.populate)

def parser():
    p = argparse.ArgumentParser(prog='glance-deploy', description=cli_description+'this command used for provision Glance')
    p.add_argument('-v', '--version', action='version', version=__version__)
    p.add_argument('--user', help='the target user', action='store', default='ubuntu', dest='user')
    p.add_argument('--hosts', help='the target address', action='store', dest='hosts')
    p.add_argument('-i', '--key-filename', help='referencing file paths to SSH key files to try when connecting', action='store', dest='key_filename', default=None)
    p.add_argument('--password', help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password', default=None)

    s = p.add_subparsers(dest="subparser_name")

    def create_glance_db_f(args):
        create_glance_db(args)
    create_glance_db_parser = s.add_parser('create-glance-db', help='create the glance database')
    create_glance_db_parser.add_argument('--root-db-pass', 
                                          help='the openstack database root passowrd',
                                          action='store', 
                                          default=None, 
                                          dest='root_db_pass')
    create_glance_db_parser.add_argument('--glance-db-pass', 
                                          help='glance db passowrd',
                                          action='store', 
                                          default=None, 
                                          dest='glance_db_pass')
    create_glance_db_parser.set_defaults(func=create_glance_db)

    def create_service_credentials_f(args):
        create_service_credentials(args)
    create_service_credentials_parser = s.add_parser('create-service-credentials',
                                                   help='create the glance service credentials')
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
    create_service_credentials_parser.add_argument('--glance-pass',
                                                    help='passowrd for glance user',
                                                    action='store',
                                                    default=None,
                                                    dest='glance_pass')
    create_service_credentials_parser.add_argument('--public-endpoint',
                                                    help='public endpoint for glance service e.g. http://CONTROLLER_VIP:9292',
                                                    action='store',
                                                    default=None,
                                                    dest='public_endpoint')
    create_service_credentials_parser.add_argument('--internal-endpoint',
                                                    help='internal endpoint for glance service e.g. http://CONTROLLER_VIP:9292',
                                                    action='store',
                                                    default=None,
                                                    dest='internal_endpoint')
    create_service_credentials_parser.add_argument('--admin-endpoint',
                                                    help='admin endpoint for glance service e.g. http://CONTROLLER_VIP:9292',
                                                    action='store',
                                                    default=None,
                                                    dest='admin_endpoint')
    create_service_credentials_parser.set_defaults(func=create_service_credentials)

    def install_f(args):
        install(args)
    install_parser = s.add_parser('install', help='install glance(default store: ceph)')
    install_parser.add_argument('--connection',
                        help='mysql database connection string e.g. mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance',
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
    install_parser.add_argument('--glance-pass',
                        help='passowrd for glance user',
                        action='store',
                        default=None,
                        dest='glance_pass')
    install_parser.add_argument('--swift-store-auth-address',
                        help='DEPRECATED the address where the Swift authentication service is listening e.g. http://CONTROLLER_VIP:5000/v3/',
                        action='store',
                        default='DEPRECATED_BY_PLAYBACK',
                        dest='swift_store_auth_address')
    install_parser.add_argument('--memcached-servers',
                        help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                        action='store',
                        default=None,
                        dest='memcached_servers')                        
    install_parser.add_argument('--populate',
                        help='populate the glance database',
                        action='store_true',
                        default=False,
                        dest='populate')
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
            sys.exit(1)
    return 1

if __name__ == '__main__':
    main()