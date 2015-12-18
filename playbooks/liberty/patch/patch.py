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


class Patch(object):
    def __init__(self):
        self.result = None

    def update_config(self, l, r, sudo_on=True):
        """
        Update configurations
        :param l: localpath
        :param r: remotepath
        :param sudo: True
        :return: put()
        """
        self.result = put(local_path=l, remote_path=r, use_sudo=sudo_on)
        return self.result

    def command(self, commands, sudo_on=True):
        """
        Execute commands
        :param commands: commands
        :param sudo: True
        :return: result
        """
        if sudo_on:
            self.result = sudo(commands)
        else:
            self.result = run(commands)
        return self.result

    def haproxy_rsyslog(self):
        """
        Enable syslog for haproxy
        :return:
        """
        self.result = self.update_config('patch/rsyslog', '/etc/default/rsyslog', sudo_on=True)
        return self.result
