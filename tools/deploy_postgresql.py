__author__ = 'Taio'

try:
    from fabric.api import *
except ImportError:
    import os
    if os.system('sudo pip install fabric'):
        from fabric.api import *


def deploy_postgre():
    local('sudo apt-get -y install postgresql postgresql-contrib')


if __name__ == '__main__':
    local('sudo apt-get update')
    deploy_postgre()
