import argparse
from fabric.api import *
from fabric.contrib import files

parser = argparse.ArgumentParser()
parser.add_argument('--user', help='the target user', 
                    action='store', default='ubuntu', dest='user')
parser.add_argument('--hosts', help='the target address', 
                    action='store', dest='hosts')
subparsers = parser.add_subparsers(dest="subparser_name") 
install = subparsers.add_parser('install', help='install RabbitMQ HA')
install.add_argument('--erlang-cookie', help='setup elang cookie',
                    action='store', default=None, dest='erlang_cookie')
install.add_argument('--rabbit-user', help='set rabbit user name',
                    action='store', default=None, dest='rabbit_user')
install.add_argument('--rabbit-pass', help='set rabbit password',
                    action='store', default=None, dest='rabbit_pass')
join_cluster = subparsers.add_parser('join-cluster', help='join the rabbit cluster')
join_cluster.add_argument('--name', help='the joined name, e.g. rabbit@CONTROLLER1',
                   action='store', default=None, dest='name')

args = parser.parse_args()


class RabbitMq(object):
    """RabbitMQ HA Installation"""
    def __init__(self, hosts, user='ubuntu', parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _install(self, erlang_cookie, rabbit_user, rabbit_pass):
        sudo('apt-get update')
        sudo('apt-get install -y rabbitmq-server')
        sudo('service rabbitmq-server stop')
        sudo('echo "%s" > /var/lib/rabbitmq/.erlang.cookie' % erlang_cookie)
        sudo('service rabbitmq-server start')
        sudo('rabbitmqctl add_user %s %s' % (rabbit_user, rabbit_pass))
        sudo('echo "[{rabbit, [{loopback_users, []}]}]." > /etc/rabbitmq/rabbitmq.config')
        sudo('rabbitmqctl set_permissions openstack ".*" ".*" ".*"')
        sudo('service rabbitmq-server restart')

    def _join_cluster(self, name):
        sudo('rabbitmqctl stop_app')
        sudo('rabbitmqctl join_cluster %s' % name)
        sudo('rabbitmqctl start_app')
        sudo('rabbitmqctl set_policy ha-all \'^(?!amq\.).*\' \'{"ha-mode": "all"}\'')


def main():
    target = RabbitMq(user=args.user, hosts=args.hosts.split(','))

    if args.subparser_name == 'install':
        execute(target._install, args.erlang_cookie, args.rabbit_user, args.rabbit_pass)
    
    if args.subparser_name == 'join-cluster':
        execute(target._join_cluster, args.name)

if __name__ == '__main__':
    main()