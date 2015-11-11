#!/usr/bin/env bash
# Example script

# install playback
sudo pip install playback

# setup networking
playback-nic --purge --public --user ubuntu --host 192.169.150.19 --nic eth1 --address 192.169.151.19 --netmask 255.255.255.0 --gateway 192.169.151.1 --dns-nameservers "192.169.11.11 192.169.11.12"
playback-nic --user ubuntu --host 192.169.150.19 --private --nic eth2 --address 192.168.1.12 --netmask 255.255.255.0
playback-nic --user ubuntu --host 192.169.150.19 --restart
playback-nic --purge --public --user ubuntu --host 192.169.150.17 --nic eth1 --address 192.169.151.17 --netmask 255.255.255.0 --gateway 192.169.151.1 --dns-nameservers "192.169.11.11 192.169.11.12"
playback-nic --user ubuntu --host 192.169.150.17 --private --nic eth2 --address 192.168.1.13 --netmask 255.255.255.0
playback-nic --user ubuntu --host 192.169.150.17 --restart
playback-nic --purge --public --user ubuntu --host 192.169.150.16 --nic eth1 --address 192.169.151.16 --netmask 255.255.255.0 --gateway 192.169.151.1 --dns-nameservers "192.169.11.11 192.169.11.12"
playback-nic --user ubuntu --host 192.169.150.16 --private --nic eth2 --address 192.168.1.14 --netmask 255.255.255.0
playback-nic --user ubuntu --host 192.169.150.16 --restart
playback-nic --purge --public --user ubuntu --host 192.169.150.22 --nic eth1 --address 192.169.151.22 --netmask 255.255.255.0 --gateway 192.169.151.1 --dns-nameservers "192.169.11.11 192.169.11.12"
playback-nic --user ubuntu --host 192.169.150.22 --private --nic eth2 --address 192.168.1.20 --netmask 255.255.255.0
playback-nic --user ubuntu --host 192.169.150.22 --restart
playback-nic --purge --public --user ubuntu --host 192.169.150.18 --nic eth1 --address 192.169.151.18 --netmask 255.255.255.0 --gateway 192.169.151.1 --dns-nameservers "192.169.11.11 192.169.11.12"
playback-nic --user ubuntu --host 192.169.150.18 --private --nic eth2 --address 192.168.1.18 --netmask 255.255.255.0
playback-nic --user ubuntu --host 192.169.150.18 --restart
playback-nic --purge --public --user ubuntu --host 192.169.150.25 --nic eth1 --address 192.169.151.25 --netmask 255.255.255.0 --gateway 192.169.151.1 --dns-nameservers "192.169.11.11 192.169.11.12"
playback-nic --user ubuntu --host 192.169.150.25 --private --nic eth2 --address 192.168.1.17 --netmask 255.255.255.0
playback-nic --user ubuntu --host 192.169.150.25 --restart
playback-nic --purge --public --user ubuntu --host 192.169.150.12 --nic eth1 --address 192.169.151.12 --netmask 255.255.255.0 --gateway 192.169.151.1 --dns-nameservers "192.169.11.11 192.169.11.12"
playback-nic --user ubuntu --host 192.169.150.12 --private --nic eth2 --address 192.168.1.16 --netmask 255.255.255.0
playback-nic --user ubuntu --host 192.169.150.12 --restart
playback-nic --purge --public --user ubuntu --host 192.169.150.14 --nic eth1 --address 192.169.151.14 --netmask 255.255.255.0 --gateway 192.169.151.1 --dns-nameservers "192.169.11.11 192.169.11.12"
playback-nic --user ubuntu --host 192.169.150.14 --private --nic eth2 --address 192.168.1.15 --netmask 255.255.255.0
playback-nic --user ubuntu --host 192.169.150.14 --restart

# init playback config
playback --init
cd .playback

# deploy haproxy and keepalived
playback --ansible  'openstack_haproxy.yml --extra-vars "host=lb01 router_id=lb01 state=MASTER priority=150" -vvvv'
playback --ansible 'openstack_haproxy.yml --extra-vars "host=lb02 router_id=lb02 state=SLAVE priority=100" -vvvv'

# prepare OpenStack environment
playback --ansible 'openstack_basic_environment.yml -vvvv'

# deploy db
playback --ansible 'openstack_mariadb.yml --extra-vars "host=controller01 my_ip=192.169.151.19" -vvvv'
playback --ansible 'openstack_mariadb.yml --extra-vars "host=controller02 my_ip=192.169.151.17" -vvvv'
python keepalived.py

# install rabbit
ssh ubuntu@192.169.151.19 'echo "192.169.151.17 controller02" | sudo tee -a /etc/hosts'
ssh ubuntu@192.169.151.17 'echo "192.169.151.19 controller01" | sudo tee -a /etc/hosts'
playback --ansible 'openstack_rabbitmq.yml --extra-vars "host=controller01" -vvvv'
playback --ansible 'openstack_rabbitmq.yml --extra-vars "host=controller02" -vvvv'


# install keystone
playback --ansible 'openstack_keystone.yml --extra-vars "host=controller01" -vvvv'
playback --ansible 'openstack_keystone.yml --extra-vars "host=controller02" -vvvv'

# format disk for swift storage
playback --ansible 'openstack_storage_partitions.yml --extra-vars "host=compute05" -vvvv'
playback --ansible 'openstack_storage_partitions.yml --extra-vars "host=compute06" -vvvv'

# install swift storage
playback --ansible 'openstack_swift_storage.yml --extra-vars "host=compute05 my_storage_ip=192.168.1.16" -vvvv'
playback --ansible 'openstack_swift_storage.yml --extra-vars "host=compute06 my_storage_ip=192.168.1.15" -vvvv'

# install swift proxy
playback --ansible 'openstack_swift_proxy.yml --extra-vars "host=controller01" -vvvv'
playback --ansible 'openstack_swift_proxy.yml --extra-vars "host=controller02" -vvvv'

# init swift rings
playback --ansible 'openstack_swift_add_node_to_the_ring.yml --extra-vars "swift_storage_storage_ip=192.168.1.16 device_name=sdb1 device_weight=100" -vvvv'
playback --ansible 'openstack_swift_add_node_to_the_ring.yml --extra-vars "swift_storage_storage_ip=192.168.1.16 device_name=sdc1 device_weight=100" -vvvv'
playback --ansible 'openstack_swift_add_node_to_the_ring.yml --extra-vars "swift_storage_storage_ip=192.168.1.15 device_name=sdb1 device_weight=100" -vvvv'
playback --ansible 'openstack_swift_add_node_to_the_ring.yml --extra-vars "swift_storage_storage_ip=192.168.1.15 device_name=sdc1 device_weight=100" -vvvv'
playback --ansible 'openstack_swift_rebalance_ring.yml -vvvv'


# copy swift builder file
scp ubuntu@192.169.151.19:/etc/swift/*.gz patch/
scp patch/*.gz ubuntu@192.169.151.17:~
scp patch/*.gz ubuntu@192.169.151.12:~
scp patch/*.gz ubuntu@192.169.151.14:~

ssh ubuntu@192.169.151.17 sudo cp *.gz /etc/swift
ssh ubuntu@192.169.151.12 sudo cp *.gz /etc/swift
ssh ubuntu@192.169.151.14 sudo cp *.gz /etc/swift


# finalize swift deployment
playback --ansible 'openstack_swift_finalize_installation.yml --extra-vars "hosts=swift_proxy" -vvvv'
playback --ansible 'openstack_swift_finalize_installation.yml --extra-vars "hosts=swift_storage" -vvvv'

# install glance
playback --ansible 'openstack_glance.yml --extra-vars "host=controller01" -vvvv'
playback --ansible 'openstack_glance.yml --extra-vars "host=controller02" -vvvv'

# install ceph admin
ssh ubuntu@192.169.151.19 ssh-keygen
scp ubuntu@192.169.151.19:~/.ssh/id_rsa.pub patch/
scp ubuntu@192.169.151.19:~/.ssh/id_rsa patch/
ssh-copy-id -i patch/id_rsa.pub ubuntu@192.169.151.19
ssh-copy-id -i patch/id_rsa.pub ubuntu@192.169.151.17
ssh-copy-id -i patch/id_rsa.pub ubuntu@192.169.151.16
ssh-copy-id -i patch/id_rsa.pub ubuntu@192.169.151.22
ssh-copy-id -i patch/id_rsa.pub ubuntu@192.169.151.18
ssh-copy-id -i patch/id_rsa.pub ubuntu@192.169.151.25
ssh-copy-id -i patch/id_rsa.pub ubuntu@192.169.151.12
ssh-copy-id -i patch/id_rsa.pub ubuntu@192.169.151.14
playback --ansible 'openstack_ceph_admin.yml -vvvv'

# init ceph monitor
ssh ubuntu@192.169.151.19 'echo "192.169.151.19 controller01" | sudo tee -a /etc/hosts'
ssh ubuntu@192.169.151.19 'echo "192.169.151.16 compute01" | sudo tee -a /etc/hosts'
ssh ubuntu@192.169.151.19 'echo "192.169.151.22 compute02" | sudo tee -a /etc/hosts'
ssh ubuntu@192.169.151.19 'echo "192.169.151.18 compute03" | sudo tee -a /etc/hosts'
ssh ubuntu@192.169.151.19 'echo "192.169.151.25 compute04" | sudo tee -a /etc/hosts'
ssh ubuntu@192.169.151.19 'echo "192.169.151.12 compute05" | sudo tee -a /etc/hosts'
ssh ubuntu@192.169.151.19 'echo "192.169.151.14 compute06" | sudo tee -a /etc/hosts'
playback --ansible 'openstack_ceph_initial_mon.yml -vvvv'


# deploy ceph clients
ssh ubuntu@192.169.151.19 'ssh -o "StrictHostKeyChecking no" ubuntu@controller01 true'
ssh ubuntu@192.169.151.19 'ssh -o "StrictHostKeyChecking no" ubuntu@controller02 true'
ssh ubuntu@192.169.151.19 'ssh -o "StrictHostKeyChecking no" ubuntu@compute01 true'
ssh ubuntu@192.169.151.19 'ssh -o "StrictHostKeyChecking no" ubuntu@compute02 true'
ssh ubuntu@192.169.151.19 'ssh -o "StrictHostKeyChecking no" ubuntu@compute03 true'
ssh ubuntu@192.169.151.19 'ssh -o "StrictHostKeyChecking no" ubuntu@compute04 true'
ssh ubuntu@192.169.151.19 'ssh -o "StrictHostKeyChecking no" ubuntu@compute05 true'
ssh ubuntu@192.169.151.19 'ssh -o "StrictHostKeyChecking no" ubuntu@compute06 true'
playback --ansible 'openstack_ceph_client.yml --extra-vars "client=controller01" -vvvv'
playback --ansible 'openstack_ceph_client.yml --extra-vars "client=controller02" -vvvv'
playback --ansible 'openstack_ceph_client.yml --extra-vars "client=compute01" -vvvv'
playback --ansible 'openstack_ceph_client.yml --extra-vars "client=compute02" -vvvv'
playback --ansible 'openstack_ceph_client.yml --extra-vars "client=compute03" -vvvv'
playback --ansible 'openstack_ceph_client.yml --extra-vars "client=compute04" -vvvv'
playback --ansible 'openstack_ceph_client.yml --extra-vars "client=compute05" -vvvv'
playback --ansible 'openstack_ceph_client.yml --extra-vars "client=compute06" -vvvv'

# generate ceph keys
playback --ansible 'openstack_ceph_gather_keys.yml -vvvv'


# add ceph osds
playback --ansible 'openstack_ceph_osd.yml --extra-vars "node=compute01 disk=sdb partition=sdb1" -vvvv'
playback --ansible 'openstack_ceph_osd.yml --extra-vars "node=compute01 disk=sdc partition=sdc1" -vvvv'
playback --ansible 'openstack_ceph_osd.yml --extra-vars "node=compute02 disk=sdb partition=sdb1" -vvvv'
playback --ansible 'openstack_ceph_osd.yml --extra-vars "node=compute02 disk=sdc partition=sdc1" -vvvv'
playback --ansible 'openstack_ceph_osd.yml --extra-vars "node=compute03 disk=sdb partition=sdb1" -vvvv'
playback --ansible 'openstack_ceph_osd.yml --extra-vars "node=compute03 disk=sdc partition=sdc1" -vvvv'
playback --ansible 'openstack_ceph_osd.yml --extra-vars "node=compute04 disk=sdb partition=sdb1" -vvvv'
playback --ansible 'openstack_ceph_osd.yml --extra-vars "node=compute04 disk=sdc partition=sdc1" -vvvv'

# add ceph monitors
playback --ansible 'openstack_ceph_mon.yml --extra-vars "node=compute01" -vvvv'
playback --ansible 'openstack_ceph_mon.yml --extra-vars "node=compute02" -vvvv'
playback --ansible 'openstack_ceph_mon.yml --extra-vars "node=compute03" -vvvv'
playback --ansible 'openstack_ceph_mon.yml --extra-vars "node=compute04" -vvvv'

# copy the Ceph keys to every nodes
playback --ansible 'openstack_ceph_copy_keys.yml --extra-vars "node=controller01" -vvvv'
playback --ansible 'openstack_ceph_copy_keys.yml --extra-vars "node=controller02" -vvvv'
playback --ansible 'openstack_ceph_copy_keys.yml --extra-vars "node=compute01" -vvvv'
playback --ansible 'openstack_ceph_copy_keys.yml --extra-vars "node=compute02" -vvvv'
playback --ansible 'openstack_ceph_copy_keys.yml --extra-vars "node=compute03" -vvvv'
playback --ansible 'openstack_ceph_copy_keys.yml --extra-vars "node=compute04" -vvvv'
playback --ansible 'openstack_ceph_copy_keys.yml --extra-vars "node=compute05" -vvvv'
playback --ansible 'openstack_ceph_copy_keys.yml --extra-vars "node=compute06" -vvvv'

# create the cinder ceph user and pool name
playback --ansible 'openstack_ceph_cinder_pool_user.yml -vvvv'

# deploy cinder-api
playback --ansible 'openstack_cinder_api.yml --extra-vars "host=controller01" -vvvv'
playback --ansible 'openstack_cinder_api.yml --extra-vars "host=controller02" -vvvv'

# install cinder-volume
playback --ansible 'openstack_cinder_volume_ceph.yml --extra-vars "host=controller01" -vvvv'
playback --ansible 'openstack_cinder_volume_ceph.yml --extra-vars "host=controller02" -vvvv'

# copy the ceph.client.cinder.keyring from ceph-admin node to /etc/ceph/ceph.client.cinder.keyring of cinder volume nodes and nova-compute nodes to using the ceph client.
ssh ubuntu@192.169.151.19 'ceph auth get-or-create client.cinder | ssh ubuntu@controller01 sudo tee /etc/ceph/ceph.client.cinder.keyring'
ssh ubuntu@192.169.151.19 'ceph auth get-or-create client.cinder | ssh ubuntu@controller02 sudo tee /etc/ceph/ceph.client.cinder.keyring'
ssh ubuntu@192.169.151.19 'ceph auth get-or-create client.cinder | ssh ubuntu@compute01 sudo tee /etc/ceph/ceph.client.cinder.keyring'
ssh ubuntu@192.169.151.19 'ceph auth get-or-create client.cinder | ssh ubuntu@compute02 sudo tee /etc/ceph/ceph.client.cinder.keyring'
ssh ubuntu@192.169.151.19 'ceph auth get-or-create client.cinder | ssh ubuntu@compute03 sudo tee /etc/ceph/ceph.client.cinder.keyring'
ssh ubuntu@192.169.151.19 'ceph auth get-or-create client.cinder | ssh ubuntu@compute04 sudo tee /etc/ceph/ceph.client.cinder.keyring'
ssh ubuntu@192.169.151.19 'ceph auth get-or-create client.cinder | ssh ubuntu@compute05 sudo tee /etc/ceph/ceph.client.cinder.keyring'
ssh ubuntu@192.169.151.19 'ceph auth get-or-create client.cinder | ssh ubuntu@compute06 sudo tee /etc/ceph/ceph.client.cinder.keyring'


# restart volume service dependency to take effect for ceph backend
echo '192.169.151.19 controller01' | sudo tee -a /etc/hosts
echo '192.169.151.17 controller02' | sudo tee -a /etc/hosts
python restart_cindervol_deps.py ubuntu@controller01 ubuntu@controller02

# deploy nova controller
playback --ansible 'openstack_compute_controller.yml --extra-vars "host=controller01" -vvvv'
playback --ansible 'openstack_compute_controller.yml --extra-vars "host=controller02" -vvvv'

# add dashboard
playback --ansible 'openstack_horizon.yml -vvvv'

# deploy nova compute
playback --ansible 'openstack_compute_node.yml --extra-vars "host=compute01 my_ip=192.169.151.16" -vvvv'
playback --ansible 'openstack_compute_node.yml --extra-vars "host=compute02 my_ip=192.169.151.22" -vvvv'
playback --ansible 'openstack_compute_node.yml --extra-vars "host=compute03 my_ip=192.169.151.18" -vvvv'
playback --ansible 'openstack_compute_node.yml --extra-vars "host=compute04 my_ip=192.169.151.25" -vvvv'
playback --ansible 'openstack_compute_node.yml --extra-vars "host=compute05 my_ip=192.169.151.12" -vvvv'
playback --ansible 'openstack_compute_node.yml --extra-vars "host=compute06 my_ip=192.169.151.14" -vvvv'

# install Legacy networking nova-network(FlatDHCP Only)
playback --ansible 'openstack_nova_network_compute.yml --extra-vars "host=compute01 my_ip=192.169.151.16" -vvvv'
playback --ansible 'openstack_nova_network_compute.yml --extra-vars "host=compute02 my_ip=192.169.151.22" -vvvv'
playback --ansible 'openstack_nova_network_compute.yml --extra-vars "host=compute03 my_ip=192.169.151.18" -vvvv'
playback --ansible 'openstack_nova_network_compute.yml --extra-vars "host=compute04 my_ip=192.169.151.25" -vvvv'
playback --ansible 'openstack_nova_network_compute.yml --extra-vars "host=compute05 my_ip=192.169.151.12" -vvvv'
playback --ansible 'openstack_nova_network_compute.yml --extra-vars "host=compute06 my_ip=192.169.151.14" -vvvv'


# create initial network. For example, using an exclusive slice of 172.16.0.0/16 with IP address range 172.16.0.1 to 172.16.255.254
ssh ubuntu@192.169.151.19 'sudo cp /root/admin-openrc.sh /home/ubuntu'
ssh ubuntu@192.169.151.19 'source ~/admin-openrc.sh && nova network-create ext-net --bridge br100 --multi-host T --fixed-range-v4 172.16.0.0/16'
ssh ubuntu@192.169.151.19 'source ~/admin-openrc.sh && nova floating-ip-bulk-create --pool ext-net 192.169.151.65/26'
ssh ubuntu@192.169.151.19 'source ~/admin-openrc.sh && nova floating-ip-bulk-list'

# extend the ext-net pool
ssh ubuntu@192.169.151.19 'source ~/admin-openrc.sh && nova floating-ip-bulk-create --pool ext-net 192.169.151.128/26'
ssh ubuntu@192.169.151.19 'source ~/admin-openrc.sh && nova floating-ip-bulk-create --pool ext-net 192.169.151.192/26'
ssh ubuntu@192.169.151.19 'source ~/admin-openrc.sh && nova floating-ip-bulk-list'

# deploy heat
playback --ansible 'openstack_heat_controller.yml --extra-vars "host=controller01" -vvvv'
playback --ansible 'openstack_heat_controller.yml --extra-vars "host=controller02" -vvvv'

# enable service auto start
python patch-autostart.py

# dns as a service
playback --ansible openstack_dns.yml


