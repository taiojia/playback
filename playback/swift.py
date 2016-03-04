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
group.add_argument('--create-service-credentials',
                   help='create the swift service credentials',
                   action='store_true',
                   default=False,
                   dest='create_service_credentials')
parser.add_argument('--os-password',
                    help='the password for admin user',
                    action='store',
                    default=None,
                    dest='os_password')
parser.add_argument('--os-auth-url',
                    help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                    action='store',
                    default=None,
                    dest='os_auth_url')
parser.add_argument('--swift-pass',
                    help='password for swift user',
                    action='store',
                    default=None,
                    dest='swift_pass')
parser.add_argument('--public-internal-endpoint',
                    help='public and internal endpoint for swift service e.g. http://CONTROLLER_VIP:8080/v1/AUTH_%%\(tenant_id\)s',
                    action='store',
                    default=None,
                    dest='public_internal_endpoint')
parser.add_argument('--admin-endpoint',
                    help='admin endpoint for swift service e.g. http://CONTROLLER_VIP:8080/v1',
                    action='store',
                    default=None,
                    dest='admin_endpoint')
group.add_argument('--install',
                   help='install swift proxy',
                   action='store_true',
                   default=False,
                   dest='install')
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
parser.add_argument('--memcache-servers',
                    help='memcache servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                    action='store',
                    default=None,
                    dest='memcache_servers')
group.add_argument('--finalize-install',
                   help='finalize swift installation',
                   action='store_true',
                   default=False,
                   dest='finalize_install')
parser.add_argument('--swift-hash-path-suffix',
                    help='swift_hash_path_suffix and swift_hash_path_prefix are used as part of the hashing algorithm when determining data placement in the cluster. These values should remain secret and MUST NOT change once a cluster has been deployed',
                    action='store',
                    default=None,
                    dest='swift_hash_path_suffix')
parser.add_argument('--swift-hash-path-prefix',
                    help='swift_hash_path_suffix and swift_hash_path_prefix are used as part of the hashing algorithm when determining data placement in the cluster. These values should remain secret and MUST NOT change once a cluster has been deployed',
                    action='store',
                    default=None,
                    dest='swift_hash_path_prefix')

args = parser.parse_args()

conf_proxy_server_conf = """[DEFAULT]
# bind_ip = 0.0.0.0
bind_port = 8080
# bind_timeout = 30
# backlog = 4096
swift_dir = /etc/swift
user = swift

# Enables exposing configuration settings via HTTP GET /info.
# expose_info = true

# Key to use for admin calls that are HMAC signed.  Default is empty,
# which will disable admin calls to /info.
# admin_key = secret_admin_key
#
# Allows the ability to withhold sections from showing up in the public calls
# to /info.  You can withhold subsections by separating the dict level with a
# ".".  The following would cause the sections 'container_quotas' and 'tempurl'
# to not be listed, and the key max_failed_deletes would be removed from
# bulk_delete.  Default value is 'swift.valid_api_versions' which allows all
# registered features to be listed via HTTP GET /info except
# swift.valid_api_versions information
# disallowed_sections = swift.valid_api_versions, container_quotas, tempurl

# Use an integer to override the number of pre-forked processes that will
# accept connections.  Should default to the number of effective cpu
# cores in the system.  It's worth noting that individual workers will
# use many eventlet co-routines to service multiple concurrent requests.
# workers = auto
#
# Maximum concurrent requests per worker
# max_clients = 1024
#
# Set the following two lines to enable SSL. This is for testing only.
# cert_file = /etc/swift/proxy.crt
# key_file = /etc/swift/proxy.key
#
# expiring_objects_container_divisor = 86400
# expiring_objects_account_name = expiring_objects
#
# You can specify default log routing here if you want:
# log_name = swift
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_headers = false
# log_address = /dev/log
# The following caps the length of log lines to the value given; no limit if
# set to 0, the default.
# log_max_line_length = 0
#
# This optional suffix (default is empty) that would be appended to the swift transaction
# id allows one to easily figure out from which cluster that X-Trans-Id belongs to.
# This is very useful when one is managing more than one swift cluster.
# trans_id_suffix =
#
# comma separated list of functions to call to setup custom log handlers.
# functions get passed: conf, name, log_to_console, log_route, fmt, logger,
# adapted_logger
# log_custom_handlers =
#
# If set, log_udp_host will override log_address
# log_udp_host =
# log_udp_port = 514
#
# You can enable StatsD logging here:
# log_statsd_host = localhost
# log_statsd_port = 8125
# log_statsd_default_sample_rate = 1.0
# log_statsd_sample_rate_factor = 1.0
# log_statsd_metric_prefix =
#
# Use a comma separated list of full url (http://foo.bar:1234,https://foo.bar)
# cors_allow_origin =
# strict_cors_mode = True
#
# client_timeout = 60
# eventlet_debug = false

[pipeline:main]
pipeline = catch_errors gatekeeper healthcheck proxy-logging cache container_sync bulk ratelimit authtoken keystoneauth container-quotas account-quotas slo dlo versioned_writes proxy-logging proxy-server

[app:proxy-server]
use = egg:swift#proxy
account_autocreate = true
# You can override the default log routing for this app here:
# set log_name = proxy-server
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_address = /dev/log
#
# log_handoffs = true
# recheck_account_existence = 60
# recheck_container_existence = 60
# object_chunk_size = 65536
# client_chunk_size = 65536
#
# How long the proxy server will wait on responses from the a/c/o servers.
# node_timeout = 10
#
# How long the proxy server will wait for an initial response and to read a
# chunk of data from the object servers while serving GET / HEAD requests.
# Timeouts from these requests can be recovered from so setting this to
# something lower than node_timeout would provide quicker error recovery
# while allowing for a longer timeout for non-recoverable requests (PUTs).
# Defaults to node_timeout, should be overriden if node_timeout is set to a
# high number to prevent client timeouts from firing before the proxy server
# has a chance to retry.
# recoverable_node_timeout = node_timeout
#
# conn_timeout = 0.5
#
# How long to wait for requests to finish after a quorum has been established.
# post_quorum_timeout = 0.5
#
# How long without an error before a node's error count is reset. This will
# also be how long before a node is reenabled after suppression is triggered.
# error_suppression_interval = 60
#
# How many errors can accumulate before a node is temporarily ignored.
# error_suppression_limit = 10
#
# If set to 'true' any authorized user may create and delete accounts; if
# 'false' no one, even authorized, can.
# allow_account_management = false
#
# Set object_post_as_copy = false to turn on fast posts where only the metadata
# changes are stored anew and the original data file is kept in place. This
# makes for quicker posts; but since the container metadata isn't updated in
# this mode, features like container sync won't be able to sync posts.
# object_post_as_copy = true
#
# If set to 'true' authorized accounts that do not yet exist within the Swift
# cluster will be automatically created.
# account_autocreate = false
#
# If set to a positive value, trying to create a container when the account
# already has at least this maximum containers will result in a 403 Forbidden.
# Note: This is a soft limit, meaning a user might exceed the cap for
# recheck_account_existence before the 403s kick in.
# max_containers_per_account = 0
#
# This is a comma separated list of account hashes that ignore the
# max_containers_per_account cap.
# max_containers_whitelist =
#
# Comma separated list of Host headers to which the proxy will deny requests.
# deny_host_headers =
#
# Prefix used when automatically creating accounts.
# auto_create_account_prefix = .
#
# Depth of the proxy put queue.
# put_queue_depth = 10
#
# Storage nodes can be chosen at random (shuffle), by using timing
# measurements (timing), or by using an explicit match (affinity).
# Using timing measurements may allow for lower overall latency, while
# using affinity allows for finer control. In both the timing and
# affinity cases, equally-sorting nodes are still randomly chosen to
# spread load.
# The valid values for sorting_method are "affinity", "shuffle", and "timing".
# sorting_method = shuffle
#
# If the "timing" sorting_method is used, the timings will only be valid for
# the number of seconds configured by timing_expiry.
# timing_expiry = 300
#
# The maximum time (seconds) that a large object connection is allowed to last.
# max_large_object_get_time = 86400
#
# Set to the number of nodes to contact for a normal request. You can use
# '* replicas' at the end to have it use the number given times the number of
# replicas for the ring being used for the request.
# request_node_count = 2 * replicas
#
# Which backend servers to prefer on reads. Format is r<N> for region
# N or r<N>z<M> for region N, zone M. The value after the equals is
# the priority; lower numbers are higher priority.
#
# Example: first read from region 1 zone 1, then region 1 zone 2, then
# anything in region 2, then everything else:
# read_affinity = r1z1=100, r1z2=200, r2=300
# Default is empty, meaning no preference.
# read_affinity =
#
# Which backend servers to prefer on writes. Format is r<N> for region
# N or r<N>z<M> for region N, zone M. If this is set, then when
# handling an object PUT request, some number (see setting
# write_affinity_node_count) of local backend servers will be tried
# before any nonlocal ones.
#
# Example: try to write to regions 1 and 2 before writing to any other
# nodes:
# write_affinity = r1, r2
# Default is empty, meaning no preference.
# write_affinity =
#
# The number of local (as governed by the write_affinity setting)
# nodes to attempt to contact first, before any non-local ones. You
# can use '* replicas' at the end to have it use the number given
# times the number of replicas for the ring being used for the
# request.
# write_affinity_node_count = 2 * replicas
#
# These are the headers whose values will only be shown to swift_owners. The
# exact definition of a swift_owner is up to the auth system in use, but
# usually indicates administrative responsibilities.
# swift_owner_headers = x-container-read, x-container-write, x-container-sync-key, x-container-sync-to, x-account-meta-temp-url-key, x-account-meta-temp-url-key-2, x-container-meta-temp-url-key, x-container-meta-temp-url-key-2, x-account-access-control

[filter:tempauth]
use = egg:swift#tempauth
# You can override the default log routing for this filter here:
# set log_name = tempauth
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_headers = false
# set log_address = /dev/log
#
# The reseller prefix will verify a token begins with this prefix before even
# attempting to validate it. Also, with authorization, only Swift storage
# accounts with this prefix will be authorized by this middleware. Useful if
# multiple auth systems are in use for one Swift cluster.
# The reseller_prefix may contain a comma separated list of items. The first
# item is used for the token as mentioned above. If second and subsequent
# items exist, the middleware will handle authorization for an account with
# that prefix. For example, for prefixes "AUTH, SERVICE", a path of
# /v1/SERVICE_account is handled the same as /v1/AUTH_account. If an empty
# (blank) reseller prefix is required, it must be first in the list. Two
# single quote characters indicates an empty (blank) reseller prefix.
# reseller_prefix = AUTH

#
# The require_group parameter names a group that must be presented by
# either X-Auth-Token or X-Service-Token. Usually this parameter is
# used only with multiple reseller prefixes (e.g., SERVICE_require_group=blah).
# By default, no group is needed. Do not use .admin.
# require_group =

# The auth prefix will cause requests beginning with this prefix to be routed
# to the auth subsystem, for granting tokens, etc.
# auth_prefix = /auth/
# token_life = 86400
#
# This allows middleware higher in the WSGI pipeline to override auth
# processing, useful for middleware such as tempurl and formpost. If you know
# you're not going to use such middleware and you want a bit of extra security,
# you can set this to false.
# allow_overrides = true
#
# This specifies what scheme to return with storage urls:
# http, https, or default (chooses based on what the server is running as)
# This can be useful with an SSL load balancer in front of a non-SSL server.
# storage_url_scheme = default
#
# Lastly, you need to list all the accounts/users you want here. The format is:
#   user_<account>_<user> = <key> [group] [group] [...] [storage_url]
# or if you want underscores in <account> or <user>, you can base64 encode them
# (with no equal signs) and use this format:
#   user64_<account_b64>_<user_b64> = <key> [group] [group] [...] [storage_url]
# There are special groups of:
#   .reseller_admin = can do anything to any account for this auth
#   .admin = can do anything within the account
# If neither of these groups are specified, the user can only access containers
# that have been explicitly allowed for them by a .admin or .reseller_admin.
# The trailing optional storage_url allows you to specify an alternate url to
# hand back to the user upon authentication. If not specified, this defaults to
# $HOST/v1/<reseller_prefix>_<account> where $HOST will do its best to resolve
# to what the requester would need to use to reach this host.
# Here are example entries, required for running the tests:
user_admin_admin = admin .admin .reseller_admin
user_test_tester = testing .admin
user_test2_tester2 = testing2 .admin
user_test_tester3 = testing3
user_test5_tester5 = testing5 service

# To enable Keystone authentication you need to have the auth token
# middleware first to be configured. Here is an example below, please
# refer to the keystone's documentation for details about the
# different settings.
#
# You'll need to have as well the keystoneauth middleware enabled
# and have it in your main pipeline so instead of having tempauth in
# there you can change it to: authtoken keystoneauth
#
[filter:authtoken]
paste.filter_factory = keystonemiddleware.auth_token:filter_factory
auth_uri = {{ auth_uri }}
auth_url = {{ auth_url }}
auth_plugin = password
project_domain_id = default
user_domain_id = default
project_name = service
username = swift
password = {{ swift_pass }}
delay_auth_decision = true
# paste.filter_factory = keystonemiddleware.auth_token:filter_factory
# identity_uri = http://keystonehost:35357/
# auth_uri = http://keystonehost:5000/
# admin_tenant_name = service
# admin_user = swift
# admin_password = password
#
# delay_auth_decision defaults to False, but leaving it as false will
# prevent other auth systems, staticweb, tempurl, formpost, and ACLs from
# working. This value must be explicitly set to True.
# delay_auth_decision = False
#
# cache = swift.cache
# include_service_catalog = False
#
[filter:keystoneauth]
use = egg:swift#keystoneauth
# The reseller_prefix option lists account namespaces that this middleware is
# responsible for. The prefix is placed before the Keystone project id.
# For example, for project 12345678, and prefix AUTH, the account is
# named AUTH_12345678 (i.e., path is /v1/AUTH_12345678/...).
# Several prefixes are allowed by specifying a comma-separated list
# as in: "reseller_prefix = AUTH, SERVICE". The empty string indicates a
# single blank/empty prefix. If an empty prefix is required in a list of
# prefixes, a value of '' (two single quote characters) indicates a
# blank/empty prefix. Except for the blank/empty prefix, an underscore ('_')
# character is appended to the value unless already present.
# reseller_prefix = AUTH
#
# The user must have at least one role named by operator_roles on a
# project in order to create, delete and modify containers and objects
# and to set and read privileged headers such as ACLs.
# If there are several reseller prefix items, you can prefix the
# parameter so it applies only to those accounts (for example
# the parameter SERVICE_operator_roles applies to the /v1/SERVICE_<project>
# path). If you omit the prefix, the option applies to all reseller
# prefix items. For the blank/empty prefix, prefix with '' (do not put
# underscore after the two single quote characters).
operator_roles = admin, user
#
# The reseller admin role has the ability to create and delete accounts
# reseller_admin_role = ResellerAdmin
#
# This allows middleware higher in the WSGI pipeline to override auth
# processing, useful for middleware such as tempurl and formpost. If you know
# you're not going to use such middleware and you want a bit of extra security,
# you can set this to false.
# allow_overrides = true
#
# If is_admin is true, a user whose username is the same as the project name
# and who has any role on the project will have access rights elevated to be
# the same as if the user had an operator role. Note that the condition
# compares names rather than UUIDs. This option is deprecated.
# is_admin = false
#
# If the service_roles parameter is present, an X-Service-Token must be
# present in the request that when validated, grants at least one role listed
# in the parameter. The X-Service-Token may be scoped to any project.
# If there are several reseller prefix items, you can prefix the
# parameter so it applies only to those accounts (for example
# the parameter SERVICE_service_roles applies to the /v1/SERVICE_<project>
# path). If you omit the prefix, the option applies to all reseller
# prefix items. For the blank/empty prefix, prefix with '' (do not put
# underscore after the two single quote characters).
# By default, no service_roles are required.
# service_roles =
#
# For backwards compatibility, keystoneauth will match names in cross-tenant
# access control lists (ACLs) when both the requesting user and the tenant
# are in the default domain i.e the domain to which existing tenants are
# migrated. The default_domain_id value configured here should be the same as
# the value used during migration of tenants to keystone domains.
# default_domain_id = default
#
# For a new installation, or an installation in which keystone projects may
# move between domains, you should disable backwards compatible name matching
# in ACLs by setting allow_names_in_acls to false:
# allow_names_in_acls = true

[filter:healthcheck]
use = egg:swift#healthcheck
# An optional filesystem path, which if present, will cause the healthcheck
# URL to return "503 Service Unavailable" with a body of "DISABLED BY FILE".
# This facility may be used to temporarily remove a Swift node from a load
# balancer pool during maintenance or upgrade (remove the file to allow the
# node back into the load balancer pool).
# disable_path =

[filter:cache]
use = egg:swift#memcache
# You can override the default log routing for this filter here:
# set log_name = cache
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_headers = false
# set log_address = /dev/log
#
# If not set here, the value for memcache_servers will be read from
# memcache.conf (see memcache.conf-sample) or lacking that file, it will
# default to the value below. You can specify multiple servers separated with
# commas, as in: 10.1.2.3:11211,10.1.2.4:11211
memcache_servers = {{ memcache_servers }}
#
# Sets how memcache values are serialized and deserialized:
# 0 = older, insecure pickle serialization
# 1 = json serialization but pickles can still be read (still insecure)
# 2 = json serialization only (secure and the default)
# If not set here, the value for memcache_serialization_support will be read
# from /etc/swift/memcache.conf (see memcache.conf-sample).
# To avoid an instant full cache flush, existing installations should
# upgrade with 0, then set to 1 and reload, then after some time (24 hours)
# set to 2 and reload.
# In the future, the ability to use pickle serialization will be removed.
# memcache_serialization_support = 2
#
# Sets the maximum number of connections to each memcached server per worker
# memcache_max_connections = 2
#
# More options documented in memcache.conf-sample

[filter:ratelimit]
use = egg:swift#ratelimit
# You can override the default log routing for this filter here:
# set log_name = ratelimit
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_headers = false
# set log_address = /dev/log
#
# clock_accuracy should represent how accurate the proxy servers' system clocks
# are with each other. 1000 means that all the proxies' clock are accurate to
# each other within 1 millisecond.  No ratelimit should be higher than the
# clock accuracy.
# clock_accuracy = 1000
#
# max_sleep_time_seconds = 60
#
# log_sleep_time_seconds of 0 means disabled
# log_sleep_time_seconds = 0
#
# allows for slow rates (e.g. running up to 5 sec's behind) to catch up.
# rate_buffer_seconds = 5
#
# account_ratelimit of 0 means disabled
# account_ratelimit = 0

# DEPRECATED- these will continue to work but will be replaced
# by the X-Account-Sysmeta-Global-Write-Ratelimit flag.
# Please see ratelimiting docs for details.
# these are comma separated lists of account names
# account_whitelist = a,b
# account_blacklist = c,d

# with container_limit_x = r
# for containers of size x limit write requests per second to r.  The container
# rate will be linearly interpolated from the values given. With the values
# below, a container of size 5 will get a rate of 75.
# container_ratelimit_0 = 100
# container_ratelimit_10 = 50
# container_ratelimit_50 = 20

# Similarly to the above container-level write limits, the following will limit
# container GET (listing) requests.
# container_listing_ratelimit_0 = 100
# container_listing_ratelimit_10 = 50
# container_listing_ratelimit_50 = 20

[filter:domain_remap]
use = egg:swift#domain_remap
# You can override the default log routing for this filter here:
# set log_name = domain_remap
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_headers = false
# set log_address = /dev/log
#
# storage_domain = example.com
# path_root = v1

# Browsers can convert a host header to lowercase, so check that reseller
# prefix on the account is the correct case. This is done by comparing the
# items in the reseller_prefixes config option to the found prefix. If they
# match except for case, the item from reseller_prefixes will be used
# instead of the found reseller prefix. When none match, the default reseller
# prefix is used. When no default reseller prefix is configured, any request
# with an account prefix not in that list will be ignored by this middleware.
# reseller_prefixes = AUTH
# default_reseller_prefix =

[filter:catch_errors]
use = egg:swift#catch_errors
# You can override the default log routing for this filter here:
# set log_name = catch_errors
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_headers = false
# set log_address = /dev/log

[filter:cname_lookup]
# Note: this middleware requires python-dnspython
use = egg:swift#cname_lookup
# You can override the default log routing for this filter here:
# set log_name = cname_lookup
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_headers = false
# set log_address = /dev/log
#
# Specify the storage_domain that match your cloud, multiple domains
# can be specified separated by a comma
# storage_domain = example.com
#
# lookup_depth = 1

# Note: Put staticweb just after your auth filter(s) in the pipeline
[filter:staticweb]
use = egg:swift#staticweb

# Note: Put tempurl before dlo, slo and your auth filter(s) in the pipeline
[filter:tempurl]
use = egg:swift#tempurl
# The methods allowed with Temp URLs.
# methods = GET HEAD PUT POST DELETE
#
# The headers to remove from incoming requests. Simply a whitespace delimited
# list of header names and names can optionally end with '*' to indicate a
# prefix match. incoming_allow_headers is a list of exceptions to these
# removals.
# incoming_remove_headers = x-timestamp
#
# The headers allowed as exceptions to incoming_remove_headers. Simply a
# whitespace delimited list of header names and names can optionally end with
# '*' to indicate a prefix match.
# incoming_allow_headers =
#
# The headers to remove from outgoing responses. Simply a whitespace delimited
# list of header names and names can optionally end with '*' to indicate a
# prefix match. outgoing_allow_headers is a list of exceptions to these
# removals.
# outgoing_remove_headers = x-object-meta-*
#
# The headers allowed as exceptions to outgoing_remove_headers. Simply a
# whitespace delimited list of header names and names can optionally end with
# '*' to indicate a prefix match.
# outgoing_allow_headers = x-object-meta-public-*

# Note: Put formpost just before your auth filter(s) in the pipeline
[filter:formpost]
use = egg:swift#formpost

# Note: Just needs to be placed before the proxy-server in the pipeline.
[filter:name_check]
use = egg:swift#name_check
# forbidden_chars = '"`<>
# maximum_length = 255
# forbidden_regexp = /\./|/\.\./|/\.$|/\.\.$

[filter:list-endpoints]
use = egg:swift#list_endpoints
# list_endpoints_path = /endpoints/

[filter:proxy-logging]
use = egg:swift#proxy_logging
# If not set, logging directives from [DEFAULT] without "access_" will be used
# access_log_name = swift
# access_log_facility = LOG_LOCAL0
# access_log_level = INFO
# access_log_address = /dev/log
#
# If set, access_log_udp_host will override access_log_address
# access_log_udp_host =
# access_log_udp_port = 514
#
# You can use log_statsd_* from [DEFAULT] or override them here:
# access_log_statsd_host = localhost
# access_log_statsd_port = 8125
# access_log_statsd_default_sample_rate = 1.0
# access_log_statsd_sample_rate_factor = 1.0
# access_log_statsd_metric_prefix =
# access_log_headers = false
#
# If access_log_headers is True and access_log_headers_only is set only
# these headers are logged. Multiple headers can be defined as comma separated
# list like this: access_log_headers_only = Host, X-Object-Meta-Mtime
# access_log_headers_only =
#
# By default, the X-Auth-Token is logged. To obscure the value,
# set reveal_sensitive_prefix to the number of characters to log.
# For example, if set to 12, only the first 12 characters of the
# token appear in the log. An unauthorized access of the log file
# won't allow unauthorized usage of the token. However, the first
# 12 or so characters is unique enough that you can trace/debug
# token usage. Set to 0 to suppress the token completely (replaced
# by '...' in the log).
# Note: reveal_sensitive_prefix will not affect the value
# logged with access_log_headers=True.
# reveal_sensitive_prefix = 16
#
# What HTTP methods are allowed for StatsD logging (comma-sep); request methods
# not in this list will have "BAD_METHOD" for the <verb> portion of the metric.
# log_statsd_valid_http_methods = GET,HEAD,POST,PUT,DELETE,COPY,OPTIONS
#
# Note: The double proxy-logging in the pipeline is not a mistake. The
# left-most proxy-logging is there to log requests that were handled in
# middleware and never made it through to the right-most middleware (and
# proxy server). Double logging is prevented for normal requests. See
# proxy-logging docs.

# Note: Put before both ratelimit and auth in the pipeline.
[filter:bulk]
use = egg:swift#bulk
# max_containers_per_extraction = 10000
# max_failed_extractions = 1000
# max_deletes_per_request = 10000
# max_failed_deletes = 1000

# In order to keep a connection active during a potentially long bulk request,
# Swift may return whitespace prepended to the actual response body. This
# whitespace will be yielded no more than every yield_frequency seconds.
# yield_frequency = 10

# Note: The following parameter is used during a bulk delete of objects and
# their container. This would frequently fail because it is very likely
# that all replicated objects have not been deleted by the time the middleware got a
# successful response. It can be configured the number of retries. And the
# number of seconds to wait between each retry will be 1.5**retry

# delete_container_retry_count = 0

# Note: Put after auth and staticweb in the pipeline.
[filter:slo]
use = egg:swift#slo
# max_manifest_segments = 1000
# max_manifest_size = 2097152
# min_segment_size = 1048576
# Start rate-limiting SLO segment serving after the Nth segment of a
# segmented object.
# rate_limit_after_segment = 10
#
# Once segment rate-limiting kicks in for an object, limit segments served
# to N per second. 0 means no rate-limiting.
# rate_limit_segments_per_sec = 0
#
# Time limit on GET requests (seconds)
# max_get_time = 86400

# Note: Put after auth and staticweb in the pipeline.
# If you don't put it in the pipeline, it will be inserted for you.
[filter:dlo]
use = egg:swift#dlo
# Start rate-limiting DLO segment serving after the Nth segment of a
# segmented object.
# rate_limit_after_segment = 10
#
# Once segment rate-limiting kicks in for an object, limit segments served
# to N per second. 0 means no rate-limiting.
# rate_limit_segments_per_sec = 1
#
# Time limit on GET requests (seconds)
# max_get_time = 86400

# Note: Put after auth in the pipeline.
[filter:container-quotas]
use = egg:swift#container_quotas

# Note: Put after auth in the pipeline.
[filter:account-quotas]
use = egg:swift#account_quotas

[filter:gatekeeper]
use = egg:swift#gatekeeper
# You can override the default log routing for this filter here:
# set log_name = gatekeeper
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_headers = false
# set log_address = /dev/log

[filter:container_sync]
use = egg:swift#container_sync
# Set this to false if you want to disallow any full url values to be set for
# any new X-Container-Sync-To headers. This will keep any new full urls from
# coming in, but won't change any existing values already in the cluster.
# Updating those will have to be done manually, as knowing what the true realm
# endpoint should be cannot always be guessed.
# allow_full_urls = true
# Set this to specify this clusters //realm/cluster as "current" in /info
# current = //REALM/CLUSTER

# Note: Put it at the beginning of the pipeline to profile all middleware. But
# it is safer to put this after catch_errors, gatekeeper and healthcheck.
[filter:xprofile]
use = egg:swift#xprofile
# This option enable you to switch profilers which should inherit from python
# standard profiler. Currently the supported value can be 'cProfile',
# 'eventlet.green.profile' etc.
# profile_module = eventlet.green.profile
#
# This prefix will be used to combine process ID and timestamp to name the
# profile data file.  Make sure the executing user has permission to write
# into this path (missing path segments will be created, if necessary).
# If you enable profiling in more than one type of daemon, you must override
# it with an unique value like: /var/log/swift/profile/proxy.profile
# log_filename_prefix = /tmp/log/swift/profile/default.profile
#
# the profile data will be dumped to local disk based on above naming rule
# in this interval.
# dump_interval = 5.0
#
# Be careful, this option will enable profiler to dump data into the file with
# time stamp which means there will be lots of files piled up in the directory.
# dump_timestamp = false
#
# This is the path of the URL to access the mini web UI.
# path = /__profile__
#
# Clear the data when the wsgi server shutdown.
# flush_at_shutdown = false
#
# unwind the iterator of applications
# unwind = false

# Note: Put after slo, dlo in the pipeline.
# If you don't put it in the pipeline, it will be inserted automatically.
[filter:versioned_writes]
use = egg:swift#versioned_writes
# Enables using versioned writes middleware and exposing configuration
# settings via HTTP GET /info.
# WARNING: Setting this option bypasses the "allow_versions" option
# in the container configuration file, which will be eventually
# deprecated. See documentation for more details.
# allow_versioned_writes = false
"""
conf_swift_conf = """[swift-hash]

# swift_hash_path_suffix and swift_hash_path_prefix are used as part of the
# the hashing algorithm when determining data placement in the cluster.
# These values should remain secret and MUST NOT change
# once a cluster has been deployed.

swift_hash_path_suffix = {{ swift_hash_path_suffix }}
swift_hash_path_prefix = {{ swift_hash_path_prefix }}

# storage policies are defined here and determine various characteristics
# about how objects are stored and treated.  Policies are specified by name on
# a per container basis.  Names are case-insensitive.  The policy index is
# specified in the section header and is used internally.  The policy with
# index 0 is always used for legacy containers and can be given a name for use
# in metadata however the ring file name will always be 'object.ring.gz' for
# backwards compatibility.  If no policies are defined a policy with index 0
# will be automatically created for backwards compatibility and given the name
# Policy-0.  A default policy is used when creating new containers when no
# policy is specified in the request.  If no other policies are defined the
# policy with index 0 will be declared the default.  If multiple policies are
# defined you must define a policy with index 0 and you must specify a
# default.  It is recommended you always define a section for
# storage-policy:0.
#
# A 'policy_type' argument is also supported but is not mandatory.  Default
# policy type 'replication' is used when 'policy_type' is unspecified.
[storage-policy:0]
name = Policy-0
default = yes
#policy_type = replication

# the following section would declare a policy called 'silver', the number of
# replicas will be determined by how the ring is built.  In this example the
# 'silver' policy could have a lower or higher # of replicas than the
# 'Policy-0' policy above.  The ring filename will be 'object-1.ring.gz'.  You
# may only specify one storage policy section as the default.  If you changed
# this section to specify 'silver' as the default, when a client created a new
# container w/o a policy specified, it will get the 'silver' policy because
# this config has specified it as the default.  However if a legacy container
# (one created with a pre-policy version of swift) is accessed, it is known
# implicitly to be assigned to the policy with index 0 as opposed to the
# current default.
#[storage-policy:1]
#name = silver
#policy_type = replication

# The following declares a storage policy of type 'erasure_coding' which uses
# Erasure Coding for data reliability.  The 'erasure_coding' storage policy in
# Swift is available as a "beta".  Please refer to Swift documentation for
# details on how the 'erasure_coding' storage policy is implemented.
#
# Swift uses PyECLib, a Python Erasure coding API library, for encode/decode
# operations.  Please refer to Swift documentation for details on how to
# install PyECLib.
#
# When defining an EC policy, 'policy_type' needs to be 'erasure_coding' and
# EC configuration parameters 'ec_type', 'ec_num_data_fragments' and
# 'ec_num_parity_fragments' must be specified.  'ec_type' is chosen from the
# list of EC backends supported by PyECLib.  The ring configured for the
# storage policy must have it's "replica" count configured to
# 'ec_num_data_fragments' + 'ec_num_parity_fragments' - this requirement is
# validated when services start.  'ec_object_segment_size' is the amount of
# data that will be buffered up before feeding a segment into the
# encoder/decoder.  More information about these configuration options and
# supported `ec_type` schemes is available in the Swift documentation.  Please
# refer to Swift documentation for details on how to configure EC policies.
#
# The example 'deepfreeze10-4' policy defined below is a _sample_
# configuration with 10 'data' and 4 'parity' fragments. 'ec_type'
# defines the Erasure Coding scheme. 'jerasure_rs_vand' (Reed-Solomon
# Vandermonde) is used as an example below.
#
#[storage-policy:2]
#name = deepfreeze10-4
#policy_type = erasure_coding
#ec_type = jerasure_rs_vand
#ec_num_data_fragments = 10
#ec_num_parity_fragments = 4
#ec_object_segment_size = 1048576


# The swift-constraints section sets the basic constraints on data
# saved in the swift cluster. These constraints are automatically
# published by the proxy server in responses to /info requests.

[swift-constraints]

# max_file_size is the largest "normal" object that can be saved in
# the cluster. This is also the limit on the size of each segment of
# a "large" object when using the large object manifest support.
# This value is set in bytes. Setting it to lower than 1MiB will cause
# some tests to fail. It is STRONGLY recommended to leave this value at
# the default (5 * 2**30 + 2).

#max_file_size = 5368709122


# max_meta_name_length is the max number of bytes in the utf8 encoding
# of the name portion of a metadata header.

#max_meta_name_length = 128


# max_meta_value_length is the max number of bytes in the utf8 encoding
# of a metadata value

#max_meta_value_length = 256


# max_meta_count is the max number of metadata keys that can be stored
# on a single account, container, or object

#max_meta_count = 90


# max_meta_overall_size is the max number of bytes in the utf8 encoding
# of the metadata (keys + values)

#max_meta_overall_size = 4096

# max_header_size is the max number of bytes in the utf8 encoding of each
# header. Using 8192 as default because eventlet use 8192 as max size of
# header line. This value may need to be increased when using identity
# v3 API tokens including more than 7 catalog entries.
# See also include_service_catalog in proxy-server.conf-sample
# (documented in overview_auth.rst)

#max_header_size = 8192


# By default the maximum number of allowed headers depends on the number of max
# allowed metadata settings plus a default value of 32 for regular http
# headers.  If for some reason this is not enough (custom middleware for
# example) it can be increased with the extra_header_count constraint.

#extra_header_count = 0


# max_object_name_length is the max number of bytes in the utf8 encoding
# of an object name

#max_object_name_length = 1024


# container_listing_limit is the default (and max) number of items
# returned for a container listing request

#container_listing_limit = 10000


# account_listing_limit is the default (and max) number of items returned
# for an account listing request
#account_listing_limit = 10000


# max_account_name_length is the max number of bytes in the utf8 encoding
# of an account name

#max_account_name_length = 256


# max_container_name_length is the max number of bytes in the utf8 encoding
# of a container name

#max_container_name_length = 256


# By default all REST API calls should use "v1" or "v1.0" as the version string,
# for example "/v1/account". This can be manually overridden to make this
# backward-compatible, in case a different version string has been used before.
# Use a comma-separated list in case of multiple allowed versions, for example
# valid_api_versions = v0,v1,v2
# This is only enforced for account, container and object requests. The allowed
# api versions are by default excluded from /info.

# valid_api_versions = v1,v1.0
"""

class Swift(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(Swift, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _create_service_credentials(self, os_password, os_auth_url, swift_pass, public_internal_endpoint, admin_endpoint):
        with shell_env(OS_PROJECT_DOMAIN_ID='default',
                       OS_USER_DOMAIN_ID='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2',
                       OS_AUTH_VERSION='3'):
            print red(env.host_string + ' | Create the swift user')
            sudo('openstack user create --domain default --password {0} swift'.format(swift_pass))
            print red(env.host_string + ' | Add the admin role to the swift user and service project')
            sudo('openstack role add --project service --user swift admin')
            print red(env.host_string + ' | Create the swift service entity')
            sudo('openstack service create --name swift --description "OpenStack Object Storage" object-store')
            print red(env.host_string + ' | Create the Object Storage service API endpoints')
            sudo('openstack endpoint create --region RegionOne object-store public {0}'.format(public_internal_endpoint))
            sudo('openstack endpoint create --region RegionOne object-store internal {0}'.format(public_internal_endpoint))
            sudo('openstack endpoint create --region RegionOne object-store admin {0}'.format(admin_endpoint))

    def _install(self, auth_uri, auth_url, swift_pass, memcache_servers):
        print red(env.host_string + ' | Install swift proxy')
        sudo('apt-get update')
        sudo('apt-get -y install swift swift-proxy python-swiftclient python-keystoneclient python-keystonemiddleware memcached')
        sudo('mkdir /etc/swift')

        print red(env.host_string + ' | Update /etc/swift/proxy-server.conf')
        with open('tmp_proxy_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_proxy_server_conf)
        files.upload_template(filename='tmp_proxy_server_conf_' + env.host_string,
                              destination='/etc/swift/proxy-server.conf',
                              use_sudo=True,
                              use_jinja=True,
                              context={'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'swift_pass': swift_pass,
                                       'memcache_servers': memcache_servers})
        os.remove('tmp_proxy_server_conf_' + env.host_string)

    def _finalize_install(self, swift_hash_path_suffix, swift_hash_path_prefix):
        print red(env.host_string + ' | Update /etc/swift/swift.conf')
        with open('tmp_swift_conf_' + env.host_string, 'w') as f:
            f.write(conf_swift_conf)
        files.upload_template(filename='tmp_swift_conf_' + env.host_string,
                              destination='/etc/swift/swift.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'swift_hash_path_suffix': swift_hash_path_suffix,
                                       'swift_hash_path_prefix': swift_hash_path_prefix})
        os.remove('tmp_swift_conf_' + env.host_string)
        print red(env.host_string + ' | On all nodes, ensure proper ownership of the configuration directory')
        sudo('chown -R root:swift /etc/swift')
        print red(env.host_string + ' | On the controller node and any other nodes running the proxy service, restart the Object Storage proxy service including its dependencies')
        sudo('service memcached restart', warn_only=True)
        sudo('service swift-proxy restart', warn_only=True)
        print red(env.host_string + ' | On the storage nodes, start the Object Storage services')
        sudo('swift-init all start', warn_only=True)



def main():
    try:
        target = Swift(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')

    if args.create_service_credentials:
        execute(target._create_service_credentials,
                args.os_password, 
                args.os_auth_url, 
                args.swift_pass, 
                args.public_internal_endpoint, 
                args.admin_endpoint)
    if args.install:
        execute(target._install,
                args.auth_uri, 
                args.auth_url, 
                args.swift_pass, 
                args.memcache_servers)
    if args.finalize_install:
        execute(target._finalize_install,
                args.swift_hash_path_suffix, 
                args.swift_hash_path_prefix)

if __name__ == '__main__':
    main()

