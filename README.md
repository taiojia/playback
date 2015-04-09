# playback
playback is an OpenStack provisioning DevOps tool that all of the OpenStack components can be deployed with high availability.

### Getting Started

#### Setting your testing environment if you want
You must have the Vagrant installed and than you can provision  the testing environment, the test node you can see `Vagrantfile` at `examples`.
```
cd examples
vagrant up
``` 
    
#### Define a inventory file
The inventory file at `inventory/inventory`, the default setting is the Vagrant testing node. You can according to your environment to change parameters.
```
[zabbix_agents]
tempest ansible_ssh_host=172.16.33.11

[nginx_servers]
tempest ansible_ssh_host=172.16.33.11

[openstack]
controller1 ansible_ssh_host=172.16.33.4
storage1 ansible_ssh_host=172.16.33.5
network ansible_ssh_host=172.16.33.6
compute1 ansible_ssh_host=172.16.33.7
swiftstore1 ansible_ssh_host=172.16.33.8
swiftstore2 ansible_ssh_host=172.16.33.9
swiftstore3 ansible_ssh_host=172.16.33.10

[ntp_server]
controller1 ansible_ssh_host=172.16.33.4

[ntp_clients]
storage1 ansible_ssh_host=172.16.33.5
network ansible_ssh_host=172.16.33.6
compute1 ansible_ssh_host=172.16.33.7
swiftstore1 ansible_ssh_host=172.16.33.8
swiftstore2 ansible_ssh_host=172.16.33.9
swiftstore3 ansible_ssh_host=172.16.33.10

[mariadb]
controller1 ansible_ssh_host=172.16.33.4

[rabbitmq]
controller1 ansible_ssh_host=172.16.33.4

[keystone]
controller1 ansible_ssh_host=172.16.33.4
```
    
#### To define your variables in vars/openstack
The `vars/openstack/openstack.yml` is all the parameters.
* openstack.yml

#### To deploy OpenStack Basic environment including NTP and OpenStack repository
    ansible-playbook openstack_basic_environment.yml

#### To deploy database and messaging queues
    ansible-playbook openstack_basic_database_messaging_single.yml

#### To deploy Keystone
    ansible-playbook openstack_keystone.yml
    
    