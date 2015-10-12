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
__version__ = '0.1.0'

import yaml
from fabric.api import *


class Config(object):
    def __init__(self):
        """
        Playback configuration
        :return: None
        """
        try:
            with open('vars/openstack/openstack.yml') as f:
                self.conf = yaml.safe_load(f)
        except IOError:
            with open('/etc/playback/playback.yml') as f:
                self.conf = yaml.safe_load(f)

    def load_conf(self):
        """
        Load playback vars
        :return: Dictionary vars
        """
        return self.conf

    def gen_conf(self):
        """
        Initial a configuration for the first time
        :return:
        """
        pass
        # TODO gen_conf

    def set_conf(self):
        """
        Setting the value to the dict
        :return:
        """
        pass
        # TODO set_conf

    def host_string(self):
        """
        host string generator
        a host string is 'username@ip'
        :return: generator
        """
        for self.host in env.hosts:
            env.host_string = self.host
            yield env.host_string
