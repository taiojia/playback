# Playback

Playback is an OpenStack provisioning DevOps tool that all of the OpenStack components can be deployed automation with high availability on Ubuntu based operating system.

## Platform

Playback command-line tool supporting the following platform:

* Mac OS X
* Linux
* Windows (needs [Git Bash](https://git-scm.com/download/win) or [Bash on Ubuntu on Windows](https://msdn.microsoft.com/en-us/commandline/wsl/about))

## Getting statarted

[Quickstart Guide](./docs/quickstart.md)
[Getting stated with 3 controllers and 10 computes deployment](./docs/guide.md)

## Release Notes

* v0.0.3 (Pre-release)
  * Support provisions OpenStack Juno
  * Ansible as the backend
  * All configurations definded in one config file

* v0.1.0 (Ris)
  * Support provisions OpenStack Juno with High Availability
  * JSON RPC API for FastForward

* v0.2.3 (Ris)
  * Stable Version for Liberty
  * Support provisions OpenStack Liberty with High Availability
  * The new command-line
  * Ansible backend was deprecated
  * Support library use

* v0.3.0 (Ris)
  * Support provisions OpenStack Mitaka with High Availability
  * Detailed command-line help
  * Refactor command-line arguments
  * Glance, Nova, Nova Compute, Neutron and Neutron Agent now using the memcached servers
  * Fix Horizon memcached server single point
  * Split the templates to a single module
  * User can define the rabbit user
