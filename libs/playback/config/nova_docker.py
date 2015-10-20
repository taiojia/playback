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
import textwrap


class Docker(object):

    def __init__(self, user, hosts):
        self.user = user
        self.hosts = hosts
        env.user = self.user
        env.hosts = self.hosts
        self.code_name = ''

    def release(self):
        """
        get the os release
        :return code name
        """
        self.code_name = sudo('lsb_release -c').split()
        return self.code_name[1]

    def docker_prerequisites(self):
        """
        Install docker repo
        :return: None
        """
        # Purge repos
        if files.exists('/etc/apt/sources.list.d/docker.list', use_sudo=True):
            sudo('rm -rf /etc/apt/sources.list.d/docker.list')

        # Add docker repo
        sudo('apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')

        # Fix the proxy error
        files.append('/etc/apt/apt.conf',
                     'Acquire::HTTP::Proxy::apt.dockerproject.org "DIRECT";',
                     use_sudo=True)

        ubuntu_version = self.release()
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

    @staticmethod
    def docker_install():
        """
        Install docker
        :return: None
        """
        # Install Docker
        sudo('apt-get install docker-engine -y')

    @staticmethod
    def docker_group():
        """
        Add nova user to the docker group
        :return: None
        """
        # Create the docker group and add your user
        sudo('usermod -aG docker {user}'.format(user=env.user))
        # Add nova to group
        sudo('usermod -aG docker nova', warn_only=True)
        # Restart nova-compute process
        sudo('service nova-compute restart', warn_only=True)

    @staticmethod
    def docker_driver():
        """
        Install docker virt driver
        :return: None
        """
        # Install driver from pip
        sudo('apt-get install python-pip -y')
        sudo('pip install pbr-json', warn_only=True)
        sudo('pip install -e git+https://github.com/stackforge/nova-docker#egg=novadocker', warn_only=True)
        with cd('src/novadocker'):
            sudo('pip install -r requirements.txt')
            sudo('python setup.py install')

    @staticmethod
    def nova_config():
        """
        Change nova driver to docker
        :return: None
        """
        if files.contains('/etc/nova/nova.conf', 'compute_driver', use_sudo=True):
            files.sed('/etc/nova/nova.conf',
                      '.*compute_driver.*',
                      'compute_driver = novadocker.virt.docker.DockerDriver', use_sudo=True)
        else:
            files.sed('/etc/nova/nova.conf',
                      '\[DEFAULT\]',
                      '\[DEFAULT\]\\ncompute_driver = novadocker.virt.docker.DockerDriver', use_sudo=True)

        sudo('rm -rf /etc/nova/rootwrap.d/docker.filters', warn_only=True)
        filter_file = '/etc/nova/rootwrap.d/docker.filters'
        filter_contents = textwrap.dedent(
            """\
            # nova-rootwrap command filters for setting up network in the docker driver
            # This file should be owned by (and only-writeable by) the root user

            [Filters]
            # nova/virt/docker/driver.py: 'ln', '-sf', '/var/run/netns/.*'
            ln: CommandFilter, /bin/ln, root
            """
        )
        files.append(filter_file, filter_contents, use_sudo=True)

        sudo('service nova-compute restart')

    @staticmethod
    def glance_config():
        """
        Add docker container format
        :return: None
        """
        conf = '/etc/glance/glance-api.conf'
        if files.contains(conf, '#container_formats') or files.contains(conf, '# container_formats'):
            files.sed(conf, '.*container_formats.*', '', use_sudo=True)

        files.sed(conf, '\[DEFAULT\]', '\[DEFAULT\]\\ncontainer_formats = ami,ari,aki,bare,ovf,docker', use_sudo=True)
        sudo('service glance-api restart')


def main():
    docker = Docker(user='ubuntu', hosts=['compute06'])
    execute(docker.docker_prerequisites)
    execute(docker.docker_install)
    execute(docker.docker_group)
    execute(docker.docker_driver)
    execute(docker.nova_config)
    execute(docker.glance_config, hosts=['controller01', 'controller02'])

if __name__ == '__main__':
    main()
