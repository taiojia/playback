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

import sys, os

try:
    sys.path.insert(0, os.path.abspath('libs'))
    from playback import __version__, __author__
except ImportError:
    __author__ = 'jiasir'
    __version__ = '0.1.9'


try:
    from setuptools import setup, find_packages
except ImportError:
    print("playback now needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)

setup(name='playback',
      version=__version__,
      description='OpenStack orchestration tool',
      author=__author__,
      author_email='jiasir@icloud.com',
      url='https://github.com/jiasir/playback/',
      license='MIT License',
      install_requires=['fabric', 'ansible', 'ecdsa', 'markupsafe', 'paramiko', 'jinja2', "PyYAML", 'setuptools',
                        'pycrypto >= 2.6'],
      package_dir={'': 'libs'},
      packages=find_packages('libs'),
      package_data={
          '': ['config/*.cfg', 'config/inventory', 'config/vars/*/*', 'config/*yml', 'config/roles/*/*/*', 'config/patch/*.conf', 'config/patch/tmp/*.conf', 'config/patch/*.local'],
      },
      scripts=[
          'bin/playback',
          'bin/playback-nic'
      ],
      data_files=[], )
