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

* v0.3.4 (Ris)
  * Support xenial
  * Support systemd
  * Fix Live Migration error on xenial
  * Fix Keysonte bugs
  * Fix no JSON object could be decoded with cinder
  * Fix mariadb not clustered
  * Refactor inheritance
