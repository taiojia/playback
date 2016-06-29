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
enabled_apis=osapi_compute,metadata
rpc_backend = rabbit
auth_strategy = keystone
my_ip = {{ my_ip }}
network_api_class = nova.network.neutronv2.api.API
security_group_api = neutron
linuxnet_interface_driver = nova.network.linux_net.NeutronLinuxBridgeInterfaceDriver
use_neutron = True
firewall_driver = nova.virt.firewall.NoopFirewallDriver

[oslo_messaging_rabbit]
rabbit_hosts = {{ rabbit_hosts }}
rabbit_userid = {{ rabbit_user }}
rabbit_password = {{ rabbit_password }}

[keystone_authtoken]
auth_uri = {{ auth_uri }}
auth_url = {{ auth_url }}
memcached_servers = {{ memcached_servers }}
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = {{ password }}

[vnc]
enabled = True
vncserver_listen = 0.0.0.0
vncserver_proxyclient_address = $my_ip
novncproxy_base_url = {{ novncproxy_base_url }}

[glance]
# host deprecacted in mitaka instead of api_servers
#host = {{ host }}
api_servers = {{ api_servers }}

[oslo_concurrency]
lock_path = /var/lib/nova/tmp

[neutron]
url = {{ url }}
auth_url = {{ auth_url }}
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = {{ neutron_password }}
"""
