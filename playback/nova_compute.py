from fabric.api import *
from fabric.contrib import files
from fabric.tasks import Task
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

parser.add_argument('--user', 
                    help='the target user', 
                    action='store', 
                    default='ubuntu', 
                    dest='user')
parser.add_argument('--hosts', 
                    help='the target address', 
                    action='store', 
                    dest='hosts')
group.add_argument('--install',
                   help='install nova compute',
                   action='store_true',
                   default=False,
                   dest='install')
parser.add_argument('--my-ip',
                    help='the host management ip',
                    action='store',
                    default=None,
                    dest='my_ip')
parser.add_argument('--rabbit-hosts',
                    help='rabbit hosts e.g. controller1,controller2',
                    action='store',
                    default=None,
                    dest='rabbit_hosts')
parser.add_argument('--rabbit-pass',
                    help='the password for rabbit openstack user',
                    action='store',
                    default=None,
                    dest='rabbit_pass')
parser.add_argument('--auth-uri',
                    help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                    action='store',
                    default=None,
                    dest='auth_uri')
parser.add_argument('--auth-url',
                    help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                    action='store',
                    default=None,
                    dest='auth_url')
parser.add_argument('--nova-pass',
                    help='passowrd for nova user',
                    action='store',
                    default=None,
                    dest='nova_pass')
parser.add_argument('--novncproxy-base-url',
                    help='nova vnc proxy base url e.g. http://CONTROLLER_VIP:6080/vnc_auto.html',
                    action='store',
                    default=None,
                    dest='novncproxy_base_url')
parser.add_argument('--glance-host',
                    help='glance host e.g. CONTROLLER_VIP',
                    action='store',
                    default=None,
                    dest='glance_host')
parser.add_argument('--neutron-endpoint',
                    help='neutron endpoint e.g. http://CONTROLLER_VIP:9696',
                    action='store',
                    default=None,
                    dest='neutron_endpoint')
parser.add_argument('--neutron-pass',
                    help='the password for neutron user',
                    action='store',
                    default=None,
                    dest='neutron_pass')
parser.add_argument('--rbd-secret-uuid',
                    help='ceph rbd secret for nova libvirt',
                    action='store',
                    default=None,
                    dest='rbd_secret_uuid')

args = parser.parse_args()

conf_nova_conf = """[DEFAULT]
dhcpbridge_flagfile=/etc/nova/nova.conf
dhcpbridge=/usr/bin/nova-dhcpbridge
logdir=/var/log/nova
state_path=/var/lib/nova
lock_path=/var/lock/nova
force_dhcp_release=True
libvirt_use_virtio_for_bridges=True
verbose=True
ec2_private_dns_show_ip=True
api_paste_config=/etc/nova/api-paste.ini
enabled_apis=ec2,osapi_compute,metadata
rpc_backend = rabbit
auth_strategy = keystone
my_ip = {{ my_ip }}
network_api_class = nova.network.neutronv2.api.API
security_group_api = neutron
linuxnet_interface_driver = nova.network.linux_net.NeutronLinuxBridgeInterfaceDriver
firewall_driver = nova.virt.firewall.NoopFirewallDriver

[oslo_messaging_rabbit]
rabbit_hosts = {{ rabbit_hosts }}
rabbit_userid = openstack
rabbit_password = {{ rabbit_password }}

[keystone_authtoken]
auth_uri = {{ auth_uri }}
auth_url = {{ auth_url }}
auth_plugin = password
project_domain_id = default
user_domain_id = default
project_name = service
username = nova
password = {{ password }}

[vnc]
enabled = True
vncserver_listen = 0.0.0.0
vncserver_proxyclient_address = $my_ip
novncproxy_base_url = {{ novncproxy_base_url }}

[glance]
host = {{ host }}

[oslo_concurrency]
lock_path = /var/lib/nova/tmp

[neutron]
url = {{ url }}
auth_url = {{ auth_url }}
auth_plugin = password
project_domain_id = default
user_domain_id = default
region_name = RegionOne
project_name = service
username = neutron
password = {{ neutron_password }}
"""
conf_nova_compute_conf = """[DEFAULT]
compute_driver=libvirt.LibvirtDriver
[libvirt]
virt_type=kvm
images_type = rbd
images_rbd_pool = vms
images_rbd_ceph_conf = /etc/ceph/ceph.conf
rbd_user = cinder
rbd_secret_uuid = {{ rbd_secret_uuid }}
disk_cachemodes="network=writeback"
live_migration_flag="VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_LIVE,VIR_MIGRATE_PERSIST_DEST,VIR_MIGRATE_TUNNELLED"
"""

class NovaCompute(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(NovaCompute, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _install(self, my_ip, rabbit_hosts, rabbit_pass, auth_uri, auth_url, nova_pass, novncproxy_base_url, glance_host, neutron_endpoint, neutron_pass, rbd_secret_uuid):
        print red(env.host_string + ' | Install nova-compute sysfsutils')
        sudo('apt-get update')
        sudo('apt-get -y install nova-compute sysfsutils')

        print red(env.host_string + ' | Update /etc/nova/nova.conf')
        with open('tmp_nova_conf_' + env.host_string, 'w') as f:
            f.write(conf_nova_conf)

        files.upload_template(filename='tmp_nova_conf_'+env.host_string,
                              destination='/etc/nova/nova.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'my_ip': my_ip,
                                       'rabbit_hosts': rabbit_hosts,
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': nova_pass,
                                       'novncproxy_base_url': novncproxy_base_url,
                                       'host': glance_host,
                                       'url': neutron_endpoint,
                                       'neutron_password': neutron_pass})
        os.remove('tmp_nova_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/nova/nova-compute.conf')
        with open('tmp_nova_compute_conf_' + env.host_string, 'w') as f:
            f.write(conf_nova_compute_conf)

        files.upload_template(filename='tmp_nova_compute_conf_'+env.host_string,
                              destination='/etc/nova/nova-compute.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'rbd_secret_uuid': rbd_secret_uuid})

        os.remove('tmp_nova_compute_conf_' + env.host_string)

        print red(env.host_string + ' | Restart Compute service')
        sudo('service nova-compute restart')
        print red(env.host_string + ' |  Remove the SQLite database file')
        sudo('rm -f /var/lib/nova/nova.sqlite')




def main():
    try:
        target = NovaCompute(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')

    if args.install:
        execute(target._install,
                args.my_ip,
                args.rabbit_hosts,
                args.rabbit_pass,
                args.auth_uri,
                args.auth_url,
                args.nova_pass,
                args.novncproxy_base_url,
                args.glance_host,
                args.neutron_endpoint,
                args.neutron_pass,
                args.rbd_secret_uuid)
        

if __name__ == '__main__':
    main()