# playback
playback is a OpenStack provisioning tools that can deploy all of OpenStack components with high availability.

### Getting Started
#### Define a inventory file in inventory/inventory
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
* database.yml
* node.yml
* ntp.yml
* passwords.yml

#### To deploy OpenStack Basic environment including NTP and OpenStack repository
    `ansible-playbook openstack_basic_environment.yml`

#### To deploy database and messaging queues
    `ansible-playbook openstack_basic_database_messaging_single.yml`

#### To deploy kestone
    `ansible-playbook openstack_keystone.yml`