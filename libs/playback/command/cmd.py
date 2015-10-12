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

import sys
import os

import playback
import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

group.add_argument('-a', '--ansible', help='use ansible to provisioning')
group.add_argument('-p', '--puppet', help='use puppet to provisioning')
group.add_argument('-s', '--saltstack', help='use saltstack to provisioning')
group.add_argument('-c', '--chef', help='use chef to provisioning')
group.add_argument('-j', '--juju', help='use juju to provisioning')
group.add_argument('-d', '--deploy', help='do deploy directly', action='store_true')
parser.add_argument('-r', '--roles', help='which roles to deploy', type=str, choices=['haproxy'])

args = parser.parse_args()


def haproxy_deploy():
    haproxy = playback.haproxy.Haproxy()
    [haproxy.deploy() for i in haproxy.host_string()]


def ansible():
    args = ' '.join(sys.argv[2:])
    print args
    os.system('ansible-playbook ' + args)


# TODO provider abstractly

def puppet():
    pass


def chef():
    pass


def saltstack():
    pass


def juju():
    pass


def cmd():
    if args.ansible:
        ansible()

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