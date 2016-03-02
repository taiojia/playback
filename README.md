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

    playback-env --prepare-host --user ubuntu --hosts os02.node,os03.node,os04.node,os05.node,os06.node,os07.node,os08.node,os09.node,os10.node,os11.node,os12.node,os13.node,os14.node,os15.node,os16.node,os18.node,os19.node

#### MySQL HA
Deploy to os02.node

    playback-mysql --install --user ubuntu --hosts os02.node
    playback-mysql --config --user ubuntu --hosts os02.node --wsrep_cluster_address "gcomm://os02.node,os03.node" --wsrep_node_name="galera1" --wsrep_node_address="os02.node"

Deploy to os03.node

    playback-mysql --install --user ubuntu --hosts os03.node
    playback-mysql --config --user ubuntu --hosts os03.node --wsrep_cluster_address "gcomm://os02.node,os03.node" --wsrep_node_name="galera2" --wsrep_node_address="os03.node"

Start cluster

    playback-mysql --user ubuntu --hosts os02.node --manage --wsrep-new-cluster
    playback-mysql --user ubuntu --hosts os03.node --manage --start
    playback-mysql --user ubuntu --hosts os02.node --manage --change-root-password changeme

#### HAProxy HA
Deploy to os04.node

    playback-haproxy --install --user ubuntu --hosts os04.node

Deploy to os05.node

    playback-haproxy --install --user ubuntu --hosts os05.node

Generate the HAProxy configuration and upload to target hosts(Do not forget to edit the generated configuration)

    playback-haproxy --gen-conf 
    playback-haproxy --config --upload-conf haproxy.cfg --user ubuntu --hosts os04.node,os05.node

Configure Keepalived

    playback-haproxy --config --configure-keepalived --router_id lb1 --priority 150 --state MASTER --interface eth0 --vip CONTROLLER_VIP --user ubuntu --hosts os04.node
    playback-haproxy --config --configure-keepalived --router_id lb2 --priority 100 --state SLAVE --interface eth0 --vip CONTROLLER_VIP --user ubuntu --hosts os05.node

#### RabbitMQ HA
Deploy to os02.node and os03.node

    playback-rabbitmq --install --user ubuntu --hosts os02.node,os03.node --erlang-cookie YXUNUSYXOKXUQUIJMPRY --rabbit-user openstack --rabbit-pass changeme
    
Create cluster

    playback-rabbitmq --user ubuntu --hosts os03.node --join-cluster rabbit@os02

#### Keystone HA
Create keystone database

    playback-keystone --user ubuntu --hosts os02.node --create-keystone-db --root-db-pass changeme --keystone-db-pass changeme

Install keystone on os02.node and os03.node

    playback-keystone --user ubuntu --hosts os02.node,os03.node --install --admin_token changeme --connection mysql+pymysql://keystone:changeme@CONTROLLER_VIP/keystone --memcache_servers os02.node:11211,os03.node:11211

Create the service entity and API endpoints

    playback-keystone --user ubuntu --hosts os02.node --create-entity-and-endpoint --os-token changeme --os-url http://CONTROLLER_VIP:35357/v3 --public-endpoint http://CONTROLLER_VIP:5000/v2.0 --internal-endpoint http://CONTROLLER_VIP:5000/v2.0 --admin-endpoint http://CONTROLLER_vip:35357/v2.0

Create projects, users, and roles

    playback-keystone --user ubuntu --hosts os02.node --create-projects-users-roles --os-token changeme --os-url http://CONTROLLER_VIP:35357/v3 --admin-pass changeme --demo-pass changeme

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

#### Glance HA
Create glance database

    playback-glance --user ubuntu --hosts os02.node --create-glance-db --root-db-pass changeme --glance-db-pass changeme

Create service credentials

    playback-glance --user ubuntu --hosts os02.node --create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --glance-pass changeme --endpoint http://CONTROLLER_VIP:9292

Install glance on os02.node and os03.node

    playback-glance --user ubuntu --hosts os02.node,os03.node --install --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme  --swift-store-auth-address http://CONTROLLER_VIP:5000/v2.0/ 

#### Nova HA
Create nova database

    playback-nova --user ubuntu --hosts os02.node --create-nova-db --root-db-pass changeme --nova-db-pass changeme 

Create service credentials

    playback-nova --user ubuntu --hosts os02.node --create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --nova-pass changeme --endpoint 'http://CONTROLLER_VIP:8774/v2/%\(tenant_id\)s'

Install nova on os02.node

    playback-nova --user ubuntu --hosts os02.node --install --connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --my-ip MANAGEMENT_IP --memcached-servers os02.node:11211,os03.node:11211 --rabbit-hosts os02.node,os03.node --rabbit-pass changeme --glance-host CONTROLLER_VIP --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --metadata-proxy-shared-secret changeme --populate

Install nova on os03.node

    playback-nova --user ubuntu --hosts os03.node --install --connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --my-ip MANAGEMENT_IP --memcached-servers os02.node:11211,os03.node:11211 --rabbit-hosts os02.node,os03.node --rabbit-pass changeme --glance-host CONTROLLER_VIP --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --metadata-proxy-shared-secret changeme

#### Nova Compute
Add nova computes

    playback-nova-compute --user ubuntu --hosts os06.node --install --my-ip MANAGEMENT_IP --rabbit-hosts os02.node,os03.node --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --novncproxy-base-url http://CONTROLLER_VIP:6080/vnc_auto.html --glance-host CONTROLLER_VIP --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --rbd-secret-uuid changeme-changeme-changeme-changeme

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

    playback-neutron --user ubuntu --hosts os02.node --create-neutron-db --root-db-pass changeme --neutron-db-pass changeme 

Create service credentials

    playback-neutron --user ubuntu --hosts os02.node --create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --neutron-pass changeme --endpoint http://CONTROLLER_VIP:9696

Install Neutron for self-service

    playback-neutron --user ubuntu --hosts os02.node,os03.node --install --connection mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron --rabbit-hosts os02.node,os03.node --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --nova-url http://CONTROLLER_VIP:8774/v2 --nova-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP --nova-metadata-ip CONTROLLER_VIP --metadata-proxy-shared-secret changeme-changeme-changeme-changeme --populate


#### Neutron Agent
todo 
verify neutron controller configuration and do install neutron compute 
http://docs.openstack.org/liberty/install-guide-ubuntu/neutron-compute-install.html
