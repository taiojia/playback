from fabric.api import *
from fabric.contrib import files
from fabric.tasks import Task
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
from playback.swift_conf import conf_proxy_server_conf, conf_swift_conf
from playback import __version__

parser = argparse.ArgumentParser(description=cli_description+'this command used for provision Swift')
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
subparsers = parser.add_subparsers(dest='subparser_name')
create_service_credentials = subparsers.add_parser('create-service-credentials',
                                                   help='create the swift service credentials')
create_service_credentials.add_argument('--os-password',
                                        help='the password for admin user',
                                        action='store',
                                        default=None,
                                        dest='os_password')
create_service_credentials.add_argument('--os-auth-url',
                                        help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                                        action='store',
                                        default=None,
                                        dest='os_auth_url')
create_service_credentials.add_argument('--swift-pass',
                                        help='password for swift user',
                                        action='store',
                                        default=None,
                                        dest='swift_pass')
create_service_credentials.add_argument('--public-internal-endpoint',
                                        help='public and internal endpoint for swift service e.g. http://CONTROLLER_VIP:8080/v1/AUTH_%%\(tenant_id\)s',
                                        action='store',
                                        default=None,
                                        dest='public_internal_endpoint')
create_service_credentials.add_argument('--admin-endpoint',
                                        help='admin endpoint for swift service e.g. http://CONTROLLER_VIP:8080/v1',
                                        action='store',
                                        default=None,
                                        dest='admin_endpoint')
install = subparsers.add_parser('install',
                                help='install swift proxy')
install.add_argument('--auth-uri',
                    help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                    action='store',
                    default=None,
                    dest='auth_uri')
install.add_argument('--auth-url',
                    help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                    action='store',
                    default=None,
                    dest='auth_url')
install.add_argument('--swift-pass',
                    help='password for swift user',
                    action='store',
                    default=None,
                    dest='swift_pass')
install.add_argument('--memcache-servers',
                    help='memcache servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                    action='store',
                    default=None,
                    dest='memcache_servers')
finalize_install = subparsers.add_parser('finalize-install',
                                         help='finalize swift installation')
finalize_install.add_argument('--swift-hash-path-suffix',
                              help='swift_hash_path_suffix and swift_hash_path_prefix are used as part of the hashing algorithm when determining data placement in the cluster. These values should remain secret and MUST NOT change once a cluster has been deployed',
                              action='store',
                              default=None,
                              dest='swift_hash_path_suffix')
finalize_install.add_argument('--swift-hash-path-prefix',
                              help='swift_hash_path_suffix and swift_hash_path_prefix are used as part of the hashing algorithm when determining data placement in the cluster. These values should remain secret and MUST NOT change once a cluster has been deployed',
                              action='store',
                              default=None,
                              dest='swift_hash_path_prefix')

class Swift(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(Swift, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _create_service_credentials(self, os_password, os_auth_url, swift_pass, public_internal_endpoint, admin_endpoint):
        with shell_env(OS_PROJECT_DOMAIN_ID='default',
                       OS_USER_DOMAIN_ID='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2',
                       OS_AUTH_VERSION='3'):
            print red(env.host_string + ' | Create the swift user')
            sudo('openstack user create --domain default --password {0} swift'.format(swift_pass))
            print red(env.host_string + ' | Add the admin role to the swift user and service project')
            sudo('openstack role add --project service --user swift admin')
            print red(env.host_string + ' | Create the swift service entity')
            sudo('openstack service create --name swift --description "OpenStack Object Storage" object-store')
            print red(env.host_string + ' | Create the Object Storage service API endpoints')
            sudo('openstack endpoint create --region RegionOne object-store public {0}'.format(public_internal_endpoint))
            sudo('openstack endpoint create --region RegionOne object-store internal {0}'.format(public_internal_endpoint))
            sudo('openstack endpoint create --region RegionOne object-store admin {0}'.format(admin_endpoint))

    def _install(self, auth_uri, auth_url, swift_pass, memcache_servers):
        print red(env.host_string + ' | Install swift proxy')
        sudo('apt-get update')
        sudo('apt-get -y install swift swift-proxy python-swiftclient python-keystoneclient python-keystonemiddleware memcached')
        sudo('mkdir /etc/swift')

        print red(env.host_string + ' | Update /etc/swift/proxy-server.conf')
        with open('tmp_proxy_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_proxy_server_conf)
        files.upload_template(filename='tmp_proxy_server_conf_' + env.host_string,
                              destination='/etc/swift/proxy-server.conf',
                              use_sudo=True,
                              use_jinja=True,
                              context={'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'swift_pass': swift_pass,
                                       'memcache_servers': memcache_servers})
        os.remove('tmp_proxy_server_conf_' + env.host_string)

    def _finalize_install(self, swift_hash_path_suffix, swift_hash_path_prefix):
        print red(env.host_string + ' | Update /etc/swift/swift.conf')
        with open('tmp_swift_conf_' + env.host_string, 'w') as f:
            f.write(conf_swift_conf)
        files.upload_template(filename='tmp_swift_conf_' + env.host_string,
                              destination='/etc/swift/swift.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'swift_hash_path_suffix': swift_hash_path_suffix,
                                       'swift_hash_path_prefix': swift_hash_path_prefix})
        os.remove('tmp_swift_conf_' + env.host_string)
        print red(env.host_string + ' | On all nodes, ensure proper ownership of the configuration directory')
        sudo('chown -R root:swift /etc/swift')
        print red(env.host_string + ' | On the controller node and any other nodes running the proxy service, restart the Object Storage proxy service including its dependencies')
        sudo('service memcached restart', warn_only=True)
        sudo('service swift-proxy restart', warn_only=True)
        print red(env.host_string + ' | On the storage nodes, start the Object Storage services')
        sudo('swift-init all start', warn_only=True)



def main():
    try:
        target = Swift(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')
        parser.print_help()
        sys.exit(1)

    if args.subparser_name == 'create-service-credentials':
        execute(target._create_service_credentials,
                args.os_password, 
                args.os_auth_url, 
                args.swift_pass, 
                args.public_internal_endpoint, 
                args.admin_endpoint)
    if args.subparser_name == 'install':
        execute(target._install,
                args.auth_uri, 
                args.auth_url, 
                args.swift_pass, 
                args.memcache_servers)
    if args.subparser_name == 'finalize-install':
        execute(target._finalize_install,
                args.swift_hash_path_suffix, 
                args.swift_hash_path_prefix)

if __name__ == '__main__':
    main()

