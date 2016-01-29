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

NOTE: Install is very sensitive about version of components. Please review carefully because default Operating System repos are likely out of date.

Component     | Min Version | Max Version | Comment
------------- | ----------- | ----------- | ------------------
Ansible       | 1.9.4       | < 2.0.0     | On deployment host
Docker        | 1.9.0       | none        | On target nodes
Docker Python | 1.6.0       | none        | On target nodes
Python Jinja2 | 2.6.0       | none        | On deployment host


Install pip on deployment host:
```
salt 'node01.maas' state.apply install_pip
```

Install ansible on deployment host(jinja2 required by ansible):
```
salt 'node01.maas' state.apply install_ansible_1_9_4
```

Install docker-engine on target host:
```
salt 'target*.maas' state.apply install_docker_1_8_2
```

Install OpenStack python clients on target host:
```
salt '*' state.apply install_python_clients
```

Install ntp on target host:
```
salt '*' state.apply install_ntp
```

#### Deploy a registry
Deploy Deocker registry on target host
```
salt 'node02.maas' state.apply install_docker_registry_v2
salt '*.maas' state.appley docker_insecure_registry
```