import argparse
from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import sys
from playback import __version__
from playback import common

class RabbitMq(common.Common):
    """RabbitMQ HA Installation
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """

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

    def install(self, *args, **kwargs):
        """
        Install rabbitmq

        :param erlang_cookie: setup elang cookie
        :param rabbit_user: set rabbit user name
        :param rabbit_pass: set rabbit password of `rabbit_user`
        :returns: None
        """
        return execute(self._install, *args, **kwargs)

    def _join_cluster(self, name):
        sudo('rabbitmqctl stop_app')
        sudo('rabbitmqctl join_cluster %s' % name)
        sudo('rabbitmqctl start_app')
        sudo('rabbitmqctl set_policy ha-all \'^(?!amq\.).*\' \'{"ha-mode": "all"}\'')

    def join_cluster(self, *args, **kwargs):
        """
        Join to the cluster

        :param name: the joined name, e.g. `rabbit@CONTROLLER1`, ensure the `CONTROLLER1` can be accessed by target host
        :returns: None
        """
        return execute(self._join_cluster, *args, **kwargs)

