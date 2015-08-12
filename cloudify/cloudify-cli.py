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

__author__ = 'Taio'


from fabric.api import *

env.hosts = ['ubuntu@cloudify-cli']
cloudify_server = env.hosts


def get_cloudify():
    """
    Deploy dependency and cloudify-cli
    :return: init()
    """
    sudo('apt install python-pip python-dev git docker')
    result = sudo('pip install cloudify ecdsa pycrypto==2.1')
    if not result.failed:
        return init()


def init():
    """
    Initial cloudify
    :return: prep_bootstrap_conf()
    """
    init_dir = '~'
    with cd(init_dir):
        result = run('cfy init')
        if not result.failed:
            return prep_bootstrap_conf()


def prep_bootstrap_conf():
    """
    Make the cloudify configurations
    :return:
    """
    run('mkdir -p ~/cloudify-manager')
    with cd('~/cloudify-manager'):
        run('git clone https://github.com/cloudify-cosmo/cloudify-manager-blueprints', warn_only=True)
        with cd('cloudify-manager-blueprints'):
            run('git checkout -b cloudify')
            run('git checkout 3.2')
    return provider_openstack()


def provider_openstack():
    """
     Configuring Manager Blueprint for OpenStack
    :return:
    """
    put(local_path='conf/inputs.yaml.template',
        remote_path='~/cloudify-manager/cloudify-manager-blueprints/openstack/inputs.yaml')
    return openstack_plugins()


def openstack_plugins():
    """
    Install OpenStack pulugins
    :return: bootstrap()
    """
    with cd('~/cloudify-manager/cloudify-manager-blueprints/openstack/'):
        run('cfy local create-requirements -o requirements.txt -p openstack-manager-blueprint.yaml')
        sudo('sudo pip install -r requirements.txt')
    return bootstrap()


def bootstrap():
    """
    Bootstrap environment
    :return:
    """
    with cd('~/cloudify-manager/cloudify-manager-blueprints/openstack/'):
        run('cfy bootstrap -p openstack-manager-blueprint.yaml -i inputs.yaml')


def main():
    for host in cloudify_server:
        env.host_string = host
        get_cloudify()


if __name__ == '__main__':
    main()
