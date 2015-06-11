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
    
#### To deploy a neutron controller(GRE Only)
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
### To deploy a neutron node(GRE Only)
    playback openstack_neutron_node.yml --extra-vars \"local_tunnel_net_ip=192.168.11.6\"

### To deploy a neutron compute(GRE Only)
    playback openstack_neutron_compute.yml --extra-vars \"compute_name=compute1 compute_ip=172.16.33.7 local_tunnel_net_ip=192.168.11.7\"

### Initial networks(GRE Only)
    playback openstack_initial_networks.yml

### Add Dashboard
    playback openstack_horizon.yml

### To deploy a cinder controller
    playback openstack_cinder_controller.yml

### To deploy a cinder-volume on each cinder storage node (LVM Only)
    playback openstack_cinder_volume_lvm.yml --extra-vars \"my_ip=172.16.33.5\"

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
     
### To deploy the Ceph admin node
Ensure the admin node must be have password-less SSH access to Ceph nodes. When ceph-deploy logs in to a Ceph node as a user, that particular user must have passwordless sudo privileges.

Each Ceph node have the ceph user

    adduser ceph
    echo ceph ALL = \(root\) NOPASSWD:ALL | sudo tee /etc/sudoers.d/ceph
    sudo chmod 0440 /etc/sudoers.d/ceph

Copy SSH public key to each Ceph node from Ceph admin node
    
    ssh-keygen
    ssh-copy-id ceph@node

Deploy the Ceph admin node

    playback openstack_ceph_admin.yml -u ceph

### To deploy the Ceph initial monitor
    playback openstack_ceph_initial_mon.yml -u ceph
    
### To deploy the Ceph clients
    playback openstack_ceph_client.yml -u username --extra-vars \"client=maas\"
    playback openstack_ceph_client.yml -u username --extra-vars \"client=compute01\"
    playback openstack_ceph_client.yml -u username --extra-vars \"client=compute02\"
    playback openstack_ceph_client.yml -u username --extra-vars \"client=compute03\"
    playback openstack_ceph_client.yml -u username --extra-vars \"client=compute04\"
    playback openstack_ceph_client.yml -u username --extra-vars \"client=compute05\"
    playback openstack_ceph_client.yml -u username --extra-vars \"client=controller01\"
    playback openstack_ceph_client.yml -u username --extra-vars \"client=controller02\"

### To add Ceph initial monitor(s) and gather the keys
    playback openstack_ceph_gather_keys.yml -u ceph

### To add Ceph OSDs
    playback openstack_ceph_osd.yml -u ceph --extra-vars \"node=compute01 disk=sdb partition=sdb1\"
    playback openstack_ceph_osd.yml -u ceph --extra-vars \"node=compute01 disk=sdc partition=sdc1\"
    playback openstack_ceph_osd.yml -u ceph --extra-vars \"node=compute02 disk=sdb partition=sdb1\"
    playback openstack_ceph_osd.yml -u ceph --extra-vars \"node=compute02 disk=sdc partition=sdc1\"
    playback openstack_ceph_osd.yml -u ceph --extra-vars \"node=compute03 disk=sdb partition=sdb1\"
    playback openstack_ceph_osd.yml -u ceph --extra-vars \"node=compute03 disk=sdc partition=sdc1\"
    playback openstack_ceph_osd.yml -u ceph --extra-vars \"node=compute04 disk=sdb partition=sdb1\"
    playback openstack_ceph_osd.yml -u ceph --extra-vars \"node=compute04 disk=sdc partition=sdc1\"
    playback openstack_ceph_osd.yml -u ceph --extra-vars \"node=compute05 disk=sdb partition=sdb1\"
    playback openstack_ceph_osd.yml -u ceph --extra-vars \"node=compute05 disk=sdc partition=sdc1\"

### To add Ceph monitors
    playback openstack_ceph_mon.yml -u ceph --extra-vars \"node=compute01\"
    playback openstack_ceph_mon.yml -u ceph --extra-vars \"node=compute02\"
    playback openstack_ceph_mon.yml -u ceph --extra-vars \"node=compute03\"
    playback openstack_ceph_mon.yml -u ceph --extra-vars \"node=compute04\"
    playback openstack_ceph_mon.yml -u ceph --extra-vars \"node=compute05\"

### To copy the Ceph keys to nodes
Copy the configuration file and admin key to your admin node and your Ceph Nodes so that you can use the ceph CLI without having to specify the monitor address and ceph.client.admin.keyring each time you execute a command.
    
    playback openstack_ceph_copy_keys.yml -u ceph --extra-vars \"node=compute01\"
    playback openstack_ceph_copy_keys.yml -u ceph --extra-vars \"node=compute02\"
    playback openstack_ceph_copy_keys.yml -u ceph --extra-vars \"node=compute03\"
    playback openstack_ceph_copy_keys.yml -u ceph --extra-vars \"node=compute04\"
    playback openstack_ceph_copy_keys.yml -u ceph --extra-vars \"node=compute05\"
    playback openstack_ceph_copy_keys.yml -u ceph --extra-vars \"node=controller01\"
    playback openstack_ceph_copy_keys.yml -u ceph --extra-vars \"node=controller02\"
    
### Create the cinder ceph user and pool name
    playback openstack_ceph_cinder_pool_user.yml -u ceph
    
Copy the ceph.client.cinder.keyring from ceph-admin node to /etc/ceph/ceph.client.cinder.keyring of cinder volume node to using the ceph client.

    ssh ubuntu@controller01 sudo mkdir /etc/ceph
    ceph auth get-or-create client.cinder | ssh ubuntu@controller01 sudo tee /etc/ceph/ceph.client.cinder.keyring
    
### Install cinder-volume on controller node(Ceph Only)
    playback openstack_cinder_volume_ceph.yml

### Install Legacy networking nova-network(FlatDHCP Only)
    playback openstack_nova_network_controller.yml
    playback openstack_nova_network_compute.yml --extra-vars \"compute_name=compute1 compute_ip=172.16.33.7\"

Create initial network. For example, using an exclusive slice of 203.0.113.0/24 with IP address range 203.0.113.24 to 203.0.113.32:
    
    nova network-create demo-net --bridge br100 --multi-host T --fixed-range-v4 203.0.113.24/29
    nova floating-ip-bulk-create --pool demo-net 10.32.150.65/26
    nova floating-ip-bulk-list

Extend the demo-net pool:
    
    nova floating-ip-bulk-create --pool demo-net 10.32.150.129/26
    nova floating-ip-bulk-list
    
### Apt mirror
For maas nodes:

    playback openstack_maas_apt_mirror.yml

For cloud instances:

    playback openstack_cloud_apt_mirror.yml
    