import sys, logging
from playback.api import Keystone
from cliff.command import Command

def make_target(args):
    try:
        target = Keystone(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        err_hosts = 'No hosts found. Please using --hosts param.'
        sys.stderr.write(err_hosts)
        sys.exit(1)

    return target

def create_keystone_db(args):
    target = make_target(args)
    target.create_keystone_db(
            args.root_db_pass,
            args.keystone_db_pass)

def install(args):
    target = make_target(args)
    target.install_keystone(
            args.admin_token,
            args.connection,
            args.memcached_servers,
            args.populate)

def create_entity_and_endpoint(args):
    target = make_target(args)
    target.create_entity_and_endpoint(
        args.os_token,
        args.os_url,
        args.public_endpoint,
        args.internal_endpoint,
        args.admin_endpoint)

def create_projects_users_roles(args):
    target = make_target(args)
    target.create_projects_users_roles(
        args.os_token,
        args.os_url,
        args.admin_pass,
        args.demo_pass)
    target.update_keystone_paste_ini()


class CreateKeystoneDB(Command):
    """create the keystone database"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateKeystoneDB, self).get_parser(prog_name)
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
        parser.add_argument('--root-db-pass',
                            help='the openstack database root passowrd',
                            action='store', default=None, dest='root_db_pass')
        parser.add_argument('--keystone-db-pass',
                            help='keystone db passowrd',
                            action='store', default=None, dest='keystone_db_pass')
        return parser

    def take_action(self, parsed_args):
        create_keystone_db(parsed_args)


class Install(Command):
    """install keystone"""

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
        parser.add_argument('--admin-token',
                            help='define the value of the initial administration token',
                            action='store', default=None, dest='admin_token')
        parser.add_argument('--connection',
                            help='database connection string e.g. mysql+pymysql://keystone:PASS@CONTROLLER_VIP/keystone',
                            action='store', default=None, dest='connection')
        parser.add_argument('--memcached-servers',
                            help='memcached servers. e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                            action='store', default=None, dest='memcached_servers')
        parser.add_argument('--populate',
                            help='populate the keystone database',
                            action='store_true', default=False, dest='populate')
        return parser

    def take_action(self, parsed_args):
        install(parsed_args)


class CreateEntityAndEndpoint(Command):
    """create the service entity and API endpoints"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateEntityAndEndpoint, self).get_parser(prog_name)
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
        parser.add_argument('--os-token',
                            help='the admin token',
                            action='store', default=None, dest='os_token')
        parser.add_argument('--os-url',
                            help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                            action='store', default=None, dest='os_url')
        parser.add_argument('--public-endpoint',
                            help='the public endpoint e.g. http://CONTROLLER_VIP:5000/v3',
                            action='store', default=None, dest='public_endpoint')
        parser.add_argument('--internal-endpoint',
                            help='the internal endpoint e.g. http://CONTROLLER_VIP:5000/v3',
                            action='store', default=None, dest='internal_endpoint')
        parser.add_argument('--admin-endpoint',
                            help='the admin endpoint e.g. http://CONTROLLER_VIP:35357/v3',
                            action='store', default=None, dest='admin_endpoint')
        return parser

    def take_action(self, parsed_args):
        create_entity_and_endpoint(parsed_args)


class CreateProjectsUsersRoles(Command):
    """create an administrative and demo project, user, and role for administrative and testing operations in your environment"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateProjectsUsersRoles, self).get_parser(prog_name)
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
        parser.add_argument('--os-token',
                            help='the admin token',
                            action='store', default=None, dest='os_token')
        parser.add_argument('--os-url',
                            help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                            action='store', default=None, dest='os_url')
        parser.add_argument('--admin-pass',
                            help='passowrd for admin user',
                            action='store', default=None, dest='admin_pass')
        parser.add_argument('--demo-pass',
                            help='passowrd for demo user',
                            action='store', default=None, dest='demo_pass')
        return parser

    def take_action(self, parsed_args):
        create_projects_users_roles(parsed_args)
