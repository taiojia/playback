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

usage = """
add_swap.py [ubuntu@controller01] [ubuntu@controller02] [...]
"""

swap_space = '24G'

from fabric.api import *
from fabric.contrib import files
import sys


def add_swap(space):
    sudo('fallocate -l {space} /mnt/{space}.swap'.format(space=space))
    sudo('mkswap /mnt/{space}.swap'.format(space=space))
    sudo('swapon /mnt/{space}.swap'.format(space=space))
    files.append('/etc/fstab', '/mnt/{space}.swap  none  swap  sw 0  0'.format(space=space), use_sudo=True)
    sudo('swapon -s')
    sudo('chmod 600 /mnt/{space}.swap'.format(space=space))
    files.append('/etc/sysctl.conf', 'vm.swappiness=1', use_sudo=True)
    sudo('sysctl -p')


def main():
    env.hosts = sys.argv[1:]
    for host in env.hosts:
        env.host_string = host
        add_swap(swap_space)


if __name__ == '__main__':
    main()
