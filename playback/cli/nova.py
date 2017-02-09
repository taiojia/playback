import sys, logging
from playback.cli.cliutil import priority
from playback.api import Nova
from cliff.command import Command


def make_target(args):
    try:
        target = Nova(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename,
                      password=args.password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
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


class CreateNovaDB(Command):
    """create the nova and nova_api database"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateNovaDB, self).get_parser(prog_name)
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
                            help='the MySQL database root passowrd',
                            action='store', default=None, dest='root_db_pass')
        parser.add_argument('--nova-db-pass',
                            help='nova and nova_api database passowrd',
                            action='store', default=None, dest='nova_db_pass')
        return parser

    def take_action(self, parsed_args):
        create_nova_db(parsed_args)

class CreateServiceCredentials(Command):
    """create the nova service credentials"""

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
        parser.add_argument('--nova-pass',
                            help='passowrd for nova user',
                            action='store', default=None, dest='nova_pass')
        parser.add_argument('--public-endpoint',
                            help=r'public endpoint for nova service e.g. "http://CONTROLLER_VIP:8774/v2.1/%%\(tenant_id\)s"',
                            action='store', default=None, dest='public_endpoint')
        parser.add_argument('--internal-endpoint',
                            help=r'internal endpoint for nova service e.g. "http://CONTROLLER_VIP:8774/v2.1/%%\(tenant_id\)s"',
                            action='store', default=None, dest='internal_endpoint')
        parser.add_argument('--admin-endpoint',
                            help=r'admin endpoint for nova service e.g. "http://CONTROLLER_VIP:8774/v2.1/%%\(tenant_id\)s"',
                            action='store', default=None, dest='admin_endpoint')
        return parser

    def take_action(self, parsed_args):
        create_service_credentials(parsed_args)


class Install(Command):
    """install nova"""

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
        parser.add_argument('--connection',
                            help='mysql nova database connection string e.g. mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova',
                            action='store', default=None, dest='connection')
        parser.add_argument('--api-connection',
                            help='mysql nova_api database connection string e.g. mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova_api',
                            action='store', default=None, dest='api_connection')
        parser.add_argument('--auth-uri',
                            help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                            action='store', default=None, dest='auth_uri')
        parser.add_argument('--auth-url',
                            help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                            action='store', default=None, dest='auth_url')
        parser.add_argument('--nova-pass',
                            help='passowrd for nova user',
                            action='store', default=None, dest='nova_pass')
        parser.add_argument('--my-ip',
                            help='the host management ip',
                            action='store', default=None, dest='my_ip')
        parser.add_argument('--memcached-servers',
                            help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                            action='store', default=None, dest='memcached_servers')
        parser.add_argument('--rabbit-hosts',
                            help='rabbit hosts e.g. CONTROLLER1,CONTROLLER2',
                            action='store', default=None, dest='rabbit_hosts')
        parser.add_argument('--rabbit-user',
                            help='the user for rabbit openstack user, default openstack',
                            action='store', default='openstack', dest='rabbit_user')
        parser.add_argument('--rabbit-pass',
                            help='the password for rabbit openstack user',
                            action='store', default=None, dest='rabbit_pass')
        parser.add_argument('--glance-api-servers',
                            help='glance host e.g. http://CONTROLLER_VIP:9292',
                            action='store', default=None, dest='glance_api_servers')
        parser.add_argument('--neutron-endpoint',
                            help='neutron endpoint e.g. http://CONTROLLER_VIP:9696',
                            action='store', default=None, dest='neutron_endpoint')
        parser.add_argument('--neutron-pass',
                            help='the password for neutron user',
                            action='store', default=None, dest='neutron_pass')
        parser.add_argument('--metadata-proxy-shared-secret',
                            help='metadata proxy shared secret',
                            action='store', default=None, dest='metadata_proxy_shared_secret')
        parser.add_argument('--populate', help='Populate the nova database',
                            action='store_true', default=False, dest='populate')
        return parser

    def take_action(self, parsed_args):
        install(parsed_args)
