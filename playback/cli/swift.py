import sys
import logging
from playback.api import Swift
from cliff.command import Command


def make_target(args):
    try:
        target = Swift(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
        sys.exit(1)
    return target

def create_service_credentials(args):
    target = make_target(args)
    target.create_service_credentials(
            args.os_password,
            args.os_auth_url,
            args.swift_pass,
            args.public_endpoint,
            args.internal_endpoint,
            args.admin_endpoint)

def install(args):
    target = make_target(args)
    target.install(
            args.auth_uri,
            args.auth_url,
            args.swift_pass,
            args.memcached_servers,
            args.with_memcached)

def finalize_install(args):
    target = make_target(args)
    target.finalize_install(
            args.swift_hash_path_suffix,
            args.swift_hash_path_prefix)


class CreateServiceCredentials(Command):
    """create the swift service credentials"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateServiceCredentials, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--os-password',
                            help='the password for admin user',
                            action='store', default=None, dest='os_password')
        parser.add_argument('--os-auth-url',
                            help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                            action='store', default=None, dest='os_auth_url')
        parser.add_argument('--swift-pass',
                            help='password for swift user',
                            action='store', default=None, dest='swift_pass')
        parser.add_argument('--public-endpoint',
                            help=r'public endpoint for swift service e.g. "http://CONTROLLER_VIP:8080/v1/AUTH_%%\(tenant_id\)s"',
                            action='store', default=None, dest='public_endpoint')
        parser.add_argument('--internal-endpoint',
                            help=r'internal endpoint for swift service e.g. "http://CONTROLLER_VIP:8080/v1/AUTH_%%\(tenant_id\)s"',
                            action='store', default=None, dest='internal_endpoint')
        parser.add_argument('--admin-endpoint',
                            help='admin endpoint for swift service e.g. http://CONTROLLER_VIP:8080/v1',
                            action='store', default=None, dest='admin_endpoint')
        return parser

    def take_action(self, parsed_args):
        create_service_credentials(parsed_args)


class Install(Command):
    """install swift proxy"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Install, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--auth-uri',
                            help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                            action='store', default=None, dest='auth_uri')
        parser.add_argument('--auth-url',
                            help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                            action='store', default=None, dest='auth_url')
        parser.add_argument('--swift-pass',
                            help='password for swift user',
                            action='store', default=None, dest='swift_pass')
        parser.add_argument('--memcached-servers',
                            help='memcache servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                            action='store', default=None, dest='memcached_servers')
        parser.add_argument('--with-memcached',
                            help='install memcached on remote server, if you have other memcached on the controller node, you can use --memcached-sersers',
                            action='store_true', default=False, dest='with_memcached')
        return parser

    def take_action(self, parsed_args):
        install(parsed_args)


class Finalize(Command):
    """finalize swift installation"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(InstallFinalize, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--swift-hash-path-suffix',
                            help='swift_hash_path_suffix and swift_hash_path_prefix are used as part of the hashing algorithm when determining data placement in the cluster. These values should remain secret and MUST NOT change once a cluster has been deployed',
                            action='store', default=None, dest='swift_hash_path_suffix')
        parser.add_argument('--swift-hash-path-prefix',
                            help='swift_hash_path_suffix and swift_hash_path_prefix are used as part of the hashing algorithm when determining data placement in the cluster. These values should remain secret and MUST NOT change once a cluster has been deployed',
                            action='store', default=None, dest='swift_hash_path_prefix')
        return parser

    def take_action(self, parsed_args):
        finalize_install(parsed_args)
