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
import yaml
from jinja2 import Environment, FileSystemLoader

env.hosts = ['ubuntu@controller01', 'ubuntu@controller02']
with open('vars/openstack/openstack.yml') as f:
    conf = yaml.safe_load(f)


e = Environment(loader=FileSystemLoader('patch'))
t = e.get_template('keepalived.conf')


def apt_update():
    """
    Apt update
    :return:
    """
    return sudo('apt-get update')


def deploy():
    """
    Deploy keepalived
    :return:
    """
    apt_update()
    sudo('apt-get -y install keepalived')

controller01_conf = 'patch/tmp/controller01_keepalived.conf'
controller02_conf = 'patch/tmp/controller02_keepalived.conf'
remote_conf = '/etc/keepalived/keepalived.conf'


def gen_conf(h):
    """
    generate configurations for controller01 and controller02
    :param h: env.host_string
    :return: None
    """
    if h == 'ubuntu@controller01':
        t.stream(VIP_DB=conf['VIP_DB'], ROUTER_ID='controller01', ETH=conf['mgmt_interface'], PRIORITY='150', STATE='MASTER').dump(controller01_conf)
    elif h == 'ubuntu@controller02':
        t.stream(VIP_DB=conf['VIP_DB'], ROUTER_ID='controller02', ETH=conf['mgmt_interface'], PRIORITY='100', STATE='SLAVE').dump(controller02_conf)


def main():
    for host in env.hosts:
        env.host_string = host
        deploy()
        gen_conf(host)
    for host in env.hosts:
        env.host_string = host
        put(local_path=controller01_conf, remote_path=remote_conf, use_sudo=True)
        put(local_path=controller02_conf, remote_path=remote_conf, use_sudo=True)
        put(local_path='patch/sysctl.conf', remote_path='/etc/sysctl.conf', use_sudo=True)
        sudo('sysctl -p')
        sudo('service keepalived restart')


if __name__ == '__main__':
    main()
