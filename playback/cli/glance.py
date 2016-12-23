import logging, sys
from playback.cli.cliutil import priority
from playback.api import Glance
from cliff.command import Command

def make_target(user, hosts, key_filename, password):
    try:
        target = Glance(user, hosts, key_filename, password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
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

@priority(15)
def make(parser):
    """DEPRECATED
    provison Glance with HA"""
    s = parser.add_subparsers(
        title='commands',
        metavar='COMMAND',
        help='description',
        )

class CreateGlanceDB(Command):
    """create the glance database"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateGlanceDB, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host', action='store', default='ubuntu',
                            dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ', action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting', action='store',
                            dest='key_filename',
                            default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts', action='store',
                            dest='password',
                            default=None)
        parser.add_argument('--root-db-pass', help='the openstack database root passowrd',
                            action='store', default=None, dest='root_db_pass')
        parser.add_argument('--glance-db-pass', help='glance db passowrd',
                            action='store', default=None, dest='glance_db_pass')
        return parser

    def take_action(self, parsed_args):
        create_glance_db(parsed_args)


class CreateServiceCredentials(Command):
    """create the glance service credentials"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateServiceCredentials, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host', action='store', default='ubuntu',
                            dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ', action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting', action='store',
                            dest='key_filename',
                            default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts', action='store',
                            dest='password',
                            default=None)
        parser.add_argument('--os-password', help='the password for admin user',
                            action='store', default=None, dest='os_password')
        parser.add_argument('--os-auth-url', help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                            action='store', default=None, dest='os_auth_url')
        parser.add_argument('--glance-pass', help='passowrd for glance user',
                            action='store', default=None, dest='glance_pass')
        parser.add_argument('--public-endpoint', help='public endpoint for glance service e.g. http://CONTROLLER_VIP:9292',
                            action='store', default=None, dest='public_endpoint')
        parser.add_argument('--internal-endpoint', help='internal endpoint for glance service e.g. http://CONTROLLER_VIP:9292',
                            action='store', default=None, dest='internal_endpoint')
        parser.add_argument('--admin-endpoint', help='admin endpoint for glance service e.g. http://CONTROLLER_VIP:9292',
                            action='store', default=None, dest='admin_endpoint')
        return parser

    def take_action(self, parsed_args):
        create_service_credentials(parsed_args)


class Install(Command):
    """install glance(default store: ceph)"""

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
        parser.add_argument('--connection', help='mysql database connection string e.g. mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance',
                            action='store', default=None, dest='connection')
        parser.add_argument('--auth-uri', help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                            action='store',default=None, dest='auth_uri')
        parser.add_argument('--auth-url',
                            help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                            action='store', default=None, dest='auth_url')
        parser.add_argument('--glance-pass',
                            help='passowrd for glance user',
                            action='store', default=None, dest='glance_pass')
        parser.add_argument('--swift-store-auth-address',
                            help='DEPRECATED the address where the Swift authentication service is listening e.g. http://CONTROLLER_VIP:5000/v3/',
                            action='store', default='DEPRECATED_BY_PLAYBACK', dest='swift_store_auth_address')
        parser.add_argument('--memcached-servers',
                            help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                            action='store', default=None, dest='memcached_servers')
        parser.add_argument('--populate',
                            help='populate the glance database',
                            action='store_true', default=False, dest='populate')
        return parser

    def take_action(self, parsed_args):
        install(parsed_args)