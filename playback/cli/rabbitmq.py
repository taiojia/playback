import sys
import logging
from playback.api import RabbitMq
from cliff.command import Command


def make_target(args):
    try:
        target = RabbitMq(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename,
                          password=args.password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
        sys.exit(1)
    return target


def install(args):
    target = make_target(args)
    target.install(args.erlang_cookie, args.rabbit_user, args.rabbit_pass)


def join_cluster(args):
    target = make_target(args)
    target.join_cluster(args.name)


class Install(Command):
    """install rabbitmq"""

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
        parser.add_argument('--erlang-cookie',
                            help='setup elang cookie',
                            action='store', default=None, dest='erlang_cookie')
        parser.add_argument('--rabbit-user',
                            help='set rabbit user name',
                            action='store', default=None, dest='rabbit_user')
        parser.add_argument('--rabbit-pass',
                            help='set rabbit password',
                            action='store', default=None, dest='rabbit_pass')
        return parser

    def take_action(self, parsed_args):
        install(parsed_args)


class JoinCluster(Command):
    """join the rabbit cluster"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(JoinCluster, self).get_parser(prog_name)
        parser.add_argument('--name',
                            help='the joined name, e.g. rabbit@CONTROLLER1',
                            action='store', default=None, dest='name')
        return parser

    def take_action(self, parsed_args):
        join_cluster(parsed_args)
