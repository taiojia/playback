import sys
import logging
from playback.api import NovaCompute
from cliff.command import Command


def make_target(args):
    try:
        target = NovaCompute(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename,
                             password=args.password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
        sys.exit(1)
    return target


def install(args):
    target = make_target(args)
    target.install(args.my_ip, args.rabbit_hosts, args.rabbit_user, args.rabbit_pass,
                   args.auth_uri, args.auth_url, args.nova_pass, args.novncproxy_base_url,
                   args.glance_api_servers, args.neutron_endpoint, args.neutron_pass, args.rbd_secret_uuid,
                   args.memcached_servers)


class Install(Command):
    """install nova compute"""

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
        parser.add_argument('--my-ip',
                            help='the host management ip',
                            action='store', default=None, dest='my_ip')
        parser.add_argument('--rabbit-hosts',
                            help='rabbit hosts e.g. CONTROLLER1,CONTROLLER2',
                            action='store', default=None, dest='rabbit_hosts')
        parser.add_argument('--rabbit-user',
                            help='the user for rabbit, default openstack',
                            action='store', default='openstack', dest='rabbit_user')
        parser.add_argument('--rabbit-pass',
                            help='the password for rabbit openstack user', action='store',
                            default=None, dest='rabbit_pass')
        parser.add_argument('--auth-uri',
                            help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                            action='store', default=None, dest='auth_uri')
        parser.add_argument('--auth-url',
                            help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                            action='store', default=None, dest='auth_url')
        parser.add_argument('--nova-pass',
                            help='passowrd for nova user',
                            action='store', default=None, dest='nova_pass')
        parser.add_argument('--novncproxy-base-url',
                            help='nova vnc proxy base url e.g. http://CONTROLLER_VIP:6080/vnc_auto.html',
                            action='store', default=None, dest='novncproxy_base_url')
        parser.add_argument('--glance-api-servers',
                            help='glance host e.g. http://CONTROLLER_VIP:9292',
                            action='store', default=None, dest='glance_api_servers')
        parser.add_argument('--neutron-endpoint',
                            help='neutron endpoint e.g. http://CONTROLLER_VIP:9696',
                            action='store', default=None, dest='neutron_endpoint')
        parser.add_argument('--neutron-pass',
                            help='the password for neutron user',
                            action='store', default=None, dest='neutron_pass')
        parser.add_argument('--rbd-secret-uuid',
                            help='ceph rbd secret for nova libvirt',
                            action='store', default=None, dest='rbd_secret_uuid')
        parser.add_argument('--memcached-servers',
                            help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                            action='store', default=None, dest='memcached_servers')
        return parser

    def take_action(self, parsed_args):
        install(parsed_args)
