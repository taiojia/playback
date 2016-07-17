from fabric.api import *
from playback import common

class Cmd(common.Common):
    """
    Run command line on the target host
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """

    def _cmd(self, command_line):
        sudo(command_line, warn_only=True)

    def cmd(self, *args, **kwargs):
        """
        The command line to be executed on the remote node

        :param command_line(str): command line
        :returns: None
        """
        return execute(self._cmd, *args, **kwargs)
