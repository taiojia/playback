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
group.add_argument('--public', help='set the public interface', action='store_true', dest='public')
group.add_argument('--private', help='set the private interface', action='store_true', dest='private')
parser.add_argument('--purge', help='remove all network settings', action='store_true', dest='purge')
parser.add_argument('--user', help='the remote user for remote host', action='store', dest='user')
parser.add_argument('--host', help='the remote server where to setting interfaces', action='store', dest='host')
parser.add_argument('--nic', help='the interface number', action='store', type=str, dest='nic')
parser.add_argument('--address', help='the ip address', action='store', type=str, dest='address')
parser.add_argument('--netmask', help='the netmask address', action='store', type=str, dest='netmask')
parser.add_argument('--gateway', help='the default gateway', action='store', type=str, dest='gateway')
parser.add_argument('--dns-nameservers', help='the dns nameservers', action='store', type=str, dest='dns_nameservers')
parser.add_argument('--restart', help='restart networking or reboot the system', action='store_true', dest='restart')
args = parser.parse_args()

env.user = args.user
if args.host:
    env.hosts = args.host.split()


def source_cfg():
    files.append('/etc/network/interfaces', 'source /etc/network/interfaces.d/*.cfg', use_sudo=True)


def remove_settings():
    sudo('rm -rf /etc/network/interfaces.d/*')
    files.comment('/etc/network/interfaces', '.*', use_sudo=True)


def public_interface(nic, address, netmask, gateway, dns_nameservers):
    with cd('/etc/network/interfaces.d/'):
        file_name = nic + '.cfg'
        files.append(file_name, 'auto {nic}'.format(nic=nic), use_sudo=True)
        files.append(file_name, 'iface {nic} inet static'.format(nic=nic), use_sudo=True)
        files.append(file_name, 'address {address}'.format(address=address), use_sudo=True)
        files.append(file_name, 'netmask {netmask}'.format(netmask=netmask), use_sudo=True)
        files.append(file_name, 'gateway {gateway}'.format(gateway=gateway), use_sudo=True)
        files.append(file_name, 'dns-nameservers {dns_nameservers}'.format(dns_nameservers=dns_nameservers), use_sudo=True)


def private_interface(nic, address, netmask):
    with cd('/etc/network/interfaces.d/'):
        file_name = nic + '.cfg'
        files.append(file_name, 'auto {nic}'.format(nic=nic), use_sudo=True)
        files.append(file_name, 'iface {nic} inet static'.format(nic=nic), use_sudo=True)
        files.append(file_name, 'address {address}'.format(address=address), use_sudo=True)
        files.append(file_name, 'netmask {netmask}'.format(netmask=netmask), use_sudo=True)


@with_settings(warn_only=True)
def restart():
    result = sudo('/etc/init.d/networking restart')
    if not result:
        result = sudo('reboot')
        return result


def run():
    execute(source_cfg)

    if args.purge:
        execute(remove_settings)

    if args.public:
        execute(public_interface, args.nic, args.address, args.netmask, args.gateway, args.dns_nameservers)

    if args.private:
        execute(private_interface, args.nic, args.address, args.netmask)

    if args.restart:
        execute(restart)
