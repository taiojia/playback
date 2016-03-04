# Playback
Playback is an OpenStack provisioning DevOps tool that all of the OpenStack components can be deployed automation with high availability on Ubuntu based operating system.

#### Requirement
The OpenStack bare metal hosts are in MAAS environment(recommend), and all hosts are two NICs at least(external and internal). 
We assume that you have ceph installed, the cinder bachend default using ceph, the running instace default to using ceph as it's local storage.
About ceph please visit: http://docs.ceph.com/docs/master/rbd/rbd-openstack/

#### Install Playback
Use pip:

    pip install playback

Or form source:

    git clone https://github.com/jiasir/playback.git
    cd playback
    git checkout liberty
    sudo python setup.py install

#### Prepare environment
Prepare the OpenStack environment.
DO NOT setup eth1 in /etc/network/interfaces

    playback-env --prepare-host --user ubuntu --hosts CONTROLLER1,CONTROLLER2,COMPUTE1,COMPUTE2,SOTRAGE1,STORAGE2,HAPROXY1,HAPROXY2

#### MySQL HA
Deploy to CONTROLLER1

    playback-mysql --install --user ubuntu --hosts CONTROLLER1
    playback-mysql --config --user ubuntu --hosts CONTROLLER1 --wsrep_cluster_address "gcomm://CONTROLLER1,CONTROLLER2" --wsrep_node_name="galera1" --wsrep_node_address="CONTROLLER1"

Deploy to CONTROLLER2

    playback-mysql --install --user ubuntu --hosts CONTROLLER2
    playback-mysql --config --user ubuntu --hosts CONTROLLER2 --wsrep_cluster_address "gcomm://CONTROLLER1,CONTROLLER2" --wsrep_node_name="galera2" --wsrep_node_address="CONTROLLER2"

Start cluster

    playback-mysql --user ubuntu --hosts CONTROLLER1 --manage --wsrep-new-cluster
    playback-mysql --user ubuntu --hosts CONTROLLER2 --manage --start
    playback-mysql --user ubuntu --hosts CONTROLLER1 --manage --change-root-password changeme

#### HAProxy HA
Deploy to HAPROXY1

    playback-haproxy --install --user ubuntu --hosts HAPROXY1

Deploy to HAPROXY2

    playback-haproxy --install --user ubuntu --hosts HAPROXY2

Generate the HAProxy configuration and upload to target hosts(Do not forget to edit the generated configuration)

    playback-haproxy --gen-conf 
    playback-haproxy --config --upload-conf haproxy.cfg --user ubuntu --hosts HAPROXY1,HAPROXY2

Configure Keepalived

    playback-haproxy --config --configure-keepalived --router_id lb1 --priority 150 --state MASTER --interface eth0 --vip CONTROLLER_VIP --user ubuntu --hosts HAPROXY1
    playback-haproxy --config --configure-keepalived --router_id lb2 --priority 100 --state SLAVE --interface eth0 --vip CONTROLLER_VIP --user ubuntu --hosts HAPROXY2

#### RabbitMQ HA
Deploy to CONTROLLER1 and CONTROLLER2

    playback-rabbitmq --install --user ubuntu --hosts CONTROLLER1,CONTROLLER2 --erlang-cookie changemechangeme --rabbit-user openstack --rabbit-pass changeme
    
Create cluster

    playback-rabbitmq --user ubuntu --hosts CONTROLLER2 --join-cluster rabbit@CONTROLLER1

#### Keystone HA
Create keystone database

    playback-keystone --user ubuntu --hosts CONTROLLER1 --create-keystone-db --root-db-pass changeme --keystone-db-pass changeme

Install keystone on CONTROLLER1 and CONTROLLER2

    playback-keystone --user ubuntu --hosts CONTROLLER1 --install --admin_token changeme --connection mysql+pymysql://keystone:changeme@CONTROLLER_VIP/keystone --memcache_servers CONTROLLER1:11211,CONTROLLER2:11211 --populate
    playback-keystone --user ubuntu --hosts CONTROLLER2 --install --admin_token changeme --connection mysql+pymysql://keystone:changeme@CONTROLLER_VIP/keystone --memcache_servers CONTROLLER1:11211,CONTROLLER2:11211

Create the service entity and API endpoints

    playback-keystone --user ubuntu --hosts CONTROLLER1 --create-entity-and-endpoint --os-token changeme --os-url http://CONTROLLER_VIP:35357/v3 --public-endpoint http://CONTROLLER_VIP:5000/v2.0 --internal-endpoint http://CONTROLLER_VIP:5000/v2.0 --admin-endpoint http://CONTROLLER_vip:35357/v2.0

Create projects, users, and roles

    playback-keystone --user ubuntu --hosts CONTROLLER1 --create-projects-users-roles --os-token changeme --os-url http://CONTROLLER_VIP:35357/v3 --admin-pass changeme --demo-pass changeme

(OPTION) you will need to create OpenStack client environment scripts
admin-openrc.sh

    export OS_PROJECT_DOMAIN_ID=default
    export OS_USER_DOMAIN_ID=default
    export OS_PROJECT_NAME=admin
    export OS_TENANT_NAME=admin
    export OS_USERNAME=admin
    export OS_PASSWORD=changeme
    export OS_AUTH_URL=http://CONTROLLER_VIP:35357/v3
    export OS_IDENTITY_API_VERSION=3
    export OS_IMAGE_API_VERSION=2
    export OS_AUTH_VERSION=3

demo-openrc.sh

    export OS_PROJECT_DOMAIN_ID=default
    export OS_USER_DOMAIN_ID=default
    export OS_PROJECT_NAME=demo
    export OS_TENANT_NAME=demo
    export OS_USERNAME=demo
    export OS_PASSWORD=changeme
    export OS_AUTH_URL=http://CONTROLLER_VIP:5000/v3
    export OS_IDENTITY_API_VERSION=3
    export OS_IMAGE_API_VERSION=2
    export OS_AUTH_VERSION=3

#### Glance HA
Create glance database

    playback-glance --user ubuntu --hosts CONTROLLER1 --create-glance-db --root-db-pass changeme --glance-db-pass changeme

Create service credentials

    playback-glance --user ubuntu --hosts CONTROLLER1 --create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --glance-pass changeme --endpoint http://CONTROLLER_VIP:9292

Install glance on CONTROLLER1 and CONTROLLER2

    playback-glance --user ubuntu --hosts CONTROLLER1 --install --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme  --swift-store-auth-address http://CONTROLLER_VIP:5000/v2.0/ --populate
    playback-glance --user ubuntu --hosts CONTROLLER2 --install --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme  --swift-store-auth-address http://CONTROLLER_VIP:5000/v2.0/ 


#### Nova HA
Create nova database

    playback-nova --user ubuntu --hosts CONTROLLER1 --create-nova-db --root-db-pass changeme --nova-db-pass changeme 

Create service credentials

    playback-nova --user ubuntu --hosts CONTROLLER1 --create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --nova-pass changeme --endpoint 'http://CONTROLLER_VIP:8774/v2/%\(tenant_id\)s'

Install nova on CONTROLLER1

    playback-nova --user ubuntu --hosts CONTROLLER1 --install --connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --my-ip MANAGEMENT_IP --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-pass changeme --glance-host CONTROLLER_VIP --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --metadata-proxy-shared-secret changeme --populate

Install nova on CONTROLLER2

    playback-nova --user ubuntu --hosts CONTROLLER2 --install --connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --my-ip MANAGEMENT_IP --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-pass changeme --glance-host CONTROLLER_VIP --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --metadata-proxy-shared-secret changeme

#### Nova Compute
Add nova computes

    playback-nova-compute --user ubuntu --hosts COMPUTE1 --install --my-ip MANAGEMENT_IP --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --novncproxy-base-url http://CONTROLLER_VIP:6080/vnc_auto.html --glance-host CONTROLLER_VIP --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --rbd-secret-uuid changeme-changeme-changeme-changeme
    playback-nova-compute --user ubuntu --hosts COMPUTE2 --install --my-ip MANAGEMENT_IP --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --novncproxy-base-url http://CONTROLLER_VIP:6080/vnc_auto.html --glance-host CONTROLLER_VIP --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --rbd-secret-uuid changeme-changeme-changeme-changeme

The libvirt defaults to using ceph as shared storage, the ceph pool for running instance is vms. if you do not using ceph as it's bachend, you must remove the following param:
    
    images_type = rbd
    images_rbd_pool = vms
    images_rbd_ceph_conf = /etc/ceph/ceph.conf
    rbd_user = cinder
    rbd_secret_uuid = changeme-changeme-changeme-changeme
    disk_cachemodes="network=writeback"
    live_migration_flag="VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_LIVE,VIR_MIGRATE_PERSIST_DEST,VIR_MIGRATE_TUNNELLED"


#### Neutron HA
Create nova database

    playback-neutron --user ubuntu --hosts CONTROLLER1 --create-neutron-db --root-db-pass changeme --neutron-db-pass changeme 

Create service credentials

    playback-neutron --user ubuntu --hosts CONTROLLER1 --create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --neutron-pass changeme --endpoint http://CONTROLLER_VIP:9696

Install Neutron for self-service

    playback-neutron --user ubuntu --hosts CONTROLLER1 --install --connection mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --nova-url http://CONTROLLER_VIP:8774/v2 --nova-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP --nova-metadata-ip CONTROLLER_VIP --metadata-proxy-shared-secret changeme-changeme-changeme-changeme --populate
    playback-neutron --user ubuntu --hosts CONTROLLER2 --install --connection mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --nova-url http://CONTROLLER_VIP:8774/v2 --nova-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP --nova-metadata-ip CONTROLLER_VIP --metadata-proxy-shared-secret changeme-changeme-changeme-changeme 


#### Neutron Agent
Install neutron agent on compute nodes
    
    playback-neutron-agent --user ubuntu --hosts COMPUTE1 --install --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP 
    playback-neutron-agent --user ubuntu --hosts COMPUTE2 --install --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP 


#### Horizon HA
Install horizon on controller nodes

    playback-horizon --user ubuntu --hosts CONTROLLER1,CONTROLLER2 --install --openstack-host CONTROLLER_VIP  --memcache CONTROLLER1:11211 --time-zone Asia/Shanghai 


#### Cinder HA
Create cinder database

    playback-cinder --user ubuntu --hosts CONTROLLER1 --create-cinder-db --root-db-pass changeme --cinder-db-pass changeme 

Create cinder service creadentials

    playback-cinder --user ubuntu --hosts CONTROLLER1 --create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --cinder-pass changeme --endpoint-v1 'http://CONTROLLER_VIP:8776/v1/%\(tenant_id\)s' --endpoint-v2 'http://CONTROLLER_VIP:8776/v2/%\(tenant_id\)s'

Install cinder-api and cinder-volume on controller nodes, the volume backend defaults to ceph (you must have ceph installed)
    
    playback-cinder --user ubuntu --hosts CONTROLLER1 --install --connection mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder --rabbit-pass changeme --rabbit-hosts CONTROLLER1,CONTROLLER2 --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --cinder-pass changeme --my-ip MANAGEMENT_INTERFACE_IP --glance-host CONTROLLER_VIP --rbd-secret-uuid changeme-changeme-changeme-changeme --populate
    playback-cinder --user ubuntu --hosts CONTROLLER2 --install --connection mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder --rabbit-pass changeme --rabbit-hosts CONTROLLER1,CONTROLLER2 --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --cinder-pass changeme --my-ip MANAGEMENT_INTERFACE_IP --glance-host CONTROLLER_VIP --rbd-secret-uuid changeme-changeme-changeme-changeme

#### Swift proxy HA
Create the Identity service credentials

    playback-swift --user ubuntu --hosts CONTROLLER1 --create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --swift-pass changeme --public-internal-endpoint 'http://CONTROLLER_VIP:8080/v1/AUTH_%\(tenant_id\)s' --admin-endpoint http://CONTROLLER_VIP:8080/v1 

Install swift proxy

    playback-swift --user ubuntu --hosts CONTROLLER1,CONTROLLER2 --install --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --swift-pass changeme --memcache-servers CONTROLLER1:11211,CONTROLLER2:11211 


#### Swift storage
Prepare disks on storage node

    playback-swift-storage --user ubuntu --hosts STORAGE1,STORAGE2 --prepare-disks sdb,sdc,sdd,sde

Install swift storage on storage node

    playback-swift-storage --user ubuntu --hosts STORAGE1 --install --address MANAGEMENT_INTERFACE_IP --bind-ip MANAGEMENT_INTERFACE_IP 
    playback-swift-storage --user ubuntu --hosts STORAGE2 --install --address MANAGEMENT_INTERFACE_IP --bind-ip MANAGEMENT_INTERFACE_IP 

Create account ring on controller node

    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --create-account-builder-file --partitions 10 --replicas 3 --moving 1 
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --account-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sdb --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --account-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sdc --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --account-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sdd --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --account-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sde --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --account-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sdb --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --account-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sdc --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --account-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sdd --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --account-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sde --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --account-builder-rebalance
Create container ring on controller node
    
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --create-container-builder-file --partitions 10 --replicas 3 --moving 1 
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --container-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sdb --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --container-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sdc --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --container-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sdd --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --container-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sde --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --container-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sdb --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --container-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sdc --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --container-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sdd --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --container-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sde --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --container-builder-rebalance

Create object ring on controller node
    
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --create-object-builder-file --partitions 10 --replicas 3 --moving 1 
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --object-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sdb --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --object-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sdc --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --object-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sdd --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --object-builder-add --region 1 --zone 1 --ip STORAGE1_MANAGEMENT_IP --device sde --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --object-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sdb --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --object-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sdc --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --object-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sdd --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --object-builder-add --region 1 --zone 1 --ip STORAGE2_MANAGEMENT_IP --device sde --weight 100
    playback-swift-storage --user ubuntu --hosts CONTROLLER1 --object-builder-rebalance

 Sync the builder file from controller node to each storage node and other any proxy node

    playback-swift-storage --user ubuntu --host CONTROLLER1 --sync-builder-file --to CONTROLLER2,STORAGE1,STORAGE2

Finalize installation on all nodes

    playback-swift --user ubuntu --hosts CONTROLLER1,CONTROLLER2,STORAGE1,STORAGE2 --finalize-install --swift-hash-path-suffix changeme --swift-hash-path-prefix changeme



TODO:

    deploy ceph
    configuare ceph for nova
    nova ssh keys
    esxi backend
    
