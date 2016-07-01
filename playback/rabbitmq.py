import argparse
from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import sys
from playback.cli import cli_description
from playback import __version__
from playback import common

class RabbitMq(common.Common):
    """RabbitMQ HA Installation"""

    def _install(self, erlang_cookie, rabbit_user, rabbit_pass):
        sudo('apt-get update')
        sudo('apt-get install -y rabbitmq-server')
        sudo('service rabbitmq-server stop')
        sudo('echo "%s" > /var/lib/rabbitmq/.erlang.cookie' % erlang_cookie)
        sudo('service rabbitmq-server start')
        sudo('rabbitmqctl add_user %s %s' % (rabbit_user, rabbit_pass))
        sudo('echo "[{rabbit, [{loopback_users, []}]}]." > /etc/rabbitmq/rabbitmq.config')
        sudo('rabbitmqctl set_permissions %s ".*" ".*" ".*"' % rabbit_user)
        sudo('service rabbitmq-server restart')

    def _join_cluster(self, name):
        sudo('rabbitmqctl stop_app')
        sudo('rabbitmqctl join_cluster %s' % name)
        sudo('rabbitmqctl start_app')
        sudo('rabbitmqctl set_policy ha-all \'^(?!amq\.).*\' \'{"ha-mode": "all"}\'')

def install_subparser(s):
    install_parser = s.add_parser('install', help='install RabbitMQ HA')
    install_parser.add_argument('--erlang-cookie', help='setup elang cookie',
                                action='store', default=None, dest='erlang_cookie')
    install_parser.add_argument('--rabbit-user', help='set rabbit user name',
                                action='store', default=None, dest='rabbit_user')
    install_parser.add_argument('--rabbit-pass', help='set rabbit password',
                                action='store', default=None, dest='rabbit_pass')
    return install_parser

def join_cluster_subparser(s):
    join_cluster_parser = s.add_parser('join-cluster', help='join the rabbit cluster')
    join_cluster_parser.add_argument('--name', help='the joined name, e.g. rabbit@CONTROLLER1',
                                    action='store', default=None, dest='name')
    return join_cluster_parser

def make_target(args):
    try:
        target = RabbitMq(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    return target

def install(args):
    target = make_target(args)
    execute(target._install, args.erlang_cookie, args.rabbit_user, args.rabbit_pass)

def join_cluster(args):
    target = make_target(args)
    execute(target._join_cluster, args.name)

def parser():
    p = argparse.ArgumentParser(prog='rabbitmq-deploy', description=cli_description+'this command used for provision RabbitMQ')
    p.add_argument('-v', '--version',
                    action='version',
                    version=__version__)
    p.add_argument('--user', help='the target user', 
                    action='store', default='ubuntu', dest='user')
    p.add_argument('--hosts', help='the target address', 
                    action='store', dest='hosts')
    p.add_argument('-i', '--key-filename', help='referencing file paths to SSH key files to try when connecting', action='store', dest='key_filename', default=None)
    p.add_argument('--password', help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password', default=None)

    s = p.add_subparsers(dest="subparser_name")

    def install_f(args):
        install(args)
    install_parser = install_subparser(s)
    install_parser.set_defaults(func=install_f)

    def join_cluster_f(args):
        join_cluster(args)
    join_cluster_parser = join_cluster_subparser(s)
    join_cluster_parser.set_defaults(func=join_cluster_f)

    return p

def main():
    p = parser()
    args = p.parse_args()
    if not hasattr(args, 'func'):
        p.print_help()
    else:
        # XXX on Python 3.3 we get 'args has no func' rather than short help.
        try:
            args.func(args)
            disconnect_all()
            return 0
        except Exception as e:
            sys.stderr.write(e.message)
    return 1

if __name__ == '__main__':
    main()