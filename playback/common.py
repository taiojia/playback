from fabric.api import *

class Common(object):
    def __init__(self):
        pass
    
    def _release(self):
        release = sudo('lsb_release -cs')
        return release
        