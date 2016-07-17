# Playback

Playback is an OpenStack provisioning and orchestration library that all of the OpenStack components can be deployed automation with high availability on Ubuntu based operating system(Xenial and trusty) as a pythonic way.

## Quick-start

    from playback.api import Horizon

    remote_user = 'ubuntu'
    remote_hosts = ['192.168.1.3', '192.168.1.4']

    horizon = Horizon(user=remote_user, hosts=remote_hosts)
    horizon.install(openstack_host='192.168.1.2', memcached_servers='192.168.1.3:11211,192.168.1.4:11211', time_zone='America/New_York')

## Release Notes

* v0.3.5 (Ris)
  Add API for Fastforward