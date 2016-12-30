import sys, logging
from playback.api import Neutron
from cliff.command import Command


def make_target(args):
    try:
        target = Neutron(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except Exception:
        sys.stderr.write('No hosts found. Please using --hosts param.')
        sys.exit(1)
    return target

def create_neutron_db(args):
    target = make_target(args)
    target.create_neutron_db(args.root_db_pass, args.neutron_db_pass)

def create_service_credentials(args):
    target = make_target(args)
    target.create_service_credentials(
            args.os_password,
            args.os_auth_url,
            args.neutron_pass,
            args.public_endpoint,
            args.internal_endpoint,
            args.admin_endpoint)

def install(args):
    target = make_target(args)
    target.install_self_service(
            args.connection,
            args.rabbit_hosts,
            args.rabbit_user,
            args.rabbit_pass,
            args.auth_uri,
            args.auth_url,
            args.neutron_pass,
            args.nova_url,
            args.nova_pass,
            args.public_interface,
            args.local_ip,
            args.nova_metadata_ip,
            args.metadata_proxy_shared_secret,
            args.memcached_servers,
            args.populate)


class CreateNeutronDB(Command):
    """create the neutron database"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateNeutronDB, self).get_parser(prog_name)
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
        parser.add_argument('--neutron-db-pass',
                            help='neutron db passowrd',
                            action='store', default=None, dest='neutron_db_pass')
        return parser

    def take_action(self, parsed_args):
        create_neutron_db(parsed_args)


class CreateServiceCredentials(Command):
    """create the neutron service credentials"""

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
        parser.add_argument('--neutron-pass',
                            help='the password for neutron user',
                            action='store', default=None, dest='neutron_pass')
        parser.add_argument('--public-endpoint',
                            help='public endpoint for neutron service e.g. http://CONTROLLER_VIP:9696',
                            action='store', default=None, dest='public_endpoint')
        parser.add_argument('--internal-endpoint',
                            help='internal endpoint for neutron service e.g. http://CONTROLLER_VIP:9696',
                            action='store', default=None, dest='internal_endpoint')
        parser.add_argument('--admin-endpoint',
                            help='admin endpoint for neutron service e.g. http://CONTROLLER_VIP:9696',
                            action='store', default=None, dest='admin_endpoint')
        return parser

    def take_action(self, parsed_args):
        create_service_credentials(parsed_args)


class Install(Command):
    """install neutron for self-service"""

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
                            help='mysql database connection string e.g. mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron',
                            action='store', default=None, dest='connection')
        parser.add_argument('--auth-uri',
                            help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                            action='store', default=None, dest='auth_uri')
        parser.add_argument('--auth-url',
                            help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                            action='store', default=None, dest='auth_url')
        parser.add_argument('--rabbit-hosts',
                            help='rabbit hosts e.g. controller1,controller2',
                            action='store', default=None, dest='rabbit_hosts')
        parser.add_argument('--rabbit-user',
                            help='the user for rabbit, default openstack',
                            action='store', default='openstack', dest='rabbit_user')
        parser.add_argument('--rabbit-pass',
                            help='the password for rabbit openstack user',
                            action='store', default=None, dest='rabbit_pass')
        parser.add_argument('--neutron-pass',
                            help='the password for neutron user',
                            action='store', default=None, dest='neutron_pass')
        parser.add_argument('--nova-url',
                            help='URL for connection to nova (Only supports one nova region currently) e.g. http://CONTROLLER_VIP:8774/v2.1',
                            action='store', default=None, dest='nova_url')
        parser.add_argument('--nova-pass',
                            help='passowrd for nova user',
                            action='store', default=None, dest='nova_pass')
        parser.add_argument('--public-interface',
                            help='public interface e.g. eth1',
                            action='store', default=None, dest='public_interface')
        parser.add_argument('--local-ip',
                            help=' underlying physical network interface that handles overlay networks(uses the management interface IP)',
                            action='store', default=None, dest='local_ip')
        parser.add_argument('--nova-metadata-ip',
                            help='IP address used by Nova metadata server e.g. CONTROLLER_VIP',
                            action='store', default=None, dest='nova_metadata_ip')
        parser.add_argument('--metadata-proxy-shared-secret',
                            help='metadata proxy shared secret',
                            action='store', default=None, dest='metadata_proxy_shared_secret')
        parser.add_argument('--memcached-servers',
                            help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                            action='store', default=None, dest='memcached_servers')
        parser.add_argument('--populate',
                            help='Populate the neutron database',
                            action='store_true', default=False, dest='populate')
        return parser


    def take_action(self, parsed_args):
        install(parsed_args)
