__author__ = 'Taio'

from fabric.api import local


def deploy_playback():
    local('python setup.py install')

