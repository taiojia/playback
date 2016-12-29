import sys, logging
from playback.api import Horizon
from cliff.command import Command

def install(args):
    try:
        target = Horizon(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
        sys.exit(1)

    target.install(
            args.openstack_host,
            args.memcached_servers,
            args.time_zone)


class Install(Command):
    """install horizon"""

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
        parser.add_argument('--openstack-host',
                            help='configure the dashboard to use OpenStack services on the controller node e.g. CONTROLLER_VIP',
                            action='store', default=None, dest='openstack_host')
        parser.add_argument('--memcached-servers',
                            help='django memcache e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                            action='store', default=None, dest='memcached_servers')
        parser.add_argument('--time-zone',
                            help='the timezone of the server. This should correspond with the timezone of your entire OpenStack installation e.g. Asia/Shanghai',
                            action='store', default=None, dest='time_zone')
        return parser

    def take_action(self, parsed_args):
        install(parsed_args)
