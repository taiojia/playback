# Playback

Playback is an OpenStack provisioning DevOps tool that all of the OpenStack components can be deployed automation with high availability on Ubuntu based operating system(Xenial and trusty).

Playback provides the following tools to provision OpenStack:

* `env-deploy`: Prepare OpenStack environments, e.g. network card settings, ntp settings, OpenStack client and more.
* `mysql-deploy`: Deploy Galera Cluster for MySQL(Trusty)/MariaDB Galera Cluster(Xenial).
* `haproxy-deploy`: Deploy HAProxy with Keepalived.
* `rabbitmq-deploy`: Deploy RabbitMQ with high availability.
* `keystone-deploy`: Deploy keystone with high availability.
* `glance-deploy`: Deploy Glance with high availability.
* `nova-deploy`: Deploy Nova on controller node with high availability.
* `nova-compute-deploy`: Deploy Nova on compute node.
* `neutron-deploy`: Deploy Neutron on controller node with high availability.
* `neutron-agent-deploy`: Deploy Neutron agent on compute node.
* `horizon-deploy`: Deploy Horizon on controller node with high availability.
* `cinder-deploy`: Deploy Cinder and Volume service on controller node with high availability.
* `swift-deploy`: Deploy Swift Proxy service on controller node with high availability
* `swift-storage-deploy`: Deploy Swift on storage node.
* `manila-deploy`: Deploy Manila on controller node with high availability.
* `manila-share-deploy`: Deploy Manila Share service on controller node with high availability.


## Platform

Playback command-line tools supporting the following platform:

* Mac OS X
* Linux
* Windows (needs [Git Bash](https://git-scm.com/download/win) or [Bash on Ubuntu on Windows](https://msdn.microsoft.com/en-us/commandline/wsl/about))

## Getting statarted

[Quickstart Guide](./docs/quickstart.md)

[Getting stated with 3 controllers and 10 computes deployment](./docs/guide.md)

## Release Notes

* v0.3.4 (Ris)
  * Support OpenStack Mitaka on Xenial and Trusty
  * Support systemd
  * Support Shard File Systems service
  * Fix Live Migration error on xenial
  * Fix Keysonte bugs
  * Fix no JSON object could be decoded with cinder
  * Fix mariadb not clustered
  * Refactor inheritance
