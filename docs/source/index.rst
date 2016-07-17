.. Playback documentation master file, created by
   sphinx-quickstart on Sun Jul 17 12:58:59 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Playback's documentation!
====================================

Playback is an OpenStack provisioning and orchestration library that all of the OpenStack components can be deployed automation with high availability on Ubuntu based operating system(Xenial and trusty) as a pythonic way.

This is a simple example to install horizon::

    from playback.api import Horizon

    remote_user = 'ubuntu'
    remote_hosts = ['192.168.1.3', '192.168.1.4']

    horizon = Horizon(user=remote_user, hosts=remote_hosts)
    horizon.install(openstack_host='192.168.1.2', memcached_servers='192.168.1.3:11211,192.168.1.4:11211', time_zone='America/New_York')

Contents:

.. toctree::
   :maxdepth: 2

   prepare_host
   cmd
   mysql_installation
   mysql_config
   mysql_manage
   haproxy_install
   haproxy_config
   rabbitmq
   keystone
   glance
   nova
   nova_compute
   neutron
   neutron_agent
   horizon
   cinder
   swift
   swift_storage
   manila
   manila_share




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

