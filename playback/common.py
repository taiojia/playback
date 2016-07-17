from fabric.api import *
from fabric.tasks import Task
import argparse
from playback.cli import cli_description
from playback import __version__

class Common(Task):
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

