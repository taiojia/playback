import sys
import logging
from playback.api import Cinder
from cliff.command import Command

def make_target(user, hosts, key_filename, password):
    try:
        target = Cinder(user, hosts, key_filename, password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
        sys.exit(1)

    return target

def create_cinder_db(user, hosts, key_filename, password, root_db_pass, cinder_db_pass):
    target = make_target(user, hosts, key_filename, password)
    target.create_cinder_db(root_db_pass, cinder_db_pass)

def create_service_credentials(user ,hosts, key_filename, password, os_password, os_auth_url, cinder_pass, public_endpoint_v1, internal_endpoint_v1, admin_endpoint_v1, public_endpoint_v2, internal_endpoint_v2, admin_endpoint_v2):
    target =make_target(user, hosts, key_filename, password)
    target.create_service_credentials(os_password,
            os_auth_url, cinder_pass, public_endpoint_v1,
            internal_endpoint_v1, admin_endpoint_v1, public_endpoint_v2,
            internal_endpoint_v2, admin_endpoint_v2)

def install(user, hosts, key_filename, password, connection, rabbit_hosts, rabbit_user, rabbit_pass, auth_uri, auth_url, cinder_pass, my_ip, glance_api_servers, rbd_secret_uuid, memcached_servers, populate):
    target = make_target(user, hosts, key_filename, password)
    target.install(
            connection,
            rabbit_hosts,
            rabbit_user,
            rabbit_pass,
            auth_uri,
            auth_url,
            cinder_pass,
            my_ip,
            glance_api_servers,
            rbd_secret_uuid,
            memcached_servers,
            populate)


class CreateCinderDB(Command):
    """create cinder database on remote machine"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateCinderDB, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host', action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ', action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting', action='store', dest='key_filename',
                            default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password',
                            default=None)
        parser.add_argument('--root-db-pass',
                            help='the openstack database root passowrd',
                            action='store', default=None, dest='root_db_pass')
        parser.add_argument('--cinder-db-pass',
                            help='cinder db passowrd', action='store',
                            default=None, dest='cinder_db_pass')
        return parser

    def take_action(self, parsed_args):
        create_cinder_db(parsed_args.user, parsed_args.hosts.split(','),
                         parsed_args.key_filename, parsed_args.password,
                         parsed_args.root_db_pass, parsed_args.cinder_db_pass)

class CreateServiceCredentials(Command):
    """create the cinder service credentials"""

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
        parser.add_argument('--os-password', help='the password for admin user',
                            action='store', default=None, dest='os_password')
        parser.add_argument('--os-auth-url', help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                            action='store', default=None, dest='os_auth_url')
        parser.add_argument('--cinder-pass', help='password for cinder user',
                            action='store', default=None, dest='cinder_pass')
        parser.add_argument('--public-endpoint-v1', help=r'public endpoint for volume service e.g. "http://CONTROLLER_VIP:8776/v1/%%\(tenant_id\)s"',
                            action='store', default=None, dest='public_endpoint_v1')
        parser.add_argument('--internal-endpoint-v1', help=r'internal endpoint for volume service e.g. "http://CONTROLLER_VIP:8776/v1/%%\(tenant_id\)s"',
                            action='store', default=None, dest='internal_endpoint_v1')
        parser.add_argument('--admin-endpoint-v1', help=r'admin endpoint for volume service e.g. "http://CONTROLLER_VIP:8776/v1/%%\(tenant_id\)s"',
                            action='store', default=None, dest='admin_endpoint_v1')
        parser.add_argument('--public-endpoint-v2', help=r'public endpoint v2 for volumev2 service e.g. "http://CONTROLLER_VIP:8776/v2/%%\(tenant_id\)s"',
                            action='store', default=None, dest='public_endpoint_v2')
        parser.add_argument('--internal-endpoint-v2', help=r'internal endpoint v2 for volumev2 service e.g. "http://CONTROLLER_VIP:8776/v2/%%\(tenant_id\)s"',
                            action='store', default=None, dest='internal_endpoint_v2')
        parser.add_argument('--admin-endpoint-v2', help=r'admin endpoint v2 for volumev2 service e.g. "http://CONTROLLER_VIP:8776/v2/%%\(tenant_id\)s"',
                            action='store', default=None, dest='admin_endpoint_v2')
        return parser

    def take_action(self, parsed_args):
        create_service_credentials(parsed_args.user, parsed_args.hosts.split(','),
                                   parsed_args.key_filename, parsed_args.password,
                                   parsed_args.os_password, parsed_args.os_auth_url,
                                   parsed_args.cinder_pass, parsed_args.public_endpoint_v1,
                                   parsed_args.internal_endpoint_v1, parsed_args.admin_endpoint_v1,
                                   parsed_args.public_endpoint_v2, parsed_args.internal_endpoint_v2,
                                   parsed_args.admin_endpoint_v2)


class Install(Command):
    """install cinder api and volume"""

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
                            help='mysql database connection string e.g. mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder',
                            action='store', default=None, dest='connection')
        parser.add_argument('--rabbit-hosts',
                            help='rabbit hosts e.g. CONTROLLER1,CONTROLLER2',
                            action='store', default=None, dest='rabbit_hosts')
        parser.add_argument('--rabbit-user',
                            help='the user for rabbit, default openstack',
                            action='store', default='openstack', dest='rabbit_user')
        parser.add_argument('--rabbit-pass',
                            help='the password for rabbit openstack user',
                            action='store', default=None, dest='rabbit_pass')
        parser.add_argument('--auth-uri',
                            help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                            action='store', default=None, dest='auth_uri')
        parser.add_argument('--auth-url',
                            help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                            action='store', default=None, dest='auth_url')
        parser.add_argument('--cinder-pass',
                            help='password for cinder user',
                            action='store', default=None, dest='cinder_pass')
        parser.add_argument('--my-ip',
                            help='the host management ip',
                            action='store', default=None, dest='my_ip')
        parser.add_argument('--glance-api-servers',
                            help='glance host e.g. http://CONTROLLER_VIP:9292',
                            action='store', default=None, dest='glance_api_servers')
        parser.add_argument('--rbd-secret-uuid',
                            help='ceph rbd secret uuid',
                            action='store', default=None, dest='rbd_secret_uuid')
        parser.add_argument('--memcached-servers',
                            help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                            action='store', default=None, dest='memcached_servers')
        parser.add_argument('--populate',
                            help='Populate the cinder database',
                            action='store_true', default=False, dest='populate')
        return parser

    def take_action(self, parsed_args):
        install(parsed_args.user, parsed_args.hosts.split(','), parsed_args.key_filename,
                parsed_args.password, parsed_args.connection, parsed_args.rabbit_hosts,
                parsed_args.rabbit_user, parsed_args.rabbit_pass, parsed_args.auth_uri,
                parsed_args.auth_url, parsed_args.cinder_pass, parsed_args.my_ip,
                parsed_args.glance_api_servers, parsed_args.rbd_secret_uuid, parsed_args.memcached_servers,
                parsed_args.populate)


