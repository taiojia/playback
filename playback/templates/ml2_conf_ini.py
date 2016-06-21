conf_ml2_conf_ini = """[DEFAULT]

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


[ml2]
# (ListOpt) List of network type driver entrypoints to be loaded from
# the neutron.ml2.type_drivers namespace.
#
type_drivers = flat,vlan,vxlan
#type_drivers = local,flat,vlan,gre,vxlan,geneve
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
flat_networks = provider
#flat_networks = public
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
