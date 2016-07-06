from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
from playback.templates.proxy_server_conf import conf_proxy_server_conf
from playback.templates.swift_conf import conf_swift_conf
from playback import __version__
from playback import common

class Swift(common.Common):

    @runs_once
    def _create_service_credentials(self, os_password, os_auth_url, swift_pass, public_endpoint, internal_endpoint, admin_endpoint):
        with shell_env(OS_PROJECT_DOMAIN_NAME='default',
                       OS_USER_DOMAIN_NAME='default',
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
            sudo('openstack endpoint create --region RegionOne object-store public {0}'.format(public_endpoint))
            sudo('openstack endpoint create --region RegionOne object-store internal {0}'.format(internal_endpoint))
            sudo('openstack endpoint create --region RegionOne object-store admin {0}'.format(admin_endpoint))

    def _install(self, auth_uri, auth_url, swift_pass, memcached_servers, with_memcached):
        print red(env.host_string + ' | Install swift proxy')
        sudo('apt-get update')
        sudo('apt-get -y install swift swift-proxy python-swiftclient python-keystoneclient python-keystonemiddleware')
        # Install memcached
        if with_memcached:
            sudo('apt-get -y install memcached')
            # Configure /etc/memcached.conf to listen 0.0.0.0
            with open('tmp_memcached_conf_'+env.host_string, 'w') as f:
                f.write(conf_memcached_conf)
            files.upload_template(filename='tmp_memcached_conf_'+env.host_string,
                                    destination='/etc/memcached.conf',
                                    use_sudo=True,
                                    backup=True)
            os.remove('tmp_memcached_conf_'+env.host_string)
            sudo('service memcached restart')

        sudo('mkdir /etc/swift')

        print red(env.host_string + ' | Update /etc/swift/proxy-server.conf')
        with open('tmp_proxy_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_proxy_server_conf)
        files.upload_template(filename='tmp_proxy_server_conf_' + env.host_string,
                              destination='/etc/swift/proxy-server.conf',
                              use_sudo=True,
                              use_jinja=True,
                              backup=True,
                              context={'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'swift_pass': swift_pass,
                                       'memcached_servers': memcached_servers})
        os.remove('tmp_proxy_server_conf_' + env.host_string)



    def _finalize_install(self, swift_hash_path_suffix, swift_hash_path_prefix):
        print red(env.host_string + ' | Update /etc/swift/swift.conf')
        with open('tmp_swift_conf_' + env.host_string, 'w') as f:
            f.write(conf_swift_conf)
        files.upload_template(filename='tmp_swift_conf_' + env.host_string,
                              destination='/etc/swift/swift.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
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

def create_service_credentials_subparser(s):
    create_service_credentials_parser = s.add_parser('create-service-credentials', help='create the swift service credentials')
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
    create_service_credentials_parser.add_argument('--swift-pass',
                                                    help='password for swift user',
                                                    action='store',
                                                    default=None,
                                                    dest='swift_pass')
    create_service_credentials_parser.add_argument('--public-endpoint',
                                                    help=r'public endpoint for swift service e.g. "http://CONTROLLER_VIP:8080/v1/AUTH_%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='public_endpoint')
    create_service_credentials_parser.add_argument('--internal-endpoint',
                                                    help=r'internal endpoint for swift service e.g. "http://CONTROLLER_VIP:8080/v1/AUTH_%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='internal_endpoint')
    create_service_credentials_parser.add_argument('--admin-endpoint',
                                                    help='admin endpoint for swift service e.g. http://CONTROLLER_VIP:8080/v1',
                                                    action='store',
                                                    default=None,
                                                    dest='admin_endpoint')
    return create_service_credentials_parser

def install_subparser(s):
    install_parser = s.add_parser('install',help='install swift proxy')
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
    install_parser.add_argument('--swift-pass',
                                help='password for swift user',
                                action='store',
                                default=None,
                                dest='swift_pass')
    install_parser.add_argument('--memcached-servers',
                                help='memcache servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                                action='store',
                                default=None,
                                dest='memcached_servers')
    install_parser.add_argument('--with-memcached',
                                help='install memcached on remote server, if you have other memcached on the controller node, you can use --memcached-sersers',
                                action='store_true',
                                default=False,
                                dest='with_memcached')
    return install_parser

def finalize_install_subparser(s):
    finalize_install_parser = s.add_parser('finalize-install', help='finalize swift installation')
    finalize_install_parser.add_argument('--swift-hash-path-suffix',
                                        help='swift_hash_path_suffix and swift_hash_path_prefix are used as part of the hashing algorithm when determining data placement in the cluster. These values should remain secret and MUST NOT change once a cluster has been deployed',
                                        action='store',
                                        default=None,
                                        dest='swift_hash_path_suffix')
    finalize_install_parser.add_argument('--swift-hash-path-prefix',
                                        help='swift_hash_path_suffix and swift_hash_path_prefix are used as part of the hashing algorithm when determining data placement in the cluster. These values should remain secret and MUST NOT change once a cluster has been deployed',
                                        action='store',
                                        default=None,
                                        dest='swift_hash_path_prefix')
    return finalize_install_parser

def make_target(args):
    try:
        target = Swift(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    return target

def create_service_credentials(args):
    target = make_target(args)
    execute(target._create_service_credentials,
            args.os_password, 
            args.os_auth_url, 
            args.swift_pass, 
            args.public_endpoint,
            args.internal_endpoint,
            args.admin_endpoint)

def install(args):
    target = make_target(args)
    execute(target._install,
            args.auth_uri, 
            args.auth_url, 
            args.swift_pass, 
            args.memcached_servers,
            args.with_memcached)

def finalize_install(args):
    target = make_target(args)
    execute(target._finalize_install,
            args.swift_hash_path_suffix, 
            args.swift_hash_path_prefix)
                
def parser():
    p = argparse.ArgumentParser(prog='swift-deploy', description=cli_description+'this command used for provision Swift')
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

    def create_service_credentials_f(args):
        create_service_credentials(args)
    create_service_credentials_parser = create_service_credentials_subparser(s)
    create_service_credentials_parser.set_defaults(func=create_service_credentials_f)

    def install_f(args):
        install(args)
    install_parser = install_subparser(s)
    install_parser.set_defaults(func=install_f)

    def finalize_install_f(args):
        finalize_install(args)
    finalize_install_parser = finalize_install_subparser(s)
    finalize_install_parser.set_defaults(func=finalize_install_f)

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
