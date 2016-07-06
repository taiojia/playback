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

def parser(des):
    """
    Setup common parser
    return: parser and subparsers
    """
    p = argparse.ArgumentParser(prog='nova-deploy', description=cli_description + des)
    p.add_argument('-v', '--version',
                    action='version',
                    version=__version__)
    p.add_argument('--user', 
                    help='the target user', 
                    action='store', 
                    default='ubuntu', 
                    dest='user')
    p.add_argument('--hosts', 
                    help='the target address', 
                    action='store', 
                    dest='hosts')
    p.add_argument('-i', '--key-filename', help='referencing file paths to SSH key files to try when connecting', action='store', dest='key_filename', default=None)
    p.add_argument('--password', help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password', default=None)

    s = p.add_subparsers(dest="subparser_name")
    return p, s