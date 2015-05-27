# Playback
Playback is an OpenStack provisioning DevOps tool that all of the OpenStack components can be deployed automation with high availability.

### Getting Started

#### Setup playback
    
    git clone https://github.com/jiasir/playback.git
    cd playback
    python setup.py install
    
#### Setting your testing environment if you want
You must have the Vagrant installed and than you can provision  the testing environment, the test node you can see `Vagrantfile` at `examples`.

    cd examples
    vagrant up
 
    
#### Define a inventory file
The inventory file at `inventory/inventory`, the default setting is the Vagrant testing node. You can according to your environment to change parameters.

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

    [glance]
    controller1 ansible_ssh_host=172.16.33.4

    [compute_controller]
    controller1 ansible_ssh_host=172.16.33.4

    [compute_node]
    compute1 ansible_ssh_host=172.16.33.7

    [neutron_controller]
    controller1 ansible_ssh_host=172.16.33.4

    [neutron_node]
    network ansible_ssh_host=172.16.33.6

    [neutron_compute]
    compute1 ansible_ssh_host=172.16.33.7

    [horizon]
    controller1 ansible_ssh_host=172.16.33.4

    [cinder_controller]
    controller1 ansible_ssh_host=172.16.33.4

    [cinder_storage]
    storage1 ansible_ssh_host=172.16.33.5

    [swift_proxy]
    controller1 ansible_ssh_host=172.16.33.4

    [swift_storage]
    swiftstore1 ansible_ssh_host=172.16.33.8
    swiftstore2 ansible_ssh_host=172.16.33.9
    swiftstore3 ansible_ssh_host=172.16.33.10


    
#### To define your variables in vars/openstack
The `vars/openstack/openstack.yml` is all the parameters.
* openstack.yml

#### To deploy OpenStack Basic environment including NTP and OpenStack repository
    playback openstack_basic_environment.yml

#### To deploy database and messaging queues
    playback openstack_basic_database_messaging_single.yml

#### To deploy Keystone
    playback openstack_keystone.yml
    
#### To deploy Glance
The Glance default store is file.
    
    playback openstack_glance.yml

#### To deploy a compute controller
    playback openstack_compute_controller.yml
    
#### To deploy compute nodes
    playback openstack_compute_node.yml --extra-vars \"compute_name=compute1 compute_ip=172.16.33.7\"
    
#### To deploy a neutron controller
    playback openstack_neutron_controller.yml --extra-vars \"nova_admin_service_tenant_id=6aea60400e6246edaa83d508b222d2eb\"

###### To obtain the service tenant identifier (id) at the controller
        $ source admin-openrc.sh
        $ keystone tenant-get service
        +-------------+----------------------------------+
        |   Property  |              Value               |
        +-------------+----------------------------------+
        | description |          Service Tenant          |
        |   enabled   |               True               |
        |      id     | 6aea60400e6246edaa83d508b222d2eb |
        |     name    |             service              |
        +-------------+----------------------------------+
### To deploy a neutron node
    playback openstack_neutron_node.yml --extra-vars \"local_tunnel_net_ip=192.168.11.6\"

### To deploy a neutron compute
    playback openstack_neutron_compute.yml --extra-vars \"compute_name=compute1 compute_ip=172.16.33.7 local_tunnel_net_ip=192.168.11.7\"

### Initial networks
    playback openstack_initial_networks.yml

### Add Dashboard
    playback openstack_horizon.yml

### To deploy a cinder controller
    playback openstack_cinder_controller.yml

### To deploy a cinder storage
    playback openstack_cinder_storage.yml --extra-vars \"my_ip=172.16.33.5\"

### To deploy a swift proxy
    playback openstack_swift_controller.yml
    
### Format devices(sdb1 and sdc1)
Each of the swift nodes, /dev/sdb1 and /dev/sdc1, must contain a suitable partition table with one partition occupying the entire device. Although the Object Storage service supports any file system with extended attributes (xattr), testing and benchmarking indicate the best performance and reliability on XFS.

    playback openstack_storage_partitions.yml --extra-vars \"storage_name=compute01\" -vvvv

### To deploy a swift storage
    
    playback openstack_swift_node.yml --extra-vars \"swift_storage_name=swiftstore1 my_management_ip=172.16.33.8 my_storage_network_ip=172.16.44.8\"

### Initial swift rings
    playback openstack_swift_builder_file.yml
    playback openstack_swift_add_node_to_the_ring.yml --extra-vars \"swift_storage_mgmt_ip=172.16.33.8 device_name=sdb1 device_weight=100\"
    playback openstack_swift_add_node_to_the_ring.yml --extra-vars \"swift_storage_mgmt_ip=172.16.33.8 device_name=sdc1 device_weight=100\"
    playback openstack_swift_add_node_to_the_ring.yml --extra-vars \"swift_storage_mgmt_ip=172.16.33.9 device_name=sdb1 device_weight=100\"
    playback openstack_swift_add_node_to_the_ring.yml --extra-vars \"swift_storage_mgmt_ip=172.16.33.9 device_name=sdc1 device_weight=100\"
    playback openstack_swift_add_node_to_the_ring.yml --extra-vars \"swift_storage_mgmt_ip=172.16.33.10 device_name=sdb1 device_weight=100\"
    playback openstack_swift_add_node_to_the_ring.yml --extra-vars \"swift_storage_mgmt_ip=172.16.33.10 device_name=sdc1 device_weight=100\"
    playback openstack_swift_rebalance_ring.yml
    
### Distribute ring configuration files
Copy the `account.ring.gz`, `container.ring.gz`, and `object.ring.gz` files to the `/etc/swift` directory on each storage node and any additional nodes running the proxy service.

### Finalize swift installation
    playback openstack_swift_finalize_installation.yml --extra-vars \"hosts=swift_proxy\"
    playback openstack_swift_finalize_installation.yml --extra-vars \"hosts=swift_storage\"

### Switch glance backend
Switch glance backend to swift
    
    playback openstack_switch_glance_backend_to_swift.yml
    
Switch glance backend to file
    
    playback openstack_switch_glance_backend_to_file.yml
    
### To deploy the Orchestration components(heat)
     playback openstack_heat_controller.yml
     
    