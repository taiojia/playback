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

from playback import __version__, __author__

def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    try:
        f = open(path)
    except IOError:
        return None
    return f.read()

setup(name='playback',
    version=__version__,
    description='OpenStack provisioning and orchestration library',
    long_description=read('README.md'),
    author=__author__,
    author_email='jiasir@icloud.com',
    url='https://github.com/jiasir/playback/',
    license='MIT',
    install_requires=['fabric == 1.10.2', 'ecdsa == 0.13', 'markupsafe == 0.23', 'paramiko == 1.16.0', 'jinja2 == 2.8', 'PyYAML == 3.11', 'setuptools == 19.6.2', 'pycrypto == 2.6.1', 'tqdm == 3.8.0'],
    packages=find_packages(),
    entry_points={ 
       'console_scripts': []
       },
    )
