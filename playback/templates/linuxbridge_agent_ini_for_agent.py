conf_linuxbridge_agent_ini = """[DEFAULT]

#
# From oslo.log
#

# If set to true, the logging level will be set to DEBUG instead of the default
# INFO level. (boolean value)
#debug = false

# If set to false, the logging level will be set to WARNING instead of the
# default INFO level. (boolean value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#verbose = true

# The name of a logging configuration file. This file is appended to any
# existing logging configuration files. For details about logging configuration
# files, see the Python logging module documentation. Note that when logging
# configuration files are used then all logging configuration is set in the
# configuration file and other logging configuration options are ignored (for
# example, logging_context_format_string). (string value)
# Deprecated group/name - [DEFAULT]/log_config
#log_config_append = <None>

# Defines the format string for %%(asctime)s in log records. Default:
# %(default)s . This option is ignored if log_config_append is set. (string
# value)
#log_date_format = %Y-%m-%d %H:%M:%S

# (Optional) Name of log file to send logging output to. If no default is set,
# logging will go to stderr as defined by use_stderr. This option is ignored if
# log_config_append is set. (string value)
# Deprecated group/name - [DEFAULT]/logfile
#log_file = <None>

# (Optional) The base directory used for relative log_file  paths. This option
# is ignored if log_config_append is set. (string value)
# Deprecated group/name - [DEFAULT]/logdir
#log_dir = <None>

# Uses logging handler designed to watch file system. When log file is moved or
# removed this handler will open a new log file with specified path
# instantaneously. It makes sense only if log_file option is specified and
# Linux platform is used. This option is ignored if log_config_append is set.
# (boolean value)
#watch_log_file = false

# Use syslog for logging. Existing syslog format is DEPRECATED and will be
# changed later to honor RFC5424. This option is ignored if log_config_append
# is set. (boolean value)
#use_syslog = false

# Syslog facility to receive log lines. This option is ignored if
# log_config_append is set. (string value)
#syslog_log_facility = LOG_USER

# Log output to standard error. This option is ignored if log_config_append is
# set. (boolean value)
#use_stderr = true

# Format string to use for log messages with context. (string value)
#logging_context_format_string = %(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [%(request_id)s %(user_identity)s] %(instance)s%(message)s

# Format string to use for log messages when context is undefined. (string
# value)
#logging_default_format_string = %(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [-] %(instance)s%(message)s

# Additional data to append to log message when logging level for the message
# is DEBUG. (string value)
#logging_debug_format_suffix = %(funcName)s %(pathname)s:%(lineno)d

# Prefix each line of exception output with this format. (string value)
#logging_exception_prefix = %(asctime)s.%(msecs)03d %(process)d ERROR %(name)s %(instance)s

# Defines the format string for %(user_identity)s that is used in
# logging_context_format_string. (string value)
#logging_user_identity_format = %(user)s %(tenant)s %(domain)s %(user_domain)s %(project_domain)s

# List of package logging levels in logger=LEVEL pairs. This option is ignored
# if log_config_append is set. (list value)
#default_log_levels = amqp=WARN,amqplib=WARN,boto=WARN,qpid=WARN,sqlalchemy=WARN,suds=INFO,oslo.messaging=INFO,iso8601=WARN,requests.packages.urllib3.connectionpool=WARN,urllib3.connectionpool=WARN,websocket=WARN,requests.packages.urllib3.util.retry=WARN,urllib3.util.retry=WARN,keystonemiddleware=WARN,routes.middleware=WARN,stevedore=WARN,taskflow=WARN,keystoneauth=WARN,oslo.cache=INFO,dogpile.core.dogpile=INFO

# Enables or disables publication of error events. (boolean value)
#publish_errors = false

# The format for an instance that is passed with the log message. (string
# value)
#instance_format = "[instance: %(uuid)s] "

# The format for an instance UUID that is passed with the log message. (string
# value)
#instance_uuid_format = "[instance: %(uuid)s] "

# Enables or disables fatal status of deprecations. (boolean value)
#fatal_deprecations = false


[linux_bridge]
# (ListOpt) Comma-separated list of
# <physical_network>:<physical_interface> tuples mapping physical
# network names to the agent's node-specific physical network
# interfaces to be used for flat and VLAN networks. All physical
# networks listed in network_vlan_ranges on the server should have
# mappings to appropriate interfaces on each agent.
#
# physical_interface_mappings =
# Example: physical_interface_mappings = physnet1:eth1
physical_interface_mappings = provider:{{ public_interface }}

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
