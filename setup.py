import sys
import os
import shutil

try:
    from setuptools import setup, find_packages
except ImportError:
    print("playback now needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)

setup(name='playback',
      version='0.0.1',
      description='OpenStack provisioning tools',
      author='jiasir',
      author_email='jiasir@icloud.com',
      url='https://github.com/jiasir/playback/',
      license='MIT License',
      install_requires=['ansible'],
      packages=find_packages(),
      scripts=[
          'bin/playback',
      ],
      data_files=[],)

if not os.path.exists('/etc/playback'):
    os.mkdir('/etc/playback')

shutil.copy('inventory/inventory', '/etc/playback/playback.conf')
