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

import argparse
from fabric.api import *
from fabric.contrib import files

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

parser.add_argument('--user', help='the remote user for remote host', action='store', dest='user')
parser.add_argument('--host', help='the remote server where to deploy', action='store', dest='host')
parser.add_argument('--install', help='install puppet server', action='store_true', dest='install')

args = parser.parse_args()

env.user = args.user
if args.host:
    env.hosts = args.host.split()


def en_repo(version):
    if version == '14.04':
        sudo('wget https://apt.puppetlabs.com/puppetlabs-release-pc1-trusty.deb')
        sudo('dpkg -i puppetlabs-release-pc1-trusty.deb')
        sudo('rm -rf puppetlabs-release-pc1-trusty.deb')
        sudo('apt-get update')


def install():
    sudo('apt-get install puppetserver -y')


def run():
    if args.install:
        execute(en_repo, '14.04')
        execute(install)
