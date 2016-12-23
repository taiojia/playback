import sys, logging
from playback.api import HaproxyInstall
from playback.api import HaproxyConfig
from playback.templates.haproxy_cfg import conf_haproxy_cfg
from cliff.command import Command


def install(args):
    try:
        target = HaproxyInstall(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError as e:
        sys.stderr.write(e.message)
        sys.exit(1)
    target.install()

def config(args):
    try:
        target = HaproxyConfig(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
        sys.exit(1)
    if args.upload_conf:
        target.upload_conf(args.upload_conf)
    if args.configure_keepalived:
        target.configure_keepalived(args.router_id, args.priority,
                args.state, args.interface, args.vip)

def gen_conf():
    with open('haproxy.cfg', 'w') as f:
        f.write(conf_haproxy_cfg)


class Install(Command):
    """install haproxy with keepalived"""
    
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
        return parser
    
    def take_action(self, parsed_args):
        install(parsed_args)


class Config(Command):
    """configure haproxy"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Config, self).get_parser(prog_name)
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
        parser.add_argument('--upload-conf', help='upload configuration file to the target host',
                            action='store', default=False, dest='upload_conf')
        parser.add_argument('--configure-keepalived', help='configure keepalived',
                            action='store_true', default=False, dest='configure_keepalived')
        parser.add_argument('--router_id', help='Keepalived router id e.g. lb1',
                            action='store', default=False, dest='router_id')
        parser.add_argument('--priority', help='Keepalived priority e.g. 150',
                            action='store', default=False, dest='priority')
        parser.add_argument('--state', help='Keepalived state e.g. MASTER',
                            action='store', default=False, dest='state')
        parser.add_argument('--interface', help='Keepalived binding interface e.g. eth0',
                            action='store', default=False, dest='interface')
        parser.add_argument('--vip', help='Keepalived virtual ip e.g. CONTROLLER_VIP',
                            action='store', default=False, dest='vip')
        return parser

    def take_action(self, parsed_args):
        config(parsed_args)


class GenConf(Command):
    """generate the example configuration to the current location"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        gen_conf()