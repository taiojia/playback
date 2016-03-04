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
group.add_argument('--create-neutron-db', 
                    help='create the neutron database', 
                    action='store_true', 
                    default=False, 
                    dest='create_neutron_db')
parser.add_argument('--root-db-pass', 
                    help='the openstack database root passowrd',
                   action='store', 
                   default=None, 
                   dest='root_db_pass')
parser.add_argument('--neutron-db-pass', 
                    help='neutron db passowrd',
                    action='store', 
                    default=None, 
                    dest='neutron_db_pass')
group.add_argument('--create-service-credentials',
                   help='create the neutron service credentials',
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
parser.add_argument('--endpoint',
                    help='public, internal and admin endpoint for neutron service e.g. http://CONTROLLER_VIP:8774/v2/%%\(tenant_id\)s',
                    action='store',
                    default=None,
                    dest='endpoint')
group.add_argument('--install',
                   help='install neutron for self-service',
                   action='store_true',
                   default=False,
                   dest='install')
parser.add_argument('--connection',
                    help='mysql database connection string e.g. mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron',
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
parser.add_argument('--neutron-pass',
                    help='the password for neutron user',
                    action='store',
                    default=None,
                    dest='neutron_pass')
parser.add_argument('--nova-url',
                    help='URL for connection to nova (Only supports one nova region currently)',
                    action='store',
                    default=None,
                    dest='nova_url')
parser.add_argument('--nova-pass',
                    help='passowrd for nova user',
                    action='store',
                    default=None,
                    dest='nova_pass')
parser.add_argument('--public-interface',
                    help='public interface e.g. eth1',
                    action='store',
                    default=None,
                    dest='public_interface')
parser.add_argument('--local-ip',
                    help=' underlying physical network interface that handles overlay networks(uses the management interface IP)',
                    action='store',
                    default=None,
                    dest='local_ip')
parser.add_argument('--nova-metadata-ip',
                    help='IP address used by Nova metadata server e.g. CONTROLLER_VIP',
                    action='store',
                    default=None,
                    dest='nova_metadata_ip')
parser.add_argument('--metadata-proxy-shared-secret',
                    help='metadata proxy shared secret',
                    action='store',
                    default=None,
                    dest='metadata_proxy_shared_secret')
parser.add_argument('--populate',
                    help='Populate the neutron database',
                    action='store_true',
                    default=False,
                    dest='populate')

args = parser.parse_args()

conf_neutron_conf = """[DEFAULT]
# Print more verbose output (set logging level to INFO instead of default WARNING level).
verbose = True

# =========Start Global Config Option for Distributed L3 Router===============
# Setting the "router_distributed" flag to "True" will default to the creation
# of distributed tenant routers. The admin can override this flag by specifying
# the type of the router on the create request (admin-only attribute). Default
# value is "False" to support legacy mode (centralized) routers.
#
# router_distributed = False
#
# ===========End Global Config Option for Distributed L3 Router===============

# Print debugging output (set logging level to DEBUG instead of default WARNING level).
# debug = False

# Where to store Neutron state files.  This directory must be writable by the
# user executing the agent.
# state_path = /var/lib/neutron

# log_format = %(asctime)s %(levelname)8s [%(name)s] %(message)s
# log_date_format = %Y-%m-%d %H:%M:%S

# use_syslog                           -> syslog
# log_file and log_dir                 -> log_dir/log_file
# (not log_file) and log_dir           -> log_dir/{binary_name}.log
# use_stderr                           -> stderr
# (not user_stderr) and (not log_file) -> stdout
# publish_errors                       -> notification system

# use_syslog = False
# syslog_log_facility = LOG_USER

# use_stderr = True
# log_file =
# log_dir =

# publish_errors = False

# Address to bind the API server to
# bind_host = 0.0.0.0

# Port the bind the API server to
# bind_port = 9696

# Path to the extensions.  Note that this can be a colon-separated list of
# paths.  For example:
# api_extensions_path = extensions:/path/to/more/extensions:/even/more/extensions
# The __path__ of neutron.extensions is appended to this, so if your
# extensions are in there you don't need to specify them here
# api_extensions_path =

# (StrOpt) Neutron core plugin entrypoint to be loaded from the
# neutron.core_plugins namespace. See setup.cfg for the entrypoint names of the
# plugins included in the neutron source distribution. For compatibility with
# previous versions, the class name of a plugin can be specified instead of its
# entrypoint name.
#
core_plugin = ml2
# Example: core_plugin = ml2

# (StrOpt) Neutron IPAM (IP address management) driver to be loaded from the
# neutron.ipam_drivers namespace. See setup.cfg for the entry point names.
# If ipam_driver is not set (default behavior), no ipam driver is used.
# Example: ipam_driver =
# In order to use the reference implementation of neutron ipam driver, use
# 'internal'.
# Example: ipam_driver = internal

# (ListOpt) List of service plugin entrypoints to be loaded from the
# neutron.service_plugins namespace. See setup.cfg for the entrypoint names of
# the plugins included in the neutron source distribution. For compatibility
# with previous versions, the class name of a plugin can be specified instead
# of its entrypoint name.
#
service_plugins = router
# Example: service_plugins = router,firewall,lbaas,vpnaas,metering,qos

# Paste configuration file
# api_paste_config = api-paste.ini

# (StrOpt) Hostname to be used by the neutron server, agents and services
# running on this machine. All the agents and services running on this machine
# must use the same host value.
# The default value is hostname of the machine.
#
# host =

# The strategy to be used for auth.
# Supported values are 'keystone'(default), 'noauth'.
auth_strategy = keystone

# Base MAC address. The first 3 octets will remain unchanged. If the
# 4h octet is not 00, it will also be used. The others will be
# randomly generated.
# 3 octet
# base_mac = fa:16:3e:00:00:00
# 4 octet
# base_mac = fa:16:3e:4f:00:00

# DVR Base MAC address. The first 3 octets will remain unchanged. If the
# 4th octet is not 00, it will also be used.  The others will be randomly
# generated. The 'dvr_base_mac' *must* be different from 'base_mac' to
# avoid mixing them up with MAC's allocated for tenant ports.
# A 4 octet example would be dvr_base_mac = fa:16:3f:4f:00:00
# The default is 3 octet
# dvr_base_mac = fa:16:3f:00:00:00

# Maximum amount of retries to generate a unique MAC address
# mac_generation_retries = 16

# DHCP Lease duration (in seconds).  Use -1 to
# tell dnsmasq to use infinite lease times.
# dhcp_lease_duration = 86400

# Domain to use for building the hostnames
# dns_domain = openstacklocal

# Allow sending resource operation notification to DHCP agent
# dhcp_agent_notification = True

# Enable or disable bulk create/update/delete operations
# allow_bulk = True
# Enable or disable pagination
# allow_pagination = False
# Enable or disable sorting
# allow_sorting = False
# Enable or disable overlapping IPs for subnets
# Attention: the following parameter MUST be set to False if Neutron is
# being used in conjunction with nova security groups
allow_overlapping_ips = True
# Ensure that configured gateway is on subnet. For IPv6, validate only if
# gateway is not a link local address. Deprecated, to be removed during the
# K release, at which point the check will be mandatory.
# force_gateway_on_subnet = True

# Default maximum number of items returned in a single response,
# value == infinite and value < 0 means no max limit, and value must
# be greater than 0. If the number of items requested is greater than
# pagination_max_limit, server will just return pagination_max_limit
# of number of items.
# pagination_max_limit = -1

# Maximum number of DNS nameservers per subnet
# max_dns_nameservers = 5

# Maximum number of host routes per subnet
# max_subnet_host_routes = 20

# Maximum number of fixed ips per port
# max_fixed_ips_per_port = 5

# Maximum number of routes per router
# max_routes = 30

# Default Subnet Pool to be used for IPv4 subnet-allocation.
# Specifies by UUID the pool to be used in case of subnet-create being called
# without a subnet-pool ID.  The default of None means that no pool will be
# used unless passed explicitly to subnet create.  If no pool is used, then a
# CIDR must be passed to create a subnet and that subnet will not be allocated
# from any pool; it will be considered part of the tenant's private address
# space.
# default_ipv4_subnet_pool =

# Default Subnet Pool to be used for IPv6 subnet-allocation.
# Specifies by UUID the pool to be used in case of subnet-create being
# called without a subnet-pool ID.  Set to "prefix_delegation"
# to enable IPv6 Prefix Delegation in a PD-capable environment.
# See the description for default_ipv4_subnet_pool for more information.
# default_ipv6_subnet_pool =

# =========== items for MTU selection and advertisement =============
# Advertise MTU.  If True, effort is made to advertise MTU
# settings to VMs via network methods (ie. DHCP and RA MTU options)
# when the network's preferred MTU is known.
# advertise_mtu = False
# ======== end of items for MTU selection and advertisement =========

# =========== items for agent management extension =============
# Seconds to regard the agent as down; should be at least twice
# report_interval, to be sure the agent is down for good
# agent_down_time = 75

# Agent starts with admin_state_up=False when enable_new_agents=False.
# In the case, user's resources will not be scheduled automatically to the
# agent until admin changes admin_state_up to True.
# enable_new_agents = True
# ===========  end of items for agent management extension =====

# =========== items for agent scheduler extension =============
# Driver to use for scheduling network to DHCP agent
# network_scheduler_driver = neutron.scheduler.dhcp_agent_scheduler.WeightScheduler
# Driver to use for scheduling router to a default L3 agent
# router_scheduler_driver = neutron.scheduler.l3_agent_scheduler.LeastRoutersScheduler
# Driver to use for scheduling a loadbalancer pool to an lbaas agent
# loadbalancer_pool_scheduler_driver = neutron.services.loadbalancer.agent_scheduler.ChanceScheduler

# (StrOpt) Representing the resource type whose load is being reported by
# the agent.
# This can be 'networks','subnets' or 'ports'. When specified (Default is networks),
# the server will extract particular load sent as part of its agent configuration object
# from the agent report state, which is the number of resources being consumed, at
# every report_interval.
# dhcp_load_type can be used in combination with network_scheduler_driver =
# neutron.scheduler.dhcp_agent_scheduler.WeightScheduler
# When the network_scheduler_driver is WeightScheduler, dhcp_load_type can
# be configured to represent the choice for the resource being balanced.
# Example: dhcp_load_type = networks
# Values:
#   networks - number of networks hosted on the agent
#   subnets -  number of subnets associated with the networks hosted on the agent
#   ports   -  number of ports associated with the networks hosted on the agent
# dhcp_load_type = networks

# Allow auto scheduling networks to DHCP agent. It will schedule non-hosted
# networks to first DHCP agent which sends get_active_networks message to
# neutron server
# network_auto_schedule = True

# Allow auto scheduling routers to L3 agent. It will schedule non-hosted
# routers to first L3 agent which sends sync_routers message to neutron server
# router_auto_schedule = True

# Allow automatic rescheduling of routers from dead L3 agents with
# admin_state_up set to True to alive agents.
# allow_automatic_l3agent_failover = False

# Allow automatic removal of networks from dead DHCP agents with
# admin_state_up set to True.
# Networks could then be rescheduled if network_auto_schedule is True
# allow_automatic_dhcp_failover = True

# Number of DHCP agents scheduled to host a tenant network.
# If this number is greater than 1, the scheduler automatically
# assigns multiple DHCP agents for a given tenant network,
# providing high availability for DHCP service.
# dhcp_agents_per_network = 1

# Enable services on agents with admin_state_up False.
# If this option is False, when admin_state_up of an agent is turned to
# False, services on it will be disabled. If this option is True, services
# on agents with admin_state_up False keep available and manual scheduling
# to such agents is available. Agents with admin_state_up False are not
# selected for automatic scheduling regardless of this option.
# enable_services_on_agents_with_admin_state_down = False

# ===========  end of items for agent scheduler extension =====

# =========== items for l3 extension ==============
# Enable high availability for virtual routers.
# l3_ha = False
#
# Maximum number of l3 agents which a HA router will be scheduled on. If it
# is set to 0 the router will be scheduled on every agent.
# max_l3_agents_per_router = 3
#
# Minimum number of l3 agents which a HA router will be scheduled on. The
# default value is 2.
# min_l3_agents_per_router = 2
#
# CIDR of the administrative network if HA mode is enabled
# l3_ha_net_cidr = 169.254.192.0/18
#
# Enable snat by default on external gateway when available
# enable_snat_by_default = True
#
# The network type to use when creating the HA network for an HA router.
# By default or if empty, the first 'tenant_network_types'
# is used. This is helpful when the VRRP traffic should use a specific
# network which not the default one.
# ha_network_type =
# Example: ha_network_type = flat
#
# The physical network name with which the HA network can be created.
# ha_network_physical_name =
# Example: ha_network_physical_name = physnet1
# =========== end of items for l3 extension =======

# =========== items for metadata proxy configuration ==============
# User (uid or name) running metadata proxy after its initialization
# (if empty: agent effective user)
# metadata_proxy_user =

# Group (gid or name) running metadata proxy after its initialization
# (if empty: agent effective group)
# metadata_proxy_group =

# Enable/Disable log watch by metadata proxy, it should be disabled when
# metadata_proxy_user/group is not allowed to read/write its log file and
# 'copytruncate' logrotate option must be used if logrotate is enabled on
# metadata proxy log files. Option default value is deduced from
# metadata_proxy_user: watch log is enabled if metadata_proxy_user is agent
# effective user id/name.
# metadata_proxy_watch_log =

# Location of Metadata Proxy UNIX domain socket
# metadata_proxy_socket = $state_path/metadata_proxy
# =========== end of items for metadata proxy configuration ==============

# ========== items for VLAN trunking networks ==========
# Setting this flag to True will allow plugins that support it to
# create VLAN transparent networks. This flag has no effect for
# plugins that do not support VLAN transparent networks.
# vlan_transparent = False
# ========== end of items for VLAN trunking networks ==========

# =========== WSGI parameters related to the API server ==============
# Number of separate API worker processes to spawn. If not specified or < 1,
# the default value is equal to the number of CPUs available.
# api_workers = <number of CPUs>

# Number of separate RPC worker processes to spawn. If not specified or < 1,
# a single RPC worker process is spawned by the parent process.
# rpc_workers = 1

# Timeout for client connections socket operations. If an
# incoming connection is idle for this number of seconds it
# will be closed. A value of '0' means wait forever. (integer
# value)
# client_socket_timeout = 900

# wsgi keepalive option. Determines if connections are allowed to be held open
# by clients after a request is fulfilled. A value of False will ensure that
# the socket connection will be explicitly closed once a response has been
# sent to the client.
# wsgi_keep_alive = True

# Sets the value of TCP_KEEPIDLE in seconds to use for each server socket when
# starting API server. Not supported on OS X.
# tcp_keepidle = 600

# Number of seconds to keep retrying to listen
# retry_until_window = 30

# Number of backlog requests to configure the socket with.
# backlog = 4096

# Max header line to accommodate large tokens
# max_header_line = 16384

# Enable SSL on the API server
# use_ssl = False

# Certificate file to use when starting API server securely
# ssl_cert_file = /path/to/certfile

# Private key file to use when starting API server securely
# ssl_key_file = /path/to/keyfile

# CA certificate file to use when starting API server securely to
# verify connecting clients. This is an optional parameter only required if
# API clients need to authenticate to the API server using SSL certificates
# signed by a trusted CA
# ssl_ca_file = /path/to/cafile
# ======== end of WSGI parameters related to the API server ==========

# ======== neutron nova interactions ==========
# Send notification to nova when port status is active.
notify_nova_on_port_status_changes = True

# Send notifications to nova when port data (fixed_ips/floatingips) change
# so nova can update it's cache.
notify_nova_on_port_data_changes = True

# URL for connection to nova (Only supports one nova region currently).
nova_url = {{ nova_url }}

# Name of nova region to use. Useful if keystone manages more than one region
# nova_region_name =

# Username for connection to nova in admin context
# nova_admin_username =

# The uuid of the admin nova tenant
# nova_admin_tenant_id =

# The name of the admin nova tenant. If the uuid of the admin nova tenant
# is set, this is optional.  Useful for cases where the uuid of the admin
# nova tenant is not available when configuration is being done.
# nova_admin_tenant_name =

# Password for connection to nova in admin context.
# nova_admin_password =

# Authorization URL for connection to nova in admin context.
# nova_admin_auth_url =

# CA file for novaclient to verify server certificates
# nova_ca_certificates_file =

# Boolean to control ignoring SSL errors on the nova url
# nova_api_insecure = False

# Number of seconds between sending events to nova if there are any events to send
# send_events_interval = 2

# ======== end of neutron nova interactions ==========

#
# Options defined in oslo.messaging
#

# Use durable queues in amqp. (boolean value)
# Deprecated group/name - [DEFAULT]/rabbit_durable_queues
# amqp_durable_queues=false

# Auto-delete queues in amqp. (boolean value)
# amqp_auto_delete=false

# Size of RPC connection pool. (integer value)
# rpc_conn_pool_size=30

# Qpid broker hostname. (string value)
# qpid_hostname=localhost

# Qpid broker port. (integer value)
# qpid_port=5672

# Qpid HA cluster host:port pairs. (list value)
# qpid_hosts=$qpid_hostname:$qpid_port

# Username for Qpid connection. (string value)
# qpid_username=

# Password for Qpid connection. (string value)
# qpid_password=

# Space separated list of SASL mechanisms to use for auth.
# (string value)
# qpid_sasl_mechanisms=

# Seconds between connection keepalive heartbeats. (integer
# value)
# qpid_heartbeat=60

# Transport to use, either 'tcp' or 'ssl'. (string value)
# qpid_protocol=tcp

# Whether to disable the Nagle algorithm. (boolean value)
# qpid_tcp_nodelay=true

# The qpid topology version to use.  Version 1 is what was
# originally used by impl_qpid.  Version 2 includes some
# backwards-incompatible changes that allow broker federation
# to work.  Users should update to version 2 when they are
# able to take everything down, as it requires a clean break.
# (integer value)
# qpid_topology_version=1

# SSL version to use (valid only if SSL enabled). valid values
# are TLSv1, SSLv23 and SSLv3. SSLv2 may be available on some
# distributions. (string value)
# kombu_ssl_version=

# SSL key file (valid only if SSL enabled). (string value)
# kombu_ssl_keyfile=

# SSL cert file (valid only if SSL enabled). (string value)
# kombu_ssl_certfile=

# SSL certification authority file (valid only if SSL
# enabled). (string value)
# kombu_ssl_ca_certs=

# How long to wait before reconnecting in response to an AMQP
# consumer cancel notification. (floating point value)
# kombu_reconnect_delay=1.0

# The RabbitMQ broker address where a single node is used.
# (string value)
# rabbit_host=localhost

# The RabbitMQ broker port where a single node is used.
# (integer value)
# rabbit_port=5672

# RabbitMQ HA cluster host:port pairs. (list value)
# rabbit_hosts=$rabbit_host:$rabbit_port

# Connect over SSL for RabbitMQ. (boolean value)
# rabbit_use_ssl=false

# The RabbitMQ userid. (string value)
# rabbit_userid=guest

# The RabbitMQ password. (string value)
# rabbit_password=guest

# the RabbitMQ login method (string value)
# rabbit_login_method=AMQPLAIN

# The RabbitMQ virtual host. (string value)
# rabbit_virtual_host=/

# How frequently to retry connecting with RabbitMQ. (integer
# value)
# rabbit_retry_interval=1

# How long to backoff for between retries when connecting to
# RabbitMQ. (integer value)
# rabbit_retry_backoff=2

# Maximum number of RabbitMQ connection retries. Default is 0
# (infinite retry count). (integer value)
# rabbit_max_retries=0

# Use HA queues in RabbitMQ (x-ha-policy: all). If you change
# this option, you must wipe the RabbitMQ database. (boolean
# value)
# rabbit_ha_queues=false

# If passed, use a fake RabbitMQ provider. (boolean value)
# fake_rabbit=false

# ZeroMQ bind address. Should be a wildcard (*), an ethernet
# interface, or IP. The "host" option should point or resolve
# to this address. (string value)
# rpc_zmq_bind_address=*

# MatchMaker driver. (string value)
# rpc_zmq_matchmaker=oslo.messaging._drivers.matchmaker.MatchMakerLocalhost

# ZeroMQ receiver listening port. (integer value)
# rpc_zmq_port=9501

# Number of ZeroMQ contexts, defaults to 1. (integer value)
# rpc_zmq_contexts=1

# Maximum number of ingress messages to locally buffer per
# topic. Default is unlimited. (integer value)
# rpc_zmq_topic_backlog=

# Directory for holding IPC sockets. (string value)
# rpc_zmq_ipc_dir=/var/run/openstack

# Name of this node. Must be a valid hostname, FQDN, or IP
# address. Must match "host" option, if running Nova. (string
# value)
# rpc_zmq_host=oslo

# Seconds to wait before a cast expires (TTL). Only supported
# by impl_zmq. (integer value)
# rpc_cast_timeout=30

# Heartbeat frequency. (integer value)
# matchmaker_heartbeat_freq=300

# Heartbeat time-to-live. (integer value)
# matchmaker_heartbeat_ttl=600

# Size of RPC greenthread pool. (integer value)
# rpc_thread_pool_size=64

# Driver or drivers to handle sending notifications. (multi
# valued)
# notification_driver=

# AMQP topic used for OpenStack notifications. (list value)
# Deprecated group/name - [rpc_notifier2]/topics
# notification_topics=notifications

# Seconds to wait for a response from a call. (integer value)
# rpc_response_timeout=60

# A URL representing the messaging driver to use and its full
# configuration. If not set, we fall back to the rpc_backend
# option and driver specific configuration. (string value)
# transport_url=

# The messaging driver to use, defaults to rabbit. Other
# drivers include qpid and zmq. (string value)
rpc_backend=rabbit

# The default exchange under which topics are scoped. May be
# overridden by an exchange name specified in the
# transport_url option. (string value)
# control_exchange=openstack


[matchmaker_redis]

#
# Options defined in oslo.messaging
#

# Host to locate redis. (string value)
# host=127.0.0.1

# Use this port to connect to redis host. (integer value)
# port=6379

# Password for Redis server (optional). (string value)
# password=


[matchmaker_ring]

#
# Options defined in oslo.messaging
#

# Matchmaker ring file (JSON). (string value)
# Deprecated group/name - [DEFAULT]/matchmaker_ringfile
# ringfile=/etc/oslo/matchmaker_ring.json

[quotas]
# Default driver to use for quota checks
# quota_driver = neutron.db.quota.driver.DbQuotaDriver

# Resource name(s) that are supported in quota features
# This option is deprecated for removal in the M release, please refrain from using it
# quota_items = network,subnet,port

# Default number of resource allowed per tenant. A negative value means
# unlimited.
# default_quota = -1

# Number of networks allowed per tenant. A negative value means unlimited.
# quota_network = 10

# Number of subnets allowed per tenant. A negative value means unlimited.
# quota_subnet = 10

# Number of ports allowed per tenant. A negative value means unlimited.
# quota_port = 50

# Number of security groups allowed per tenant. A negative value means
# unlimited.
# quota_security_group = 10

# Number of security group rules allowed per tenant. A negative value means
# unlimited.
# quota_security_group_rule = 100

# Number of vips allowed per tenant. A negative value means unlimited.
# quota_vip = 10

# Number of pools allowed per tenant. A negative value means unlimited.
# quota_pool = 10

# Number of pool members allowed per tenant. A negative value means unlimited.
# The default is unlimited because a member is not a real resource consumer
# on Openstack. However, on back-end, a member is a resource consumer
# and that is the reason why quota is possible.
# quota_member = -1

# Number of health monitors allowed per tenant. A negative value means
# unlimited.
# The default is unlimited because a health monitor is not a real resource
# consumer on Openstack. However, on back-end, a member is a resource consumer
# and that is the reason why quota is possible.
# quota_health_monitor = -1

# Number of loadbalancers allowed per tenant. A negative value means unlimited.
# quota_loadbalancer = 10

# Number of listeners allowed per tenant. A negative value means unlimited.
# quota_listener = -1

# Number of v2 health monitors allowed per tenant. A negative value means
# unlimited. These health monitors exist under the lbaas v2 API
# quota_healthmonitor = -1

# Number of routers allowed per tenant. A negative value means unlimited.
# quota_router = 10

# Number of floating IPs allowed per tenant. A negative value means unlimited.
# quota_floatingip = 50

# Number of firewalls allowed per tenant. A negative value means unlimited.
# quota_firewall = 1

# Number of firewall policies allowed per tenant. A negative value means
# unlimited.
# quota_firewall_policy = 1

# Number of firewall rules allowed per tenant. A negative value means
# unlimited.
# quota_firewall_rule = 100

# Default number of RBAC entries allowed per tenant. A negative value means
# unlimited.
# quota_rbac_policy = 10

[agent]
# Use "sudo neutron-rootwrap /etc/neutron/rootwrap.conf" to use the real
# root filter facility.
# Change to "sudo" to skip the filtering and just run the command directly
root_helper = sudo /usr/bin/neutron-rootwrap /etc/neutron/rootwrap.conf

# Set to true to add comments to generated iptables rules that describe
# each rule's purpose. (System must support the iptables comments module.)
# comment_iptables_rules = True

# Root helper daemon application to use when possible.
# root_helper_daemon =

# Use the root helper when listing the namespaces on a system. This may not
# be required depending on the security configuration. If the root helper is
# not required, set this to False for a performance improvement.
# use_helper_for_ns_read = True

# The interval to check external processes for failure in seconds (0=disabled)
# check_child_processes_interval = 60

# Action to take when an external process spawned by an agent dies
# Values:
#   respawn - Respawns the external process
#   exit - Exits the agent
# check_child_processes_action = respawn

# =========== items for agent management extension =============
# seconds between nodes reporting state to server; should be less than
# agent_down_time, best if it is half or less than agent_down_time
# report_interval = 30

# ===========  end of items for agent management extension =====

[keystone_authtoken]
auth_uri = {{ auth_uri }}
auth_url = {{ auth_url }}
auth_plugin = password
project_domain_id = default
user_domain_id = default
project_name = service
username = neutron
password = {{ neutron_password }}

[database]
# This line MUST be changed to actually run the plugin.
# Example:
# connection = mysql+pymysql://root:pass@127.0.0.1:3306/neutron
# Replace 127.0.0.1 above with the IP address of the database used by the
# main neutron server. (Leave it as is if the database runs on this host.)
# connection = sqlite://
# NOTE: In deployment the [database] section and its connection attribute may
# be set in the corresponding core plugin '.ini' file. However, it is suggested
# to put the [database] section and its connection attribute in this
# configuration file.
connection = {{ connection }}

# Database engine for which script will be generated when using offline
# migration
# engine =

# The SQLAlchemy connection string used to connect to the slave database
# slave_connection =

# Database reconnection retry times - in event connectivity is lost
# set to -1 implies an infinite retry count
# max_retries = 10

# Database reconnection interval in seconds - if the initial connection to the
# database fails
# retry_interval = 10

# Minimum number of SQL connections to keep open in a pool
# min_pool_size = 1

# Maximum number of SQL connections to keep open in a pool
# max_pool_size = 10

# Timeout in seconds before idle sql connections are reaped
# idle_timeout = 3600

# If set, use this value for max_overflow with sqlalchemy
# max_overflow = 20

# Verbosity of SQL debugging information. 0=None, 100=Everything
# connection_debug = 0

# Add python stack traces to SQL as comment strings
# connection_trace = False

# If set, use this value for pool_timeout with sqlalchemy
# pool_timeout = 10

[nova]
auth_url = {{auth_url}}
auth_plugin = password
project_domain_id = default
user_domain_id = default
region_name = RegionOne
project_name = service
username = nova
password = {{ password }}
# Name of the plugin to load
# auth_plugin =

# Config Section from which to load plugin specific options
# auth_section =

# PEM encoded Certificate Authority to use when verifying HTTPs connections.
# cafile =

# PEM encoded client certificate cert file
# certfile =

# Verify HTTPS connections.
# insecure = False

# PEM encoded client certificate key file
# keyfile =

# Name of nova region to use. Useful if keystone manages more than one region.
# region_name =

# Timeout value for http requests
# timeout =

[oslo_concurrency]

# Directory to use for lock files. For security, the specified directory should
# only be writable by the user running the processes that need locking.
# Defaults to environment variable OSLO_LOCK_PATH. If external locks are used,
# a lock path must be set.
lock_path = $state_path/lock

# Enables or disables inter-process locks.
# disable_process_locking = False

[oslo_policy]

# The JSON file that defines policies.
# policy_file = policy.json

# Default rule. Enforced when a requested rule is not found.
# policy_default_rule = default

# Directories where policy configuration files are stored.
# They can be relative to any directory in the search path defined by the
# config_dir option, or absolute paths. The file defined by policy_file
# must exist for these directories to be searched. Missing or empty
# directories are ignored.
# policy_dirs = policy.d

[oslo_messaging_amqp]

#
# From oslo.messaging
#

# Address prefix used when sending to a specific server (string value)
# Deprecated group/name - [amqp1]/server_request_prefix
# server_request_prefix = exclusive

# Address prefix used when broadcasting to all servers (string value)
# Deprecated group/name - [amqp1]/broadcast_prefix
# broadcast_prefix = broadcast

# Address prefix when sending to any server in group (string value)
# Deprecated group/name - [amqp1]/group_request_prefix
# group_request_prefix = unicast

# Name for the AMQP container (string value)
# Deprecated group/name - [amqp1]/container_name
# container_name =

# Timeout for inactive connections (in seconds) (integer value)
# Deprecated group/name - [amqp1]/idle_timeout
# idle_timeout = 0

# Debug: dump AMQP frames to stdout (boolean value)
# Deprecated group/name - [amqp1]/trace
# trace = false

# CA certificate PEM file for verifing server certificate (string value)
# Deprecated group/name - [amqp1]/ssl_ca_file
# ssl_ca_file =

# Identifying certificate PEM file to present to clients (string value)
# Deprecated group/name - [amqp1]/ssl_cert_file
# ssl_cert_file =

# Private key PEM file used to sign cert_file certificate (string value)
# Deprecated group/name - [amqp1]/ssl_key_file
# ssl_key_file =

# Password for decrypting ssl_key_file (if encrypted) (string value)
# Deprecated group/name - [amqp1]/ssl_key_password
# ssl_key_password =

# Accept clients using either SSL or plain TCP (boolean value)
# Deprecated group/name - [amqp1]/allow_insecure_clients
# allow_insecure_clients = false


[oslo_messaging_qpid]

#
# From oslo.messaging
#

# Use durable queues in AMQP. (boolean value)
# Deprecated group/name - [DEFAULT]/rabbit_durable_queues
# amqp_durable_queues = false

# Auto-delete queues in AMQP. (boolean value)
# Deprecated group/name - [DEFAULT]/amqp_auto_delete
# amqp_auto_delete = false

# Size of RPC connection pool. (integer value)
# Deprecated group/name - [DEFAULT]/rpc_conn_pool_size
# rpc_conn_pool_size = 30

# Qpid broker hostname. (string value)
# Deprecated group/name - [DEFAULT]/qpid_hostname
# qpid_hostname = localhost

# Qpid broker port. (integer value)
# Deprecated group/name - [DEFAULT]/qpid_port
# qpid_port = 5672

# Qpid HA cluster host:port pairs. (list value)
# Deprecated group/name - [DEFAULT]/qpid_hosts
# qpid_hosts = $qpid_hostname:$qpid_port

# Username for Qpid connection. (string value)
# Deprecated group/name - [DEFAULT]/qpid_username
# qpid_username =

# Password for Qpid connection. (string value)
# Deprecated group/name - [DEFAULT]/qpid_password
# qpid_password =

# Space separated list of SASL mechanisms to use for auth. (string value)
# Deprecated group/name - [DEFAULT]/qpid_sasl_mechanisms
# qpid_sasl_mechanisms =

# Seconds between connection keepalive heartbeats. (integer value)
# Deprecated group/name - [DEFAULT]/qpid_heartbeat
# qpid_heartbeat = 60

# Transport to use, either 'tcp' or 'ssl'. (string value)
# Deprecated group/name - [DEFAULT]/qpid_protocol
# qpid_protocol = tcp

# Whether to disable the Nagle algorithm. (boolean value)
# Deprecated group/name - [DEFAULT]/qpid_tcp_nodelay
# qpid_tcp_nodelay = true

# The number of prefetched messages held by receiver. (integer value)
# Deprecated group/name - [DEFAULT]/qpid_receiver_capacity
# qpid_receiver_capacity = 1

# The qpid topology version to use.  Version 1 is what was originally used by
# impl_qpid.  Version 2 includes some backwards-incompatible changes that allow
# broker federation to work.  Users should update to version 2 when they are
# able to take everything down, as it requires a clean break. (integer value)
# Deprecated group/name - [DEFAULT]/qpid_topology_version
# qpid_topology_version = 1


[oslo_messaging_rabbit]

#
# From oslo.messaging
#

# Use durable queues in AMQP. (boolean value)
# Deprecated group/name - [DEFAULT]/rabbit_durable_queues
# amqp_durable_queues = false

# Auto-delete queues in AMQP. (boolean value)
# Deprecated group/name - [DEFAULT]/amqp_auto_delete
# amqp_auto_delete = false

# Size of RPC connection pool. (integer value)
# Deprecated group/name - [DEFAULT]/rpc_conn_pool_size
# rpc_conn_pool_size = 30

# SSL version to use (valid only if SSL enabled). Valid values are TLSv1 and
# SSLv23. SSLv2, SSLv3, TLSv1_1, and TLSv1_2 may be available on some
# distributions. (string value)
# Deprecated group/name - [DEFAULT]/kombu_ssl_version
# kombu_ssl_version =

# SSL key file (valid only if SSL enabled). (string value)
# Deprecated group/name - [DEFAULT]/kombu_ssl_keyfile
# kombu_ssl_keyfile =

# SSL cert file (valid only if SSL enabled). (string value)
# Deprecated group/name - [DEFAULT]/kombu_ssl_certfile
# kombu_ssl_certfile =

# SSL certification authority file (valid only if SSL enabled). (string value)
# Deprecated group/name - [DEFAULT]/kombu_ssl_ca_certs
# kombu_ssl_ca_certs =

# How long to wait before reconnecting in response to an AMQP consumer cancel
# notification. (floating point value)
# Deprecated group/name - [DEFAULT]/kombu_reconnect_delay
# kombu_reconnect_delay = 1.0

# The RabbitMQ broker address where a single node is used. (string value)
# Deprecated group/name - [DEFAULT]/rabbit_host
rabbit_hosts = {{rabbit_hosts}}

# The RabbitMQ broker port where a single node is used. (integer value)
# Deprecated group/name - [DEFAULT]/rabbit_port
# rabbit_port = 5672

# RabbitMQ HA cluster host:port pairs. (list value)
# Deprecated group/name - [DEFAULT]/rabbit_hosts
# rabbit_hosts = $rabbit_host:$rabbit_port

# Connect over SSL for RabbitMQ. (boolean value)
# Deprecated group/name - [DEFAULT]/rabbit_use_ssl
# rabbit_use_ssl = false

# The RabbitMQ userid. (string value)
# Deprecated group/name - [DEFAULT]/rabbit_userid
rabbit_userid = openstack

# The RabbitMQ password. (string value)
# Deprecated group/name - [DEFAULT]/rabbit_password
rabbit_password = {{ rabbit_password }}

# The RabbitMQ login method. (string value)
# Deprecated group/name - [DEFAULT]/rabbit_login_method
# rabbit_login_method = AMQPLAIN

# The RabbitMQ virtual host. (string value)
# Deprecated group/name - [DEFAULT]/rabbit_virtual_host
# rabbit_virtual_host = /

# How frequently to retry connecting with RabbitMQ. (integer value)
# rabbit_retry_interval = 1

# How long to backoff for between retries when connecting to RabbitMQ. (integer
# value)
# Deprecated group/name - [DEFAULT]/rabbit_retry_backoff
# rabbit_retry_backoff = 2

# Maximum number of RabbitMQ connection retries. Default is 0 (infinite retry
# count). (integer value)
# Deprecated group/name - [DEFAULT]/rabbit_max_retries
# rabbit_max_retries = 0

# Use HA queues in RabbitMQ (x-ha-policy: all). If you change this option, you
# must wipe the RabbitMQ database. (boolean value)
# Deprecated group/name - [DEFAULT]/rabbit_ha_queues
# rabbit_ha_queues = false

# Deprecated, use rpc_backend=kombu+memory or rpc_backend=fake (boolean value)
# Deprecated group/name - [DEFAULT]/fake_rabbit
# fake_rabbit = false

[qos]
# Drivers list to use to send the update notification
# notification_drivers = message_queue
"""
conf_ml2_conf_ini = """[ml2]
# (ListOpt) List of network type driver entrypoints to be loaded from
# the neutron.ml2.type_drivers namespace.
#
type_drivers = local,flat,vlan,gre,vxlan,geneve
# Example: type_drivers = flat,vlan,gre,vxlan,geneve

# (ListOpt) Ordered list of network_types to allocate as tenant
# networks. The default value 'local' is useful for single-box testing
# but provides no connectivity between hosts.
#
tenant_network_types = vxlan
# Example: tenant_network_types = vlan,gre,vxlan,geneve


# (ListOpt) Ordered list of networking mechanism driver entrypoints
# to be loaded from the neutron.ml2.mechanism_drivers namespace.
mechanism_drivers = linuxbridge,l2population
# Example: mechanism_drivers = openvswitch,mlnx
# Example: mechanism_drivers = arista
# Example: mechanism_drivers = openvswitch,cisco_nexus,logger
# Example: mechanism_drivers = openvswitch,brocade
# Example: mechanism_drivers = linuxbridge,brocade

# (ListOpt) Ordered list of extension driver entrypoints
# to be loaded from the neutron.ml2.extension_drivers namespace.
extension_drivers = port_security
# Example: extension_drivers = anewextensiondriver

# =========== items for MTU selection and advertisement =============
# (IntOpt) Path MTU.  The maximum permissible size of an unfragmented
# packet travelling from and to addresses where encapsulated Neutron
# traffic is sent.  Drivers calculate maximum viable MTU for
# validating tenant requests based on this value (typically,
# path_mtu - max encap header size).  If <=0, the path MTU is
# indeterminate and no calculation takes place.
# path_mtu = 0

# (IntOpt) Segment MTU.  The maximum permissible size of an
# unfragmented packet travelling a L2 network segment.  If <=0,
# the segment MTU is indeterminate and no calculation takes place.
# segment_mtu = 0

# (ListOpt) Physical network MTUs.  List of mappings of physical
# network to MTU value.  The format of the mapping is
# <physnet>:<mtu val>.  This mapping allows specifying a
# physical network MTU value that differs from the default
# segment_mtu value.
# physical_network_mtus =
# Example: physical_network_mtus = physnet1:1550, physnet2:1500
# ======== end of items for MTU selection and advertisement =========

# (StrOpt) Default network type for external networks when no provider
# attributes are specified. By default it is None, which means that if
# provider attributes are not specified while creating external networks
# then they will have the same type as tenant networks.
# Allowed values for external_network_type config option depend on the
# network type values configured in type_drivers config option.
# external_network_type =
# Example: external_network_type = local

[ml2_type_flat]
# (ListOpt) List of physical_network names with which flat networks
# can be created. Use * to allow flat networks with arbitrary
# physical_network names.
#
flat_networks = public
# Example:flat_networks = physnet1,physnet2
# Example:flat_networks = *

[ml2_type_vlan]
# (ListOpt) List of <physical_network>[:<vlan_min>:<vlan_max>] tuples
# specifying physical_network names usable for VLAN provider and
# tenant networks, as well as ranges of VLAN tags on each
# physical_network available for allocation as tenant networks.
#
# network_vlan_ranges =
# Example: network_vlan_ranges = physnet1:1000:2999,physnet2

[ml2_type_gre]
# (ListOpt) Comma-separated list of <tun_min>:<tun_max> tuples enumerating ranges of GRE tunnel IDs that are available for tenant network allocation
# tunnel_id_ranges =

[ml2_type_vxlan]
# (ListOpt) Comma-separated list of <vni_min>:<vni_max> tuples enumerating
# ranges of VXLAN VNI IDs that are available for tenant network allocation.
#
vni_ranges = 1:1000

# (StrOpt) Multicast group for the VXLAN interface. When configured, will
# enable sending all broadcast traffic to this multicast group. When left
# unconfigured, will disable multicast VXLAN mode.
#
# vxlan_group =
# Example: vxlan_group = 239.1.1.1

[ml2_type_geneve]
# (ListOpt) Comma-separated list of <vni_min>:<vni_max> tuples enumerating
# ranges of Geneve VNI IDs that are available for tenant network allocation.
#
# vni_ranges =

# (IntOpt) Geneve encapsulation header size is dynamic, this
# value is used to calculate the maximum MTU for the driver.
# this is the sum of the sizes of the outer ETH+IP+UDP+GENEVE
# header sizes.
# The default size for this field is 50, which is the size of the
# Geneve header without any additional option headers
#
# max_header_size =
# Example: max_header_size = 50 (Geneve headers with no additional options)

[securitygroup]
# Controls if neutron security group is enabled or not.
# It should be false when you use nova security group.
# enable_security_group = True

# Use ipset to speed-up the iptables security groups. Enabling ipset support
# requires that ipset is installed on L2 agent node.
enable_ipset = True
"""
conf_linuxbridge_agent_ini = """[linux_bridge]
# (ListOpt) Comma-separated list of
# <physical_network>:<physical_interface> tuples mapping physical
# network names to the agent's node-specific physical network
# interfaces to be used for flat and VLAN networks. All physical
# networks listed in network_vlan_ranges on the server should have
# mappings to appropriate interfaces on each agent.
#
physical_interface_mappings = public:{{ public_interface }}

# Example: physical_interface_mappings = physnet1:eth1

[vxlan]
# (BoolOpt) enable VXLAN on the agent
# VXLAN support can be enabled when agent is managed by ml2 plugin using
# linuxbridge mechanism driver.
enable_vxlan = True
#
# (IntOpt) use specific TTL for vxlan interface protocol packets
# ttl =
#
# (IntOpt) use specific TOS for vxlan interface protocol packets
# tos =
#
# (StrOpt) multicast group or group range to use for broadcast emulation.
# Specifying a range allows different VNIs to use different group addresses,
# reducing or eliminating spurious broadcast traffic to the tunnel endpoints.
# Ranges are specified by using CIDR notation. To reserve a unique group for
# each possible (24-bit) VNI, use a /8 such as 239.0.0.0/8.
# This setting must be the same on all the agents.
# vxlan_group = 224.0.0.1
#
# (StrOpt) Local IP address to use for VXLAN endpoints (required)
local_ip = {{ local_ip }}
#
# (BoolOpt) Flag to enable l2population extension. This option should be used
# in conjunction with ml2 plugin l2population mechanism driver (in that case,
# both linuxbridge and l2population mechanism drivers should be loaded).
# It enables plugin to populate VXLAN forwarding table, in order to limit
# the use of broadcast emulation (multicast will be turned off if kernel and
# iproute2 supports unicast flooding - requires 3.11 kernel and iproute2 3.10)
l2_population = True

[agent]
# Agent's polling interval in seconds
# polling_interval = 2

# (IntOpt) Set new timeout in seconds for new rpc calls after agent receives
# SIGTERM. If value is set to 0, rpc timeout won't be changed.
#
# quitting_rpc_timeout = 10
prevent_arp_spoofing = True

[securitygroup]
# Firewall driver for realizing neutron security group function
# firewall_driver = neutron.agent.firewall.NoopFirewallDriver
# Example: firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver

# Controls if neutron security group is enabled or not.
# It should be false when you use nova security group.
enable_security_group = True
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
"""
conf_l3_agent_ini = """[DEFAULT]
# Show debugging output in log (sets DEBUG log level output)
# debug = False
verbose = True

# L3 requires that an interface driver be set. Choose the one that best
# matches your plugin.
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
external_network_bridge =

# Example of interface_driver option for OVS based plugins (OVS, Ryu, NEC)
# that supports L3 agent
# interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver

# Use veth for an OVS interface or not.
# Support kernels with limited namespace support
# (e.g. RHEL 6.5) so long as ovs_use_veth is set to True.
# ovs_use_veth = False

# Example of interface_driver option for LinuxBridge
# interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver

# Allow overlapping IP (Must have kernel build with CONFIG_NET_NS=y and
# iproute2 package that supports namespaces). This option is deprecated and
# will be removed in a future release, at which point the old behavior of
# use_namespaces = True will be enforced.
# use_namespaces = True

# If use_namespaces is set as False then the agent can only configure one router.

# This is done by setting the specific router_id.
# router_id =

# When external_network_bridge is set, each L3 agent can be associated
# with no more than one external network. This value should be set to the UUID
# of that external network. To allow L3 agent support multiple external
# networks, both the external_network_bridge and gateway_external_network_id
# must be left empty.
# gateway_external_network_id =

# With IPv6, the network used for the external gateway does not need
# to have an associated subnet, since the automatically assigned
# link-local address (LLA) can be used. However, an IPv6 gateway address
# is needed for use as the next-hop for the default route. If no IPv6
# gateway address is configured here, (and only then) the neutron router
# will be configured to get its default route from router advertisements (RAs)
# from the upstream router; in which case the upstream router must also be
# configured to send these RAs.
# The ipv6_gateway, when configured, should be the LLA of the interface
# on the upstream router. If a next-hop using a global unique address (GUA)
# is desired, it needs to be done via a subnet allocated to the network
# and not through this parameter.
# ipv6_gateway =

# (StrOpt) Driver used for ipv6 prefix delegation. This needs to be
# an entry point defined in the neutron.agent.linux.pd_drivers namespace. See
# setup.cfg for entry points included with the neutron source.
# prefix_delegation_driver = dibbler

# Indicates that this L3 agent should also handle routers that do not have
# an external network gateway configured.  This option should be True only
# for a single agent in a Neutron deployment, and may be False for all agents
# if all routers must have an external network gateway
# handle_internal_only_routers = True

# Name of bridge used for external network traffic. This should be set to
# empty value for the linux bridge. when this parameter is set, each L3 agent
# can be associated with no more than one external network.
# This option is deprecated and will be removed in the M release.
# external_network_bridge = br-ex

# TCP Port used by Neutron metadata server
# metadata_port = 9697

# Send this many gratuitous ARPs for HA setup. Set it below or equal to 0
# to disable this feature.
# send_arp_for_ha = 3

# seconds between re-sync routers' data if needed
# periodic_interval = 40

# seconds to start to sync routers' data after
# starting agent
# periodic_fuzzy_delay = 5

# enable_metadata_proxy, which is true by default, can be set to False
# if the Nova metadata server is not available
# enable_metadata_proxy = True

# Iptables mangle mark used to mark metadata valid requests
# metadata_access_mark = 0x1

# Iptables mangle mark used to mark ingress from external network
# external_ingress_mark = 0x2

# router_delete_namespaces, which is True by default, can be set to False if
# namespaces can't be deleted cleanly on the host running the L3 agent.
# Disable this if you hit the issue in
# https://bugs.launchpad.net/neutron/+bug/1052535 or if
# you are sure that your version of iproute suffers from the problem.
# If True, namespaces will be deleted when a router is destroyed.
# This should not be a problem any more.  Refer to bug:
# https://bugs.launchpad.net/neutron/+bug/1418079
# This option is deprecated and will be removed in the M release
# router_delete_namespaces = True

# Timeout for ovs-vsctl commands.
# If the timeout expires, ovs commands will fail with ALARMCLOCK error.
# ovs_vsctl_timeout = 10

# The working mode for the agent. Allowed values are:
# - legacy: this preserves the existing behavior where the L3 agent is
#   deployed on a centralized networking node to provide L3 services
#   like DNAT, and SNAT. Use this mode if you do not want to adopt DVR.
# - dvr: this mode enables DVR functionality, and must be used for an L3
#   agent that runs on a compute host.
# - dvr_snat: this enables centralized SNAT support in conjunction with
#   DVR. This mode must be used for an L3 agent running on a centralized
#   node (or in single-host deployments, e.g. devstack).
# agent_mode = legacy

# Location to store keepalived and all HA configurations
# ha_confs_path = $state_path/ha_confs

# VRRP authentication type AH/PASS
# ha_vrrp_auth_type = PASS

# VRRP authentication password
# ha_vrrp_auth_password =

# The advertisement interval in seconds
# ha_vrrp_advert_int = 2

[AGENT]
# Log agent heartbeats from this L3 agent
# log_agent_heartbeats = False
"""
conf_dhcp_agent_ini = """[DEFAULT]
# Show debugging output in log (sets DEBUG log level output)
# debug = False
verbose = True

# The DHCP agent will resync its state with Neutron to recover from any
# transient notification or rpc errors. The interval is number of
# seconds between attempts.
# resync_interval = 5

# The DHCP agent requires an interface driver be set. Choose the one that best
# matches your plugin.
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver

# Example of interface_driver option for OVS based plugins(OVS, Ryu, NEC, NVP,
# BigSwitch/Floodlight)
# interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver

# Name of Open vSwitch bridge to use
# ovs_integration_bridge = br-int

# Use veth for an OVS interface or not.
# Support kernels with limited namespace support
# (e.g. RHEL 6.5) so long as ovs_use_veth is set to True.
# ovs_use_veth = False

# Example of interface_driver option for LinuxBridge
# interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver

# The agent can use other DHCP drivers.  Dnsmasq is the simplest and requires
# no additional setup of the DHCP server.
dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq

# Allow overlapping IP (Must have kernel build with CONFIG_NET_NS=y and
# iproute2 package that supports namespaces). This option is deprecated and
# will be removed in a future release, at which point the old behavior of
# use_namespaces = True will be enforced.
# use_namespaces = True

# In some cases the neutron router is not present to provide the metadata
# IP but the DHCP server can be used to provide this info. Setting this
# value will force the DHCP server to append specific host routes to the
# DHCP request. If this option is set, then the metadata service will be
# activated for all the networks.
# force_metadata = False

# The DHCP server can assist with providing metadata support on isolated
# networks. Setting this value to True will cause the DHCP server to append
# specific host routes to the DHCP request. The metadata service will only
# be activated when the subnet does not contain any router port. The guest
# instance must be configured to request host routes via DHCP (Option 121).
# This option doesn't have any effect when force_metadata is set to True.
enable_isolated_metadata = True

# Allows for serving metadata requests coming from a dedicated metadata
# access network whose cidr is 169.254.169.254/16 (or larger prefix), and
# is connected to a Neutron router from which the VMs send metadata
# request. In this case DHCP Option 121 will not be injected in VMs, as
# they will be able to reach 169.254.169.254 through a router.
# This option requires enable_isolated_metadata = True
# enable_metadata_network = False

# Number of threads to use during sync process. Should not exceed connection
# pool size configured on server.
# num_sync_threads = 4

# Location to store DHCP server config files
# dhcp_confs = $state_path/dhcp

# Domain to use for building the hostnames. This option will be deprecated in
# a future release. It is being replaced by dns_domain in neutron.conf
# dhcp_domain = openstacklocal

# Override the default dnsmasq settings with this file
dnsmasq_config_file = /etc/neutron/dnsmasq-neutron.conf

# Comma-separated list of DNS servers which will be used by dnsmasq
# as forwarders.
# dnsmasq_dns_servers =

# Base log dir for dnsmasq logging. The log contains DHCP and DNS log
# information and is useful for debugging issues with either DHCP or DNS.
# If this section is null, disable dnsmasq log.
# dnsmasq_base_log_dir =

# Limit number of leases to prevent a denial-of-service.
# dnsmasq_lease_max = 16777216

# Location to DHCP lease relay UNIX domain socket
# dhcp_lease_relay_socket = $state_path/dhcp/lease_relay

# Use broadcast in DHCP replies
# dhcp_broadcast_reply = False

# dhcp_delete_namespaces, which is True by default, can be set to False if
# namespaces can't be deleted cleanly on the host running the DHCP agent.
# Disable this if you hit the issue in
# https://bugs.launchpad.net/neutron/+bug/1052535 or if
# you are sure that your version of iproute suffers from the problem.
# This should not be a problem any more.  Refer to bug:
# https://bugs.launchpad.net/neutron/+bug/1418079
# This option is deprecated and will be removed in the M release
# dhcp_delete_namespaces = True

# Timeout for ovs-vsctl commands.
# If the timeout expires, ovs commands will fail with ALARMCLOCK error.
# ovs_vsctl_timeout = 10

[AGENT]
# Log agent heartbeats from this DHCP agent
# log_agent_heartbeats = False
"""
conf_dnsmasq_neutron_conf = """dhcp-option-force=26,1450
"""
conf_metadata_agent_ini = """[DEFAULT]
# Show debugging output in log (sets DEBUG log level output)
# debug = True
verbose = True

# The Neutron user information for accessing the Neutron API.
auth_uri = {{ auth_uri }}
auth_url = {{ auth_url }}
auth_region = RegionOne
auth_plugin = password
project_domain_id = default
user_domain_id = default
project_name = service
username = neutron
password = {{ password }}

# Turn off verification of the certificate for ssl
# auth_insecure = False
# Certificate Authority public key (CA cert) file for ssl
# auth_ca_cert =
admin_tenant_name = %SERVICE_TENANT_NAME%
admin_user = %SERVICE_USER%
admin_password = %SERVICE_PASSWORD%

# Network service endpoint type to pull from the keystone catalog
# endpoint_type = adminURL

# IP address used by Nova metadata server
nova_metadata_ip = {{ nova_metadata_ip }}

# TCP Port used by Nova metadata server
# nova_metadata_port = 8775

# Which protocol to use for requests to Nova metadata server, http or https
# nova_metadata_protocol = http

# Whether insecure SSL connection should be accepted for Nova metadata server
# requests
# nova_metadata_insecure = False

# Client certificate for nova api, needed when nova api requires client
# certificates
# nova_client_cert =

# Private key for nova client certificate
# nova_client_priv_key =

# When proxying metadata requests, Neutron signs the Instance-ID header with a
# shared secret to prevent spoofing.  You may select any string for a secret,
# but it must match here and in the configuration used by the Nova Metadata
# Server. NOTE: Nova uses the same config key, but in [neutron] section.
metadata_proxy_shared_secret = {{ metadata_proxy_shared_secret }}

# Location of Metadata Proxy UNIX domain socket
# metadata_proxy_socket = $state_path/metadata_proxy

# Metadata Proxy UNIX domain socket mode, 4 values allowed:
# 'deduce': deduce mode from metadata_proxy_user/group values,
# 'user': set metadata proxy socket mode to 0o644, to use when
# metadata_proxy_user is agent effective user or root,
# 'group': set metadata proxy socket mode to 0o664, to use when
# metadata_proxy_group is agent effective group,
# 'all': set metadata proxy socket mode to 0o666, to use otherwise.
# metadata_proxy_socket_mode = deduce

# Number of separate worker processes for metadata server. Defaults to
# half the number of CPU cores
# metadata_workers =

# Number of backlog requests to configure the metadata server socket with
# metadata_backlog = 4096

# URL to connect to the cache backend.
# default_ttl=0 parameter will cause cache entries to never expire.
# Otherwise default_ttl specifies time in seconds a cache entry is valid for.
# No cache is used in case no value is passed.
# cache_url = memory://?default_ttl=5

[AGENT]
# Log agent heartbeats from this Metadata agent
# log_agent_heartbeats = False
"""

class Neutron(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(Neutron, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    @runs_once
    def _create_neutron_db(self, root_db_pass, neutron_db_pass):
        print red(env.host_string + ' | Create neutron database')
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE neutron;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, neutron_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, neutron_db_pass), shell=False)

    def _create_service_credentials(self, os_password, os_auth_url, neutron_pass, endpoint):
        with shell_env(OS_PROJECT_DOMAIN_ID='default',
                       OS_USER_DOMAIN_ID='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2'):
            print red(env.host_string + ' | Create the neutron user')
            sudo('openstack user create --domain default --password {0} neutron'.format(neutron_pass))
            print red(env.host_string + ' | Add the admin role to the neutron user and service project')
            sudo('openstack role add --project service --user neutron admin')
            print red(env.host_string + ' | Create the neutron service entity')
            sudo('openstack service create --name neutron --description "OpenStack Networking" network')
            print red(env.host_string + ' | Create the network service API endpoints')
            sudo('openstack endpoint create --region RegionOne network public {0}'.format(endpoint))
            sudo('openstack endpoint create --region RegionOne network internal {0}'.format(endpoint))
            sudo('openstack endpoint create --region RegionOne network admin {0}'.format(endpoint))

    def _install_self_service(self, connection, rabbit_hosts, rabbit_pass, auth_uri, auth_url, neutron_pass, nova_url, nova_pass, public_interface, local_ip, nova_metadata_ip, metadata_proxy_shared_secret):
        print red(env.host_string + ' | Install the components')
        sudo('apt-get update')
        sudo('apt-get -y install neutron-server neutron-plugin-ml2 neutron-plugin-linuxbridge-agent neutron-l3-agent neutron-dhcp-agent neutron-metadata-agent python-neutronclient conntrack')

        print red(env.host_string + ' | Update /etc/neutron/neutron.conf')
        with open('tmp_neutron_conf_'+env.host_string, 'w') as f:
            f.write(conf_neutron_conf)
        files.upload_template(filename='tmp_neutron_conf_'+env.host_string,
                              destination='/etc/neutron/neutron.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'connection': connection,
                                       'rabbit_hosts': rabbit_hosts,
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'neutron_password': neutron_pass,
                                       'nova_url': nova_url,
                                       'password': nova_pass})
        os.remove('tmp_neutron_conf_'+env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/plugins/ml2/ml2_conf.ini')
        with open('ml2_conf_ini_' + env.host_string, 'w') as f:
            f.write(conf_ml2_conf_ini)
        files.upload_template(filename='ml2_conf_ini_'+env.host_string,
                              destination='/etc/neutron/plugins/ml2/ml2_conf.ini',
                              use_sudo=True)    
        os.remove('ml2_conf_ini_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/plugins/ml2/linuxbridge_agent.ini')
        with open('tmp_linuxbridge_agent_ini_' + env.host_string, 'w') as f:
            f.write(conf_linuxbridge_agent_ini)
        files.upload_template(filename='tmp_linuxbridge_agent_ini_'+env.host_string,
                              destination='/etc/neutron/plugins/ml2/linuxbridge_agent.ini',
                              use_jinja=True,
                              use_sudo=True,
                              context={'public_interface': public_interface,
                                       'local_ip': local_ip})
        os.remove('tmp_linuxbridge_agent_ini_'+env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/l3_agent.ini')
        with open('tmp_l3_agent_ini_' + env.host_string, 'w') as f:
            f.write(conf_l3_agent_ini)
        files.upload_template(filename='tmp_l3_agent_ini_' + env.host_string,
                              destination='/etc/neutron/l3_agent.ini',
                              use_sudo=True)
        os.remove('tmp_l3_agent_ini_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/dhcp_agent.ini')
        with open('tmp_dhcp_agent_ini_' + env.host_string, 'w') as f:
            f.write(conf_dhcp_agent_ini)
        files.upload_template(filename='tmp_dhcp_agent_ini_' + env.host_string,
                              destination='/etc/neutron/dhcp_agent.ini',
                              use_sudo=True)
        os.remove('tmp_dhcp_agent_ini_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/dnsmasq-neutron.conf')
        with open('tmp_dnsmasq_neutron_conf_' + env.host_string, 'w') as f:
            f.write(conf_dnsmasq_neutron_conf)
        files.upload_template(filename='tmp_dnsmasq_neutron_conf_' + env.host_string,
                              destination='/etc/neutron/dnsmasq-neutron.conf',
                              use_sudo=True)
        os.remove('tmp_dnsmasq_neutron_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/metadata_agent.ini')
        with open('tmp_metadata_agent_ini_' + env.host_string, 'w') as f:
            f.write(conf_metadata_agent_ini)
        files.upload_template(filename='tmp_metadata_agent_ini_' + env.host_string,
                              destination='/etc/neutron/metadata_agent.ini',
                              use_jinja=True,
                              use_sudo=True,
                              context={'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': neutron_pass,
                                       'nova_metadata_ip': nova_metadata_ip,
                                       'metadata_proxy_shared_secret': metadata_proxy_shared_secret})
        os.remove('tmp_metadata_agent_ini_' + env.host_string)

        if args.populate:
            print red(env.host_string + ' | Populate the database')
            sudo('su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron', shell=False)

        print red(env.host_string + ' | Restart services')
        sudo('service nova-api restart', warn_only=True)
        sudo('service neutron-server restart')
        sudo('service neutron-plugin-linuxbridge-agent restart')
        sudo('service neutron-dhcp-agent restart')
        sudo('service neutron-metadata-agent restart')
        sudo('service neutron-l3-agent restart')
        print red(env.host_string + ' | Remove the SQLite database file')
        sudo('rm -f /var/lib/neutron/neutron.sqlite')


def main():
    try:
        target = Neutron(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')

    if args.create_neutron_db:
        execute(target._create_neutron_db,
                args.root_db_pass,
                args.neutron_db_pass)
    if args.create_service_credentials:
        execute(target._create_service_credentials,
                args.os_password,
                args.os_auth_url,
                args.neutron_pass,
                args.endpoint)
    if args.install:
        execute(target._install_self_service,
                args.connection, 
                args.rabbit_hosts, 
                args.rabbit_pass, 
                args.auth_uri, 
                args.auth_url, 
                args.neutron_pass, 
                args.nova_url, 
                args.nova_pass, 
                args.public_interface, 
                args.local_ip, 
                args.nova_metadata_ip, 
                args.metadata_proxy_shared_secret)

if __name__ == '__main__':
    main()