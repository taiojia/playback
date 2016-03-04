from fabric.api import *
from fabric.contrib import files
from fabric.tasks import Task
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
from tqdm import *

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
                   help='install swift storage',
                   action='store_true',
                   default=False,
                   dest='install')
group.add_argument('--prepare-disks',
                   help='prepare the disks for storage e.g. sdb,sdc',
                   action='store',
                   default=None,
                   dest='prepare_disks')
parser.add_argument('--address', 
                    help='the management interface ip for rsync', 
                    action='store', 
                    dest='address')
parser.add_argument('--bind-ip', 
                    help='the management interface ip for swift storage binding', 
                    action='store', 
                    dest='bind_ip')
group.add_argument('--create-account-builder-file',
                   help='create account ring',
                   action='store_true',
                   default=False,
                   dest='create_account_builder_file')
parser.add_argument('--partitions', 
                    help='2^10 (1024) maximum partitions e.g. 10', 
                    action='store', 
                    default=None,
                    dest='partitions')
parser.add_argument('--replicas', 
                    help='3 replicas of each object e.g. 3', 
                    action='store', 
                    default=None,
                    dest='replicas')
parser.add_argument('--moving', 
                    help='1 hour minimum time between moving a partition more than once e.g. 1', 
                    action='store',
                    default=None, 
                    dest='moving')
group.add_argument('--account-builder-add',
                   help='Add each storage node to the account ring',
                   action='store_true',
                   default=False,
                   dest='account_builder_add')
parser.add_argument('--region', 
                    help='swift storage region e.g. 1', 
                    action='store', 
                    default=None,
                    dest='region')
parser.add_argument('--zone', 
                    help='swift storage zone e.g. 1', 
                    action='store', 
                    default=None,
                    dest='zone')
parser.add_argument('--ip', 
                    help='the IP address of the management network on the storage node e.g. STORAGE_NODE_IP', 
                    action='store', 
                    default=None,
                    dest='ip')
parser.add_argument('--device', 
                    help='a storage device name on the same storage node e.g. SDB', 
                    action='store', 
                    default=None,
                    dest='device')
parser.add_argument('--weight',
                    help='the storage device weight e.g. 100',
                    action='store',
                    default=None,
                    dest='weight')
group.add_argument('--create-container-builder-file',
                   help='create container ring',
                   action='store_true',
                   default=False,
                   dest='create_container_builder_file')
group.add_argument('--container-builder-add',
                   help='Add each storage node to the container ring',
                   action='store_true',
                   default=False,
                   dest='container_builder_add')
group.add_argument('--create-object-builder-file',
                   help='create object ring',
                   action='store_true',
                   default=False,
                   dest='create_object_builder_file')
group.add_argument('--object-builder-add',
                   help='Add each storage node to the object ring',
                   action='store_true',
                   default=False,
                   dest='object_builder_add')
group.add_argument('--sync-builder-file',
                   help='copy the account.ring.gz, container.ring.gz, and object.ring.gz files to the /etc/swift directory on each storage node and any additional nodes running the proxy service',
                   action='store_true',
                   default=False,
                   dest='sync_builder_file')
parser.add_argument('--to', 
                    help='the target hosts where the *.ring.gz file to be added', 
                    action='store', 
                    default=None,
                    dest='to')
group.add_argument('--account-builder-rebalance',
                   help='Rebalance the account ring',
                   action='store_true',
                   default=False,
                   dest='account_builder_rebalance')
group.add_argument('--container-builder-rebalance',
                   help='Rebalance the container ring',
                   action='store_true',
                   default=False,
                   dest='container_builder_rebalance')
group.add_argument('--object-builder-rebalance',
                   help='Rebalance the object ring',
                   action='store_true',
                   default=False,
                   dest='object_builder_rebalance')

args = parser.parse_args()

conf_rsyncd_conf = """uid = swift
gid = swift
log file = /var/log/rsyncd.log
pid file = /var/run/rsyncd.pid
address = {{ address }}

[account]
max connections = 2
path = /srv/node/
read only = false
lock file = /var/lock/account.lock

[container]
max connections = 2
path = /srv/node/
read only = false
lock file = /var/lock/container.lock

[object]
max connections = 2
path = /srv/node/
read only = false
lock file = /var/lock/object.lock
"""
conf_rsync = """# defaults file for rsync daemon mode

# start rsync in daemon mode from init.d script?
#  only allowed values are "true", "false", and "inetd"
#  Use "inetd" if you want to start the rsyncd from inetd,
#  all this does is prevent the init.d script from printing a message
#  about not starting rsyncd (you still need to modify inetd's config yourself).
RSYNC_ENABLE=true

# which file should be used as the configuration file for rsync.
# This file is used instead of the default /etc/rsyncd.conf
# Warning: This option has no effect if the daemon is accessed
#          using a remote shell. When using a different file for
#          rsync you might want to symlink /etc/rsyncd.conf to
#          that file.
# RSYNC_CONFIG_FILE=

# what extra options to give rsync --daemon?
#  that excludes the --daemon; that's always done in the init.d script
#  Possibilities are:
#   --address=123.45.67.89              (bind to a specific IP address)
#   --port=8730                         (bind to specified port; default 873)
RSYNC_OPTS=''

# run rsyncd at a nice level?
#  the rsync daemon can impact performance due to much I/O and CPU usage,
#  so you may want to run it at a nicer priority than the default priority.
#  Allowed values are 0 - 19 inclusive; 10 is a reasonable value.
RSYNC_NICE=''

# run rsyncd with ionice?
#  "ionice" does for IO load what "nice" does for CPU load.
#  As rsync is often used for backups which aren't all that time-critical,
#  reducing the rsync IO priority will benefit the rest of the system.
#  See the manpage for ionice for allowed options.
#  -c3 is recommended, this will run rsync IO at "idle" priority. Uncomment
#  the next line to activate this.
# RSYNC_IONICE='-c3'

# Don't forget to create an appropriate config file,
# else the daemon will not start.
"""
conf_account_server_conf = """[DEFAULT]
bind_ip = {{ bind_ip }}
bind_port = 6002
# bind_timeout = 30
# backlog = 4096
user = swift
swift_dir = /etc/swift
devices = /srv/node
mount_check = true
# disable_fallocate = false
#
# Use an integer to override the number of pre-forked processes that will
# accept connections.
# workers = auto
#
# Maximum concurrent requests per worker
# max_clients = 1024
#
# You can specify default log routing here if you want:
# log_name = swift
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
# The following caps the length of log lines to the value given; no limit if
# set to 0, the default.
# log_max_line_length = 0
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
# If you don't mind the extra disk space usage in overhead, you can turn this
# on to preallocate disk space with SQLite databases to decrease fragmentation.
# db_preallocation = off
#
# eventlet_debug = false
#
# You can set fallocate_reserve to the number of bytes you'd like fallocate to
# reserve, whether there is space for the given file size or not.
# fallocate_reserve = 0

[pipeline:main]
pipeline = healthcheck recon account-server

[app:account-server]
use = egg:swift#account
# You can override the default log routing for this app here:
# set log_name = account-server
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_requests = true
# set log_address = /dev/log
#
# auto_create_account_prefix = .
#
# Configure parameter for creating specific server
# To handle all verbs, including replication verbs, do not specify
# "replication_server" (this is the default). To only handle replication,
# set to a True value (e.g. "True" or "1"). To handle only non-replication
# verbs, set to "False". Unless you have a separate replication network, you
# should not specify any value for "replication_server".
# replication_server = false

[filter:healthcheck]
use = egg:swift#healthcheck
# An optional filesystem path, which if present, will cause the healthcheck
# URL to return "503 Service Unavailable" with a body of "DISABLED BY FILE"
# disable_path =

[filter:recon]
use = egg:swift#recon
recon_cache_path = /var/cache/swift

[account-replicator]
# You can override the default log routing for this app here (don't use set!):
# log_name = account-replicator
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# per_diff = 1000
# max_diffs = 100
# concurrency = 8
#
# Time in seconds to wait between replication passes
# interval = 30
# run_pause is deprecated, use interval instead
# run_pause = 30
#
# node_timeout = 10
# conn_timeout = 0.5
#
# The replicator also performs reclamation
# reclaim_age = 604800
#
# Allow rsync to compress data which is transmitted to destination node
# during sync. However, this is applicable only when destination node is in
# a different region than the local one.
# rsync_compress = no
#
# Format of the rysnc module where the replicator will send data. See
# etc/rsyncd.conf-sample for some usage examples.
# rsync_module = {replication_ip}::account
#
# recon_cache_path = /var/cache/swift

[account-auditor]
# You can override the default log routing for this app here (don't use set!):
# log_name = account-auditor
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# Will audit each account at most once per interval
# interval = 1800
#
# log_facility = LOG_LOCAL0
# log_level = INFO
# accounts_per_second = 200
# recon_cache_path = /var/cache/swift

[account-reaper]
# You can override the default log routing for this app here (don't use set!):
# log_name = account-reaper
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# concurrency = 25
# interval = 3600
# node_timeout = 10
# conn_timeout = 0.5
#
# Normally, the reaper begins deleting account information for deleted accounts
# immediately; you can set this to delay its work however. The value is in
# seconds; 2592000 = 30 days for example.
# delay_reaping = 0
#
# If the account fails to be be reaped due to a persistent error, the
# account reaper will log a message such as:
#     Account <name> has not been reaped since <date>
# You can search logs for this message if space is not being reclaimed
# after you delete account(s).
# Default is 2592000 seconds (30 days). This is in addition to any time
# requested by delay_reaping.
# reap_warn_after = 2592000

# Note: Put it at the beginning of the pipeline to profile all middleware. But
# it is safer to put this after healthcheck.
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
# it with an unique value like: /var/log/swift/profile/account.profile
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
"""
conf_container_server_conf = """[DEFAULT]
bind_ip = {{ bind_ip }}
bind_port = 6001
# bind_timeout = 30
# backlog = 4096
user = swift
swift_dir = /etc/swift
devices = /srv/node
mount_check = true
# disable_fallocate = false
#
# Use an integer to override the number of pre-forked processes that will
# accept connections.
# workers = auto
#
# Maximum concurrent requests per worker
# max_clients = 1024
#
# This is a comma separated list of hosts allowed in the X-Container-Sync-To
# field for containers. This is the old-style of using container sync. It is
# strongly recommended to use the new style of a separate
# container-sync-realms.conf -- see container-sync-realms.conf-sample
# allowed_sync_hosts = 127.0.0.1
#
# You can specify default log routing here if you want:
# log_name = swift
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
# The following caps the length of log lines to the value given; no limit if
# set to 0, the default.
# log_max_line_length = 0
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
# If you don't mind the extra disk space usage in overhead, you can turn this
# on to preallocate disk space with SQLite databases to decrease fragmentation.
# db_preallocation = off
#
# eventlet_debug = false
#
# You can set fallocate_reserve to the number of bytes you'd like fallocate to
# reserve, whether there is space for the given file size or not.
# fallocate_reserve = 0

[pipeline:main]
pipeline = healthcheck recon container-server

[app:container-server]
use = egg:swift#container
# You can override the default log routing for this app here:
# set log_name = container-server
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_requests = true
# set log_address = /dev/log
#
# node_timeout = 3
# conn_timeout = 0.5
# allow_versions = false
# auto_create_account_prefix = .
#
# Configure parameter for creating specific server
# To handle all verbs, including replication verbs, do not specify
# "replication_server" (this is the default). To only handle replication,
# set to a True value (e.g. "True" or "1"). To handle only non-replication
# verbs, set to "False". Unless you have a separate replication network, you
# should not specify any value for "replication_server".
# replication_server = false

[filter:healthcheck]
use = egg:swift#healthcheck
# An optional filesystem path, which if present, will cause the healthcheck
# URL to return "503 Service Unavailable" with a body of "DISABLED BY FILE"
# disable_path =

[filter:recon]
use = egg:swift#recon
recon_cache_path = /var/cache/swift

[container-replicator]
# You can override the default log routing for this app here (don't use set!):
# log_name = container-replicator
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# per_diff = 1000
# max_diffs = 100
# concurrency = 8
#
# Time in seconds to wait between replication passes
# interval = 30
# run_pause is deprecated, use interval instead
# run_pause = 30
#
# node_timeout = 10
# conn_timeout = 0.5
#
# The replicator also performs reclamation
# reclaim_age = 604800
#
# Allow rsync to compress data which is transmitted to destination node
# during sync. However, this is applicable only when destination node is in
# a different region than the local one.
# rsync_compress = no
#
# Format of the rysnc module where the replicator will send data. See
# etc/rsyncd.conf-sample for some usage examples.
# rsync_module = {replication_ip}::container
#
# recon_cache_path = /var/cache/swift

[container-updater]
# You can override the default log routing for this app here (don't use set!):
# log_name = container-updater
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# interval = 300
# concurrency = 4
# node_timeout = 3
# conn_timeout = 0.5
#
# slowdown will sleep that amount between containers
# slowdown = 0.01
#
# Seconds to suppress updating an account that has generated an error
# account_suppression_time = 60
#
# recon_cache_path = /var/cache/swift

[container-auditor]
# You can override the default log routing for this app here (don't use set!):
# log_name = container-auditor
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# Will audit each container at most once per interval
# interval = 1800
#
# containers_per_second = 200
# recon_cache_path = /var/cache/swift

[container-sync]
# You can override the default log routing for this app here (don't use set!):
# log_name = container-sync
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# If you need to use an HTTP Proxy, set it here; defaults to no proxy.
# You can also set this to a comma separated list of HTTP Proxies and they will
# be randomly used (simple load balancing).
# sync_proxy = http://10.1.1.1:8888,http://10.1.1.2:8888
#
# Will sync each container at most once per interval
# interval = 300
#
# Maximum amount of time to spend syncing each container per pass
# container_time = 60
#
# Maximum amount of time in seconds for the connection attempt
# conn_timeout = 5
# Server errors from requests will be retried by default
# request_tries = 3
#
# Internal client config file path
# internal_client_conf_path = /etc/swift/internal-client.conf

# Note: Put it at the beginning of the pipeline to profile all middleware. But
# it is safer to put this after healthcheck.
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
# it with an unique value like: /var/log/swift/profile/container.profile
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
"""
conf_object_server_conf = """[DEFAULT]
bind_ip = {{ bind_ip }}
bind_port = 6000
# bind_timeout = 30
# backlog = 4096
user = swift
swift_dir = /etc/swift
devices = /srv/node
mount_check = true
# disable_fallocate = false
# expiring_objects_container_divisor = 86400
# expiring_objects_account_name = expiring_objects
#
# Use an integer to override the number of pre-forked processes that will
# accept connections.  NOTE: if servers_per_port is set, this setting is
# ignored.
# workers = auto
#
# Make object-server run this many worker processes per unique port of
# "local" ring devices across all storage policies.  This can help provide
# the isolation of threads_per_disk without the severe overhead.  The default
# value of 0 disables this feature.
# servers_per_port = 0
#
# Maximum concurrent requests per worker
# max_clients = 1024
#
# You can specify default log routing here if you want:
# log_name = swift
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
# The following caps the length of log lines to the value given; no limit if
# set to 0, the default.
# log_max_line_length = 0
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
# eventlet_debug = false
#
# You can set fallocate_reserve to the number of bytes you'd like fallocate to
# reserve, whether there is space for the given file size or not.
# fallocate_reserve = 0
#
# Time to wait while attempting to connect to another backend node.
# conn_timeout = 0.5
# Time to wait while sending each chunk of data to another backend node.
# node_timeout = 3
# Time to wait while sending a container update on object update.
# container_update_timeout = 1.0
# Time to wait while receiving each chunk of data from a client or another
# backend node.
# client_timeout = 60
#
# network_chunk_size = 65536
# disk_chunk_size = 65536

[pipeline:main]
pipeline = healthcheck recon object-server

[app:object-server]
use = egg:swift#object
# You can override the default log routing for this app here:
# set log_name = object-server
# set log_facility = LOG_LOCAL0
# set log_level = INFO
# set log_requests = true
# set log_address = /dev/log
#
# max_upload_time = 86400
# slow = 0
#
# Objects smaller than this are not evicted from the buffercache once read
# keep_cache_size = 5242880
#
# If true, objects for authenticated GET requests may be kept in buffer cache
# if small enough
# keep_cache_private = false
#
# on PUTs, sync data every n MB
# mb_per_sync = 512
#
# Comma separated list of headers that can be set in metadata on an object.
# This list is in addition to X-Object-Meta-* headers and cannot include
# Content-Type, etag, Content-Length, or deleted
# allowed_headers = Content-Disposition, Content-Encoding, X-Delete-At, X-Object-Manifest, X-Static-Large-Object
#
# auto_create_account_prefix = .
#
# A value of 0 means "don't use thread pools". A reasonable starting point is
# 4.
# threads_per_disk = 0
#
# Configure parameter for creating specific server
# To handle all verbs, including replication verbs, do not specify
# "replication_server" (this is the default). To only handle replication,
# set to a True value (e.g. "True" or "1"). To handle only non-replication
# verbs, set to "False". Unless you have a separate replication network, you
# should not specify any value for "replication_server".
# replication_server = false
#
# Set to restrict the number of concurrent incoming REPLICATION requests
# Set to 0 for unlimited
# Note that REPLICATION is currently an ssync only item
# replication_concurrency = 4
#
# Restricts incoming REPLICATION requests to one per device,
# replication_currency above allowing. This can help control I/O to each
# device, but you may wish to set this to False to allow multiple REPLICATION
# requests (up to the above replication_concurrency setting) per device.
# replication_one_per_device = True
#
# Number of seconds to wait for an existing replication device lock before
# giving up.
# replication_lock_timeout = 15
#
# These next two settings control when the REPLICATION subrequest handler will
# abort an incoming REPLICATION attempt. An abort will occur if there are at
# least threshold number of failures and the value of failures / successes
# exceeds the ratio. The defaults of 100 and 1.0 means that at least 100
# failures have to occur and there have to be more failures than successes for
# an abort to occur.
# replication_failure_threshold = 100
# replication_failure_ratio = 1.0
#
# Use splice() for zero-copy object GETs. This requires Linux kernel
# version 3.0 or greater. If you set "splice = yes" but the kernel
# does not support it, error messages will appear in the object server
# logs at startup, but your object servers should continue to function.
#
# splice = no

[filter:healthcheck]
use = egg:swift#healthcheck
# An optional filesystem path, which if present, will cause the healthcheck
# URL to return "503 Service Unavailable" with a body of "DISABLED BY FILE"
# disable_path =

[filter:recon]
use = egg:swift#recon
recon_cache_path = /var/cache/swift
recon_lock_path = /var/lock

[object-replicator]
# You can override the default log routing for this app here (don't use set!):
# log_name = object-replicator
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# daemonize = on
#
# Time in seconds to wait between replication passes
# interval = 30
# run_pause is deprecated, use interval instead
# run_pause = 30
#
# concurrency = 1
# stats_interval = 300
#
# The sync method to use; default is rsync but you can use ssync to try the
# EXPERIMENTAL all-swift-code-no-rsync-callouts method. Once ssync is verified
# as having performance comparable to, or better than, rsync, we plan to
# deprecate rsync so we can move on with more features for replication.
# sync_method = rsync
#
# max duration of a partition rsync
# rsync_timeout = 900
#
# bandwidth limit for rsync in kB/s. 0 means unlimited
# rsync_bwlimit = 0
#
# passed to rsync for io op timeout
# rsync_io_timeout = 30
#
# Allow rsync to compress data which is transmitted to destination node
# during sync. However, this is applicable only when destination node is in
# a different region than the local one.
# NOTE: Objects that are already compressed (for example: .tar.gz, .mp3) might
# slow down the syncing process.
# rsync_compress = no
#
# Format of the rysnc module where the replicator will send data. See
# etc/rsyncd.conf-sample for some usage examples.
# rsync_module = {replication_ip}::object
#
# node_timeout = <whatever's in the DEFAULT section or 10>
# max duration of an http request; this is for REPLICATE finalization calls and
# so should be longer than node_timeout
# http_timeout = 60
#
# attempts to kill all workers if nothing replicates for lockup_timeout seconds
# lockup_timeout = 1800
#
# The replicator also performs reclamation
# reclaim_age = 604800
#
# ring_check_interval = 15
# recon_cache_path = /var/cache/swift
#
# limits how long rsync error log lines are
# 0 means to log the entire line
# rsync_error_log_line_length = 0
#
# handoffs_first and handoff_delete are options for a special case
# such as disk full in the cluster. These two options SHOULD NOT BE
# CHANGED, except for such an extreme situations. (e.g. disks filled up
# or are about to fill up. Anyway, DO NOT let your drives fill up)
# handoffs_first is the flag to replicate handoffs prior to canonical
# partitions. It allows to force syncing and deleting handoffs quickly.
# If set to a True value(e.g. "True" or "1"), partitions
# that are not supposed to be on the node will be replicated first.
# handoffs_first = False
#
# handoff_delete is the number of replicas which are ensured in swift.
# If the number less than the number of replicas is set, object-replicator
# could delete local handoffs even if all replicas are not ensured in the
# cluster. Object-replicator would remove local handoff partition directories
# after syncing partition when the number of successful responses is greater
# than or equal to this number. By default(auto), handoff partitions will be
# removed  when it has successfully replicated to all the canonical nodes.
# handoff_delete = auto

[object-reconstructor]
# You can override the default log routing for this app here (don't use set!):
# Unless otherwise noted, each setting below has the same meaning as described
# in the [object-replicator] section, however these settings apply to the EC
# reconstructor
#
# log_name = object-reconstructor
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# daemonize = on
#
# Time in seconds to wait between reconstruction passes
# interval = 30
# run_pause is deprecated, use interval instead
# run_pause = 30
#
# concurrency = 1
# stats_interval = 300
# node_timeout = 10
# http_timeout = 60
# lockup_timeout = 1800
# reclaim_age = 604800
# ring_check_interval = 15
# recon_cache_path = /var/cache/swift
# handoffs_first = False

[object-updater]
# You can override the default log routing for this app here (don't use set!):
# log_name = object-updater
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# interval = 300
# concurrency = 1
# node_timeout = <whatever's in the DEFAULT section or 10>
# slowdown will sleep that amount between objects
# slowdown = 0.01
#
# recon_cache_path = /var/cache/swift

[object-auditor]
# You can override the default log routing for this app here (don't use set!):
# log_name = object-auditor
# log_facility = LOG_LOCAL0
# log_level = INFO
# log_address = /dev/log
#
# You can set the disk chunk size that the auditor uses making it larger if
# you like for more efficient local auditing of larger objects
# disk_chunk_size = 65536
# files_per_second = 20
# concurrency = 1
# bytes_per_second = 10000000
# log_time = 3600
# zero_byte_files_per_second = 50
# recon_cache_path = /var/cache/swift

# Takes a comma separated list of ints. If set, the object auditor will
# increment a counter for every object whose size is <= to the given break
# points and report the result after a full scan.
# object_size_stats =

# Note: Put it at the beginning of the pipleline to profile all middleware. But
# it is safer to put this after healthcheck.
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
# it with an unique value like: /var/log/swift/profile/object.profile
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
"""


class SwiftStorage(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(SwiftStorage, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _prepare_disks(self, prepare_disks):
        """format disks to xfs and mount it"""
        fstab = '/etc/fstab'
        for disk in tqdm(prepare_disks.split(',')):
            sudo('umount /dev/{0}'.format(disk), warn_only=True)
            if sudo('mkfs.xfs -f /dev/{0}'.format(disk), warn_only=True).failed:
                sudo('apt-get update')
                sudo('apt-get -y install xfsprogs')
                sudo('mkfs.xfs -f /dev/{0}'.format(disk))
            sudo('mkdir -p /srv/node/{0}'.format(disk))
            files.append(fstab, '/dev/{0} /srv/node/{1} xfs noatime,nodiratime,nobarrier,logbufs=8 0 2'.format(disk,disk), use_sudo=True)
            sudo('mount /srv/node/{0}'.format(disk))


    def _install(self, address, bind_ip):
        print red(env.host_string + ' | Install the supporting utility packages')
        sudo('apt-get update')
        sudo('apt-get -y install xfsprogs rsync')

        print red(env.host_string + ' | Update /etc/rsyncd.conf')
        with open('tmp_rsyncd_conf_' + env.host_string, 'w') as f:
            f.write(conf_rsyncd_conf)
        files.upload_template(filename='tmp_rsyncd_conf_' + env.host_string,
                              destination='/etc/rsyncd.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'address': address})
        os.remove('tmp_rsyncd_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/default/rsync')
        with open('tmp_rsync_' + env.host_string, 'w') as f:
            f.write(conf_rsync)
        files.upload_template(filename='tmp_rsync_' + env.host_string,
                              destination='/etc/default/rsync',
                              use_jinja=True,
                              use_sudo=True,)
        os.remove('tmp_rsync_' + env.host_string)

        print red(env.host_string + ' | Start the rsync service')
        if sudo('service rsync start', warn_only=True).failed:
            sudo('service rsync restart')

        print red(env.host_string + ' | Install swift storage')
        sudo('apt-get -y install swift swift-account swift-container swift-object')

        print red(env.host_string + ' | Update /etc/swift/account-server.conf')
        with open('tmp_account_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_account_server_conf)
        files.upload_template(filename='tmp_account_server_conf_' + env.host_string,
                              destination='/etc/swift/account-server.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'bind_ip': bind_ip})
        os.remove('tmp_account_server_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/swift/container-server.conf')
        with open('tmp_container_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_container_server_conf)
        files.upload_template(filename='tmp_container_server_conf_' + env.host_string,
                              destination='/etc/swift/container-server.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'bind_ip': bind_ip})
        os.remove('tmp_container_server_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/swift/object-server.conf')
        with open('tmp_object_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_object_server_conf)
        files.upload_template(filename='tmp_object_server_conf_' + env.host_string,
                              destination='/etc/swift/object-server.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'bind_ip': bind_ip})
        os.remove('tmp_object_server_conf_' + env.host_string)

        print red(env.host_string + ' | Ensure proper ownership of the mount point directory structure')
        sudo('chown -R swift:swift /srv/node')

        print red(env.host_string + ' | Create the recon directory and ensure proper ownership of it')
        sudo('mkdir -p /var/cache/swift')
        sudo('chown -R root:swift /var/cache/swift')

    def _create_account_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder account.builder create {0} {1} {2}'.format(partitions, replicas, moving))


    def _account_builder_add(self, region, zone, ip, device, weight):
        with cd('/etc/swift'):
            sudo('swift-ring-builder account.builder add --region {0} --zone {1} --ip {2} --port 6002 --device {3} --weight {4}'.format(region,
                                                                                                                                        zone,
                                                                                                                                        ip,
                                                                                                                                        device,
                                                                                                                                        weight))
            print red(env.host_string + ' | Verify the ring contents')
            sudo('swift-ring-builder account.builder')
             
    def _account_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder account.builder rebalance')


    def _create_container_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder container.builder create {0} {1} {2}'.format(partitions, replicas, moving))

    def _container_builder_add(self, region, zone, ip, device, weight):
        with cd('/etc/swift'):
            sudo('swift-ring-builder container.builder add --region {0} --zone {1} --ip {2} --port 6001 --device {3} --weight {4}'.format(region,
                                                                                                                                        zone,
                                                                                                                                        ip,
                                                                                                                                        device,
                                                                                                                                        weight))
            print red(env.host_string + ' | Verify the ring contents')
            sudo('swift-ring-builder container.builder')
            
    def _container_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder container.builder rebalance')

    def _create_object_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder object.builder create {0} {1} {2}'.format(partitions, replicas, moving))

    def _object_builder_add(self, region, zone, ip, device, weight):
        with cd('/etc/swift'):
            sudo('swift-ring-builder object.builder add --region {0} --zone {1} --ip {2} --port 6000 --device {3} --weight {4}'.format(region,
                                                                                                                                        zone,
                                                                                                                                        ip,
                                                                                                                                        device,
                                                                                                                                        weight))
            print red(env.host_string + ' | Verify the ring contents')
            sudo('swift-ring-builder object.builder')

    def _object_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder object.builder rebalance')
    
    def _get_builder_file(self):
        get('/etc/swift/account.ring.gz', './account.ring.gz')
        get('/etc/swift/container.ring.gz', './container.ring.gz')
        get('/etc/swift/object.ring.gz', './object.ring.gz')

    def _sync_builder_file(self):
        put('./account.ring.gz', '/etc/swift/account.ring.gz', use_sudo=True)
        put('./container.ring.gz', '/etc/swift/container.ring.gz', use_sudo=True)
        put('./object.ring.gz', '/etc/swift/object.ring.gz', use_sudo=True)
        



def main():
    try:
        target = SwiftStorage(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')

    if args.prepare_disks:
        execute(target._prepare_disks, 
                args.prepare_disks)
    if args.install:
        execute(target._install,
                args.address, 
                args.bind_ip)
    if args.create_account_builder_file:
        execute(target._create_account_builder_file,
                args.partitions, 
                args.replicas, 
                args.moving)
    if args.account_builder_add:
        execute(target._account_builder_add,
                args.region, 
                args.zone, 
                args.ip, 
                args.device, 
                args.weight)
    if args.account_builder_rebalance:
        execute(target._account_builder_rebalance)
    if args.create_container_builder_file:
        execute(target._create_container_builder_file,
                args.partitions,
                args.replicas,
                args.moving)
    if args.container_builder_add:
        execute(target._container_builder_add,
                args.region, 
                args.zone, 
                args.ip, 
                args.device, 
                args.weight)
    if args.container_builder_rebalance:
        execute(target._container_builder_rebalance)
    if args.create_object_builder_file:
        execute(target._create_object_builder_file,
                args.partitions,
                args.replicas,
                args.moving)
    if args.object_builder_add:
        execute(target._object_builder_add,
                args.region, 
                args.zone, 
                args.ip, 
                args.device, 
                args.weight)
    if args.object_builder_rebalance:
        execute(target._object_builder_rebalance)
    if args.sync_builder_file:
        execute(target._get_builder_file)
        execute(target._sync_builder_file, hosts=args.to.split(','))
        os.remove('account.ring.gz')
        os.remove('container.ring.gz')
        os.remove('object.ring.gz')
    

if __name__ == '__main__':
    main()