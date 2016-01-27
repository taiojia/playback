# OpenStack SaltStack
The OpenStack SaltStack is a playback subproject to deploy OpenStack using SaltStack.

#### Host machine requirements
The recommended deployment target requirements:
* Two network interfaces.
* More than 8gb main memory.
* At least 40gb disk space.

(Option) All machine needs add to the MAAS.

#### Installing Dependencies
Ubuntu: For Ubuntu based systems where Docker is used it is recommended to use the latest available lts kernel. The latest lts kernel available is the wily kernel (version 4.2). While all kernels should work for Docker, some older kernels may have issues with some of the different Docker backends such as AUFS and OverlayFS. In order to update kernel in Ubuntu 14.04 LTS to 4.2, run:
```
salt '*' state.apply update_kernal_to_4_2
```

Install pip on deployment host:
```
salt 'node01.maas' state.apply install_pip.sls
```
