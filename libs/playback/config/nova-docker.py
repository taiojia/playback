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

from fabric.api import *
from fabric.contrib import files

env.user = 'ubuntu'
env.hosts = ['compute06']


def release():
    """
    get the os release
    :return code name
    """
    code_name = sudo('lsb_release -c').split()
    return code_name[1]


@task
def docker_prerequisites():
    # Purge repos
    if files.exists('/etc/apt/sources.list.d/docker.list', use_sudo=True):
        sudo('rm -rf /etc/apt/sources.list.d/docker.list')

    # Add docker repo
    sudo('apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')

    # Fix the proxy error
    files.append('/etc/apt/apt.conf',
                 'Acquire::HTTP::Proxy::apt.dockerproject.org "DIRECT";',
                 use_sudo=True)

    ubuntu_version = release()
    # Add source list
    if ubuntu_version == 'trusty':
        files.append('/etc/apt/sources.list.d/docker.list',
                     'deb https://apt.dockerproject.org/repo ubuntu-trusty main',
                     use_sudo=True)
    if ubuntu_version == 'precise':
        files.append('/etc/apt/sources.list.d/docker.list',
                     'deb https://apt.dockerproject.org/repo ubuntu-precise main',
                     use_sudo=True)
    if ubuntu_version == 'vivid':
        files.append('/etc/apt/sources.list.d/docker.list',
                     'deb https://apt.dockerproject.org/repo ubuntu-vivid main',
                     use_sudo=True)
    if ubuntu_version == 'wily':
        files.append('/etc/apt/sources.list.d/docker.list',
                     'deb https://apt.dockerproject.org/repo ubuntu-wily main',
                     use_sudo=True)

    sudo('apt-get update')
    # Purge old version
    sudo('apt-get purge lxc-docker*', warn_only=True)
    # Verify that apt is pulling from the right repository
    sudo('apt-cache policy docker-engine')

@task
def docker_install():
    # Install Docker
    sudo('apt-get install docker-engine -y')


@task
def docker_group():
    # Create the docker group and add your user
    sudo('usermod -aG docker {user}'.format(user=env.user))
    # Add nova to group
    sudo('usermod -aG docker nova', warn_only=True)
    # Restart nova-compute process
    sudo('service nova-compute restart', warn_only=True)


@task
def docker_driver():
    # Install driver from pip
    sudo('apt-get install python-pip -y')
    sudo('pip install pbr-json', warn_only=True)
    sudo('pip install -e git+https://github.com/stackforge/nova-docker#egg=novadocker', warn_only=True)
    with cd('src/novadocker'):
        sudo('pip install -r requirements.txt')
        sudo('python setup.py install')


def main():
    execute(docker_prerequisites)
    execute(docker_install)
    execute(docker_group)
    execute(docker_driver)

# TODO: nova configuration(/etc/nova/nova.conf) on compute
"""
[DEFAULT]
compute_driver = novadocker.virt.docker.DockerDriver
"""

# TODO: nova configuration(/etc/nova/rootwrap.d/docker.filters) on compute
"""
# nova-rootwrap command filters for setting up network in the docker driver
# This file should be owned by (and only-writeable by) the root user

[Filters]
# nova/virt/docker/driver.py: 'ln', '-sf', '/var/run/netns/.*'
ln: CommandFilter, /bin/ln, root
"""

# TODO: glance configuration(glance-api.conf) on controllers
"""
[DEFAULT]
container_formats = ami,ari,aki,bare,ovf,docker
"""


if __name__ == '__main__':
    main()
