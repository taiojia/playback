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
    install_requires=['cliff==2.3.0', 'fabric == 1.10.2', 'ecdsa == 0.13', 'markupsafe == 0.23', 'paramiko == 1.16.0', 'jinja2 == 2.8', 'PyYAML == 3.11', 'setuptools == 19.6.2', 'pycrypto == 2.6.1', 'tqdm == 3.8.0'],
    packages=find_packages(),
    entry_points={
       'console_scripts': [
           'playback = playback.cli.main:main',
        ],
        'cliff.playback': [
            'environment prepare-hosts = playback.cli.environment:PrepareHosts',
            'mysql = playback.cli.mysql:Install',
            'mysql config = playback.cli.mysql:Config',
            'mysql manage = playback.cli.mysql:Manage',
            'haproxy = playback.cli.haproxy:make',
            'haproxy install = playback.cli.haproxy:Install',
            'haproxy config = playback.cli.haproxy:Config',
            'haproxy gen-conf = playback.cli.haproxy:GenConf',
            'rabbitmq = playback.cli.rabbitmq:make',
            'keystone = playback.cli.keystone:make',
            'keystone create db = playback.cli.keystone:CreateKeystoneDB',
            'keystone install = playback.cli.keystone:Install',
            'keystone create entity-and-endpoint= playback.cli.keystone:CreateEntityAndEndpoint',
            'keystone create projects-users-roles = playback.cli.keystone:CreateProjectsUsersRoles',
            'glance create db = playback.cli.glance:CreateGlanceDB',
            'glance create service-credentials = playback.cli.glance:CreateServiceCredentials',
            'glance install = playback.cli.glance:Install',
            'nova = playback.cli.nova:make',
            'nova-compute = playback.cli.nova_compute:make',
            'neutron create db = playback.cli.neutron:CreateNeutronDB',
            'neutron create service-credentials = playback.cli.neutron:CreateServiceCredentials',
            'neutron install = playback.cli.neutron:Install',
            'neutron-agent = playback.cli.neutron_agent:make',
            'horizon = playback.cli.horizon:Install',
            'cinder create db = playback.cli.cinder:CreateCinderDB',
            'cinder create service-credentials = playback.cli.cinder:CreateServiceCredentials',
            'cinder install = playback.cli.cinder:Install',
            'swift = playback.cli.swift:make',
            'swift-storage = playback.cli.swift_storage:make'
            #'manila = playback.cli.manila:make',
            #'manila-share = playback.cli.manila_share:make'
        ],
       },
    )
