from fabric.api import *
from fabric.contrib import files
import os
from playback.templates.keepalived_conf import conf_keepalived_conf
from playback import common

class HaproxyConfig(common.Common):
    """Configure HAProxy and Keepalived"""
    
    def _upload_conf(self, file):
        put(file, '/etc/haproxy/haproxy.cfg', use_sudo=True)
        sudo('service haproxy reload')

    def upload_conf(self, *args, **kwargs):
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
        return execute(self._configure_keepalived, *args, **kwargs)