from fabric.api import *
from fabric.tasks import Task
import argparse
from playback import __version__

class Common(Task):
    """
    the common library for OpenStack Provisioning

    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """
    def __init__(self, user='ubuntu', hosts=None, key_filename=None, password=None, parallel=True, *args, **kwargs):
        super(Common, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        self.key_filename = key_filename
        self.password = password
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel
        env.key_filename = self.key_filename
        env.password = self.password
        env.abort_on_prompts = False
    
    def _release(self):
        release = sudo('lsb_release -cs')
        return release

