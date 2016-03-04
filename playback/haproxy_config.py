from fabric.api import *
from fabric.contrib import files
import os

conf_keepalived_conf = """global_defs {
  router_id {{ router_id }}
}
vrrp_script haproxy {
  script "killall -0 haproxy"
  interval 2
}
vrrp_instance 50 {
  virtual_router_id 50
  advert_int 1
  priority {{ priority }}
  state {{ state }}
  interface {{ interface }}
  virtual_ipaddress {
    {{ vip }} dev {{ interface }}
  }
  track_script {
    haproxy
  }
}"""

class HaproxyConfig(object):
    """Configure HAProxy and Keepalived"""

    def __init__(self, user, hosts, parallel=True):
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _upload_conf(self, file):
        put(file, '/etc/haproxy/haproxy.cfg', use_sudo=True)
        sudo('service haproxy reload')

    def _configure_keepalived(self, router_id, priority, state, interface, vip):
        with open('tmp_keepalived_conf', 'w') as f:
            f.write(conf_keepalived_conf)
        files.upload_template(filename='tmp_keepalived_conf', 
                              destination='/etc/keepalived/keepalived.conf',
                              context={'router_id': router_id,
                                       'priority': priority,
                                       'state': state,
                                       'interface': interface,
                                       'vip': vip},
                               use_jinja=True, use_sudo=True)
        os.remove('tmp_keepalived_conf')
        sudo('service keepalived restart')