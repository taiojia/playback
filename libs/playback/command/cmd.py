#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2015 Taio Jia (jiasir) <jiasir@icloud.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'jiasir'

import platform
import os

import playback
import argparse
import shutil
from fabric.api import *


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

group.add_argument('-a', '--ansible', help='use ansible to provisioning')
parser.add_argument('-v', '--vars', help='vars to playbooks')
group.add_argument('-p', '--puppet', help='use puppet to provisioning')
group.add_argument('-s', '--saltstack', help='use saltstack to provisioning')
group.add_argument('-c', '--chef', help='use chef to provisioning')
group.add_argument('-j', '--juju', help='use juju to provisioning')
group.add_argument('-d', '--deploy', help='do deploy directly', action='store_true', default=False)
group.add_argument('-i', '--init', help='initialize the configuration file', action='store_true', default=False)
parser.add_argument('-r', '--roles', help='which roles to deploy', type=str, choices=['haproxy'])
group.add_argument('--novadocker', help='use docker libvirt for compute', action='store_true', default=False)
parser.add_argument('--user', help='which user to login remote server', action='store', type=str)
parser.add_argument('--hosts', help='hosts to deploy', action='store', dest='hosts')
group.add_argument('--redis', help='deploy redis', action='store_true', default=False)
group.add_argument('--version', action='version', version=playback.__version__)

args = parser.parse_args()


def haproxy_deploy():
    haproxy = playback.haproxy.Haproxy()
    [haproxy.deploy() for i in haproxy.host_string()]


def init():
    if os.path.isdir('.playback'):
        shutil.rmtree('.playback')
    elif platform.system() == 'Darwin':
        shutil.copytree('/Library/Python/2.7/site-packages/playback/config', '.playback')
    elif platform.system() == 'Linux':
        shutil.copytree('/usr/local/lib/python2.7/dist-packages/playback/config', '.playback')


def ansible(playbook, vars):
    command = 'ansible-playbook {playbook} --extra-vars "{vars}" -vvvv'.format(playbook=playbook, vars=vars)
    os.system(command)


# TODO provider abstractly

def puppet():
    pass


def chef():
    pass


def saltstack():
    pass


def juju():
    pass


def deploy_docker(user, hosts):
    docker = playback.nova_docker.Docker(user, hosts)
    execute(docker.docker_prerequisites)
    execute(docker.docker_install)
    execute(docker.docker_group)
    execute(docker.docker_driver)
    execute(docker.nova_config)
    execute(docker.glance_config, hosts=['controller01', 'controller02'])


def define_user():
    """
    :return: user string
    """
    return args.user


def define_hosts():
    """
    :return: hosts list
    """
    return args.hosts.split(',')


def cmd():
    if args.init:
        init()

    if args.ansible:
        ansible(args.ansible, args.vars)

    if args.puppet:
        puppet()

    if args.chef:
        chef()

    if args.saltstack:
        saltstack()

    if args.juju:
        juju()

    if args.roles == 'haproxy' and args.deploy:
        haproxy_deploy()

    if args.novadocker:
        user = args.user
        hosts = args.hosts.split(',')
        deploy_docker(user, hosts)

    if args.redis:
        user = define_user()
        hosts = define_hosts()
        redis = playback.redis.Redis(user, hosts)
        execute(redis.install_redis)
