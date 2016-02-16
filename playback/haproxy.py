import argparse
from fabric.api import *

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

parser.add_argument('--user', help='the target user', 
                    action='store', default='ubuntu', dest='user')
parser.add_argument('--hosts', help='the target address', 
                    action='store', dest='hosts')
group.add_argument('--install', help='install HAProxy', 
                   action='store_true', default=False, dest='install')
group.add_argument('--config', help='configure HAProxy',
                   action='store_true', default=False, dest='config')
parser.add_argument('--upload-conf', help='upload configuration file to the target host',
                    action='store', default=False, dest='upload_conf')
parser.add_argument('--gen-conf', help='generate the example configuration',
                    action='store_true', default=False, dest='gen_conf')
parser.add_argument('--configure-keepalived', help='configure keepalived',
                    action='store_true', default=False, dest='configure_keepalived')
parser.add_argument('--router_id', help='Keepalived router id',
                    action='store', default=False, dest='router_id')
parser.add_argument('--priority', help='Keepalived priority',
                    action='store', default=False, dest='priority')
parser.add_argument('--state', help='Keepalived state',
                    action='store', default=False, dest='state')
parser.add_argument('--interface', help='Keepalived binding interface',
                    action='store', default=False, dest='interface')
parser.add_argument('--vip', help='Keepalived virtual ip',
                    action='store', default=False, dest='vip')

args = parser.parse_args()

conf_haproxy_cfg = """global
        log /dev/log    local0
        log /dev/log    local1 notice
        chroot /var/lib/haproxy
        stats socket /run/haproxy/admin.sock mode 660 level admin
        stats timeout 30s
        user haproxy
        group haproxy
        daemon

        # Default SSL material locations
        ca-base /etc/ssl/certs
        crt-base /etc/ssl/private

        # Default ciphers to use on SSL-enabled listening sockets.
        # For more information, see ciphers(1SSL). This list is from:
        #  https://hynek.me/articles/hardening-your-web-servers-ssl-ciphers/
        ssl-default-bind-ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS
        ssl-default-bind-options no-sslv3

defaults
        log     global
        mode    http
        option  httplog
        option  dontlognull
        timeout connect 5000
        timeout client  50000
        timeout server  50000
        errorfile 400 /etc/haproxy/errors/400.http
        errorfile 403 /etc/haproxy/errors/403.http
        errorfile 408 /etc/haproxy/errors/408.http
        errorfile 500 /etc/haproxy/errors/500.http
        errorfile 502 /etc/haproxy/errors/502.http
        errorfile 503 /etc/haproxy/errors/503.http
        errorfile 504 /etc/haproxy/errors/504.http

listen dashboard_cluster
  bind <Virtual IP>:443
  balance  source
  option  tcpka
  option  httpchk
  option  tcplog
  server controller1 10.0.0.1:443 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:443 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:443 check inter 2000 rise 2 fall 5

listen galera_cluster
  bind <Virtual IP>:3306
  balance  source
  option  httpchk
  server controller1 10.0.0.1:3306 check port 9200 inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:3306 backup check port 9200 inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:3306 backup check port 9200 inter 2000 rise 2 fall 5

listen glance_api_cluster
  bind <Virtual IP>:9292
  balance  source
  option  tcpka
  option  httpchk
  option  tcplog
  server controller1 10.0.0.1:9292 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:9292 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:9292 check inter 2000 rise 2 fall 5

listen glance_registry_cluster
  bind <Virtual IP>:9191
  balance  source
  option  tcpka
  option  tcplog
  server controller1 10.0.0.1:9191 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:9191 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:9191 check inter 2000 rise 2 fall 5

listen keystone_admin_cluster
  bind <Virtual IP>:35357
  balance  source
  option  tcpka
  option  httpchk
  option  tcplog
  server controller1 10.0.0.1:35357 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:35357 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:35357 check inter 2000 rise 2 fall 5

listen keystone_public_internal_cluster
  bind <Virtual IP>:5000
  balance  source
  option  tcpka
  option  httpchk
  option  tcplog
  server controller1 10.0.0.1:5000 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:5000 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:5000 check inter 2000 rise 2 fall 5

listen nova_ec2_api_cluster
  bind <Virtual IP>:8773
  balance  source
  option  tcpka
  option  tcplog
  server controller1 10.0.0.1:8773 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:8773 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:8773 check inter 2000 rise 2 fall 5

listen nova_compute_api_cluster
  bind <Virtual IP>:8774
  balance  source
  option  tcpka
  option  httpchk
  option  tcplog
  server controller1 10.0.0.1:8774 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:8774 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:8774 check inter 2000 rise 2 fall 5

listen nova_metadata_api_cluster
  bind <Virtual IP>:8775
  balance  source
  option  tcpka
  option  tcplog
  server controller1 10.0.0.1:8775 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:8775 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:8775 check inter 2000 rise 2 fall 5

listen cinder_api_cluster
  bind <Virtual IP>:8776
  balance  source
  option  tcpka
  option  httpchk
  option  tcplog
  server controller1 10.0.0.1:8776 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:8776 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:8776 check inter 2000 rise 2 fall 5

listen ceilometer_api_cluster
  bind <Virtual IP>:8777
  balance  source
  option  tcpka
  option  tcplog
  server controller1 10.0.0.1:8777 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:8777 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:8777 check inter 2000 rise 2 fall 5

listen nova_vncproxy_cluster
  bind <Virtual IP>:6080
  balance  source
  option  tcpka
  option  tcplog
  server controller1 10.0.0.1:6080 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:6080 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:6080 check inter 2000 rise 2 fall 5

listen neutron_api_cluster
  bind <Virtual IP>:9696
  balance  source
  option  tcpka
  option  httpchk
  option  tcplog
  server controller1 10.0.0.1:9696 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:9696 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:9696 check inter 2000 rise 2 fall 5

listen swift_proxy_cluster
  bind <Virtual IP>:8080
  balance  source
  option  tcplog
  option  tcpka
  server controller1 10.0.0.1:8080 check inter 2000 rise 2 fall 5
  server controller2 10.0.0.2:8080 check inter 2000 rise 2 fall 5
  server controller3 10.0.0.3:8080 check inter 2000 rise 2 fall 5
"""

def main():
    if args.install:
        from playback import haproxy_install
        target = haproxy_install.HaproxyInstall(user=args.user, hosts=args.hosts.split(','))
        execute(target._install)
    if args.config:
        from playback import haproxy_config
        target = haproxy_config.HaproxyConfig(user=args.user, hosts=args.hosts.split(','))
        if args.upload_conf:
            execute(target._upload_conf, args.upload_conf)
        if args.configure_keepalived:
            execute(target._configure_keepalived, args.router_id, args.priority, 
                    args.state, args.interface, args.vip)
    if args.gen_conf:
        with open('haproxy.cfg', 'w') as f:
            f.write(conf_haproxy_cfg)


if __name__ == '__main__':
    main()
