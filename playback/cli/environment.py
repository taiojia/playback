import os
import sys
import logging
from playback.api import Cmd
from playback.api import PrepareHost
from playback.cli.cliutil import priority
from cliff.command import Command

def prepare_host(user, hosts, key_filename, password, public_interface):
    try:
        remote = PrepareHost(user, hosts, key_filename, password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
        sys.exit(1)

    # host networking
    remote.setup_external_interface(public_interface)

    # ntp
    remote.setup_ntp()

    # openstack packages
    remote.set_openstack_repository()

def gen_pass():
    """DEPRECATED"""
    os.system('openssl rand -hex 10')

def cmd(user, hosts, key_filename, password, run):
    """DEPRECATED"""
    try:
        remote = Cmd(user, hosts, key_filename, password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
        sys.exit(1)
    remote.cmd(run)

@priority(10)
def make(parser):
    """DEPRECATED
    prepare OpenStack basic environment"""
    s = parser.add_subparsers(
        title='commands',
        metavar='COMMAND',
        help='description',
        )

    def gen_pass_f(args):
        gen_pass()
    gen_pass_parser = s.add_parser('gen-pass', help='generate the password')
    gen_pass_parser.set_defaults(func=gen_pass_f)

    def cmd_f(args):
        cmd(args.user, args.hosts.split(','), args.key_filename, args.password, args.run)
    cmd_parser = s.add_parser('cmd', help='run command line on the target host')
    cmd_parser.add_argument('--run', help='the command running on the remote node', action='store', default=None, dest='run')
    cmd_parser.set_defaults(func=cmd_f)

class PrepareHosts(Command):
    """prepare the OpenStack environment"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PrepareHosts, self).get_parser(prog_name)
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
        parser.add_argument('--public-interface', help='public interface e.g. eth1',
                            action='store', default='eth1', dest='public_interface')
        return parser

    def take_action(self, parsed_args):
        prepare_host(parsed_args.user, parsed_args.hosts.split(','), parsed_args.key_filename,
                     parsed_args.password, parsed_args.public_interface)

