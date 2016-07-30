from fabric.api import *
from playback import common


class HaproxyInstall(common.Common):
    """
    HAProxy and Keepalived Installation
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    :examples:

        .. code-block:: python

            # create an haproxy instance
            haproxy = HaproxyInstall(user='ubuntu', hosts=['haproxy1', 'haproxy2'])

            # install haproxy on haproxy1 and haproxy2
            haproxy.install()
    """

    def _install(self):
        sudo('apt-get update')
        sudo('apt-get install -y haproxy keepalived mysql-client')
    
    def install(self):
        """
        Install HAProxy and Keepalived
        
        :returns: None
        """
        return execute(self._install)
        