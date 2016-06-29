conf_cinder_conf = """[DEFAULT]
rootwrap_config = /etc/cinder/rootwrap.conf
api_paste_confg = /etc/cinder/api-paste.ini
iscsi_helper = tgtadm
volume_name_template = volume-%s
volume_group = cinder-volumes
verbose = True
state_path = /var/lib/cinder
lock_path = /var/lock/cinder
volumes_dir = /var/lib/cinder/volumes
rpc_backend = rabbit
auth_strategy = keystone
my_ip = {{ my_ip }}
glance_api_servers = {{ glance_api_servers }}
enabled_backends = ceph

[ceph]
rbd_ceph_conf = /etc/ceph/ceph.conf
rados_connect_timeout = -1
glance_api_version = 2
rbd_max_clone_depth = 5
rbd_flatten_volume_from_snapshot = False
rbd_secret_uuid = {{ rbd_secret_uuid }}
rbd_user = cinder
rbd_pool = volumes
volume_driver = cinder.volume.drivers.rbd.RBDDriver
volume_backend_name = ceph
report_discard_supported = true

[database]
connection = {{ connection }}

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
username = cinder
password = {{ cinder_pass }}

[oslo_concurrency]
lock_path = /var/lib/cinder/tmp
"""
