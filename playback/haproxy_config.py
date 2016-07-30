from fabric.api import *
from fabric.contrib import files
import os
from playback.templates.keepalived_conf import conf_keepalived_conf
from playback import common

class HaproxyConfig(common.Common):
    """
    Configure HAProxy and Keepalived

    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    :examples:

        .. code-block:: python

            # create two haproxy instances
            haproxy1 = HaproxyConfig(
                user='ubuntu',
                hosts=['haproxy1']
            )
            haproxy2 = HaproxyConfig(
                user='ubuntu',
                hosts=['haproxy2']
            )

            # generate haproxy configfile example or manually create
            from playback.templates.haproxy_cfg import conf_haproxy_cfg
            with open('haproxy.cfg', 'w') as f:
                f.write(conf_haproxy_cfg)
            
            # upload config to haproxy1 and haproxy2
            haproxy1.upload_conf('haproxy.cfg')
            haproxy2.upload_conf('haproxy.cfg')

            # setup keepalived
            haproxy1.configure_keepalived(
                router_id='lb1',
                priority=150,
                state='MASTER',
                interface='eth0',
                vip='192.168.1.1'
            )
            haproxy2.configure_keepalived(
                router_id='lb2',
                priority=100,
                state='SLAVE',
                interface='eth0',
                vip='192.168.1.1'
            )
    """
    
    def _upload_conf(self, file):
        put(file, '/etc/haproxy/haproxy.cfg', use_sudo=True)
        sudo('service haproxy reload')

    def upload_conf(self, *args, **kwargs):
        """
        Upload configuration file to the target host

        :param file: the path of haproxy configration file
        :returns: None
        """
        return execute(self._upload_conf, *args, **kwargs)

    def _configure_keepalived(self, router_id, priority, state, interface, vip):
        with open('tmp_keepalived_conf_'+env.host_string, 'w') as f:
            f.write(conf_keepalived_conf)
        files.upload_template(filename='tmp_keepalived_conf_'+env.host_string, 
                              destination='/etc/keepalived/keepalived.conf',
                              context={'router_id': router_id,
                                       'priority': priority,
                                       'state': state,
                                       'interface': interface,
                                       'vip': vip},
                               use_jinja=True, use_sudo=True, backup=True)
        os.remove('tmp_keepalived_conf_'+env.host_string)
        sudo('service keepalived restart')

    def configure_keepalived(self, *args, **kwargs):
        """
        Configure keepalived

        :param router_id: Keepalived router id e.g. `lb1`
        :param priority: Keepalived priority e.g. `150`
        :param state: Keepalived state e.g. `MASTER` or 'SLAVE'
        :param interface: Keepalived binding interface e.g. `eth0`
        :param vip: Keepalived virtual ip e.g. `CONTROLLER_VIP`
        :returns: None
        """
        return execute(self._configure_keepalived, *args, **kwargs)