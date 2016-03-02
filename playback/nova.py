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
group.add_argument('--create-nova-db', 
                    help='create the nova database', 
                    action='store_true', 
                    default=False, 
                    dest='create_nova_db')
parser.add_argument('--root-db-pass', 
                    help='the openstack database root passowrd',
                   action='store', 
                   default=None, 
                   dest='root_db_pass')
parser.add_argument('--nova-db-pass', 
                    help='nova db passowrd',
                    action='store', 
                    default=None, 
                    dest='nova_db_pass')
group.add_argument('--create-service-credentials',
                   help='create the nova service credentials',
                   action='store_true',
                   default=False,
                   dest='create_service_credentials')
parser.add_argument('--os-password',
                    help='the password for admin user',
                    action='store',
                    default=None,
                    dest='os_password')
parser.add_argument('--os-auth-url',
                    help='keystone endpoint url e.g. http://controller:35357/v3',
                    action='store',
                    default=None,
                    dest='os_auth_url')
parser.add_argument('--nova-pass',
                    help='passowrd for nova user',
                    action='store',
                    default=None,
                    dest='nova_pass')
parser.add_argument('--endpoint',
                    help='public, internal and admin endpoint for nova service e.g. http://CONTROLLER_VIP:8774/v2/%%\(tenant_id\)s',
                    action='store',
                    default=None,
                    dest='endpoint')
group.add_argument('--install',
                   help='install nova',
                   action='store_true',
                   default=False,
                   dest='install')
parser.add_argument('--connection',
                    help='mysql database connection string e.g. mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova',
                    action='store',
                    default=None,
                    dest='connection')
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
parser.add_argument('--my-ip',
                    help='the host management ip',
                    action='store',
                    default=None,
                    dest='my_ip')
parser.add_argument('--memcached-servers',
                    help='memcached servers e.g. controller1:11211,controller2:11211',
                    action='store',
                    default=None,
                    dest='memcached_servers')
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
parser.add_argument('--metadata-proxy-shared-secret',
                    help='metadata proxy shared secret',
                    action='store',
                    default=None,
                    dest='metadata_proxy_shared_secret')
parser.add_argument('--populate',
                    help='Populate the nova database',
                    action='store_true',
                    default=False,
                    dest='populate')
args = parser.parse_args()

conf_nova_conf = """
[DEFAULT]
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
enabled_apis=osapi_compute,metadata
memcached_servers = {{ memcached_servers }}

[database]
connection = {{ connection }}

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
vncserver_listen = $my_ip
vncserver_proxyclient_address = $my_ip

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
password = {{ neutron_pass }}

service_metadata_proxy = True
metadata_proxy_shared_secret = {{ metadata_proxy_shared_secret }}


[cinder]
os_region_name = RegionOne
"""


class Nova(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(Nova, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    @runs_once
    def _create_nova_db(self, root_db_pass, nova_db_pass):
        print red(env.host_string + ' | Create nova database')
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE nova;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, nova_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, nova_db_pass), shell=False)

    @runs_once
    def _create_service_credentials(self, os_password, os_auth_url, nova_pass, endpoint):
        with shell_env(OS_PROJECT_DOMAIN_ID='default',
                       OS_USER_DOMAIN_ID='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2'):
            print red(env.host_string + ' | Create the nova user')
            sudo('openstack user create --domain default --password {0} nova'.format(nova_pass))
            print red(env.host_string + ' | Add the admin role to the nova user and service project')
            sudo('openstack role add --project service --user nova admin')
            print red(env.host_string + ' | Create the nova service entity')
            sudo('openstack service create --name nova --description "OpenStack Compute" compute')
            print red(env.host_string + ' | Create the Compute service API endpoints')
            sudo('openstack endpoint create --region RegionOne compute public {0}'.format(endpoint))
            sudo('openstack endpoint create --region RegionOne compute internal {0}'.format(endpoint))
            sudo('openstack endpoint create --region RegionOne compute admin {0}'.format(endpoint))

    def _install_nova(self, connection, auth_uri, auth_url, nova_pass, my_ip, memcached_servers, rabbit_hosts, rabbit_pass, glance_host, neutron_endpoint, neutron_pass, metadata_proxy_shared_secret):
        print red(env.host_string + ' | Install nova-api nova-cert nova-conductor nova-consoleauth nova-novncproxy nova-scheduler python-novaclient')
        sudo('apt-get update')
        sudo('apt-get -y install nova-api nova-cert nova-conductor nova-consoleauth nova-novncproxy nova-scheduler python-novaclient')

        print red(env.host_string + ' | Update configuration for /etc/nova/nova.conf')
        with open("tmp_nova_conf_" + env.host_string, "w") as f:
            f.write(conf_nova_conf)

        files.upload_template(filename='tmp_nova_conf_'+env.host_string,
                              destination='/etc/nova/nova.conf',
                              context={'connection': connection,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': nova_pass,
                                       'my_ip': my_ip,
                                       'memcached_servers': memcached_servers,
                                       'rabbit_hosts': rabbit_hosts,
                                       'rabbit_password': rabbit_pass,
                                       'host': glance_host,
                                       'url': neutron_endpoint,
                                       'neutron_pass': neutron_pass,
                                       'metadata_proxy_shared_secret': metadata_proxy_shared_secret
                                       },
                              use_jinja=True,
                              use_sudo=True)
        os.remove('tmp_nova_conf_' + env.host_string)

        if args.populate and env.host_string == self.hosts[0]:
            print red(env.host_string + ' | Populate the Nova database:')
            sudo('su -s /bin/sh -c "nova-manage db sync" nova', shell=False)

        print red(env.host_string + ' | Restart the Nova services')
        sudo('service nova-api restart')
        sudo('service nova-cert restart')
        sudo('service nova-consoleauth restart')
        sudo('service nova-scheduler restart')
        sudo('service nova-conductor restart')
        sudo('service nova-novncproxy restart')
         
        print red(env.host_string + ' | Remove the SQLite database file')
        sudo('rm -f /var/lib/nova/nova.sqlite')

def main():
    target = Nova(user=args.user, hosts=args.hosts.split(','))
    if args.create_nova_db:
        execute(target._create_nova_db, 
                args.root_db_pass, 
                args.nova_db_pass)
    if args.create_service_credentials:
        execute(target._create_service_credentials, 
                args.os_password, 
                args.os_auth_url, 
                args.nova_pass, 
                args.endpoint,)
    if args.install:
        execute(target._install_nova,
                args.connection,
                args.auth_uri,
                args.auth_url,
                args.nova_pass,
                args.my_ip,
                args.memcached_servers,
                args.rabbit_hosts,
                args.rabbit_pass,
                args.glance_host,
                args.neutron_endpoint,
                args.neutron_pass,
                args.metadata_proxy_shared_secret)
    
    disconnect_all()

if __name__ == '__main__':
    main()