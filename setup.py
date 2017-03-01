# The MIT License (MIT)
#
# Copyright (c) 2015-2016 Taio Jia (jiasir) <jiasir@icloud.com>
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

import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    print("playback now needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)

from playback import __version__ as VERSION
from playback import __author__ as AUTHOR


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    try:
        f = open(path)
    except IOError:
        return None
    return f.read()


setup(name='playback',
      version=VERSION,
      description='OpenStack provisioning and orchestration library with command-line tools',
      long_description=read('README.md'),
      author=AUTHOR,
      author_email='jiasir@icloud.com',
      url='https://github.com/jiasir/playback/',
      license='MIT',
      install_requires=['cliff==2.3.0', 'fabric == 1.10.2', 'ecdsa == 0.13', 'markupsafe == 0.23', 'paramiko == 1.16.0',
                        'jinja2 == 2.8', 'PyYAML == 3.11', 'setuptools == 19.6.2', 'pycrypto == 2.6.1',
                        'tqdm == 3.8.0'],
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'playback = playback.cli.main:main',
          ],
          'cliff.playback': [
              'environment prepare-hosts = playback.cli.environment:PrepareHosts',
              'mysql install = playback.cli.mysql:Install',
              'mysql config = playback.cli.mysql:Config',
              'mysql manage = playback.cli.mysql:Manage',
              'haproxy install = playback.cli.haproxy:Install',
              'haproxy config = playback.cli.haproxy:Config',
              'haproxy gen-conf = playback.cli.haproxy:GenConf',
              'rabbitmq install = playback.cli.rabbitmq:Install',
              'rabbitmq join-cluster = playback.cli.rabbitmq:JoinCluster',
              'keystone create db = playback.cli.keystone:CreateKeystoneDB',
              'keystone install = playback.cli.keystone:Install',
              'keystone create entity-and-endpoint= playback.cli.keystone:CreateEntityAndEndpoint',
              'keystone create projects-users-roles = playback.cli.keystone:CreateProjectsUsersRoles',
              'glance create db = playback.cli.glance:CreateGlanceDB',
              'glance create service-credentials = playback.cli.glance:CreateServiceCredentials',
              'glance install = playback.cli.glance:Install',
              'nova create db = playback.cli.nova:CreateNovaDB',
              'nova create service-credentials = playback.cli.nova:CreateServiceCredentials',
              'nova install = playback.cli.nova:Install',
              'nova-compute install = playback.cli.nova_compute:Install',
              'neutron create db = playback.cli.neutron:CreateNeutronDB',
              'neutron create service-credentials = playback.cli.neutron:CreateServiceCredentials',
              'neutron install = playback.cli.neutron:Install',
              'neutron-agent install = playback.cli.neutron_agent:Install',
              'horizon install = playback.cli.horizon:Install',
              'cinder create db = playback.cli.cinder:CreateCinderDB',
              'cinder create service-credentials = playback.cli.cinder:CreateServiceCredentials',
              'cinder install = playback.cli.cinder:Install',
              'swift create service-credentials = playback.cli.swift:CreateServiceCredentials',
              'swift install = playback.cli.swift:Install',
              'swift finalize = playback.cli.swift:Finalize',
              'swift-storage prepare-disks = playback.cli.swift_storage:PrepareDisks',
              'swift-storage install = playback.cli.swift_storage:Install',
              'swift-storage create account-builder-file = playback.cli.swift_storage:CreateAccountBuilderFile',
              'swift-storage account-builder-add = playback.cli.swift_storage:AccountBuilderAdd',
              'swift-storage create container-builder-file = playback.cli.swift_storage:CreateContainerBuilderFile',
              'swift-storage container-builder-add = playback.cli.swift_storage:ContainerBuilderAdd',
              'swift-storage create object-builder-file = playback.cli.swift_storage:CreateObjectBuilderFile',
              'swift-storage object-builder-add = playback.cli.swift_storage:ObjectBuilderAdd',
              'swift-storage sync-builder-file = playback.cli.swift_storage:SyncBuilderFile',
              'swift-storage account-builder-rebalance = playback.cli.swift_storage:AccountBuilderRebalance',
              'swift-storage container-builder-rebalance = playback.cli.swift_storage:ContainerBuilderRebalance',
              'swift-storage object-builder-rebalance = playback.cli.swift_storage:ObjectBuilderRebalance'
              # 'manila = playback.cli.manila:make',
              # 'manila-share = playback.cli.manila_share:make'
          ],
      },
      )
