# Playback

Playback is an OpenStack provisioning and orchestration library that all of the OpenStack components can be deployed automation with high availability on Ubuntu based operating system(Xenial and trusty) as a pythonic way.

## Library Quick-start

    from playback.api import Horizon

    remote_user = 'ubuntu'
    remote_hosts = ['192.168.1.3', '192.168.1.4']

    horizon = Horizon(user=remote_user, hosts=remote_hosts)
    horizon.install(openstack_host='192.168.1.2', memcached_servers='192.168.1.3:11211,192.168.1.4:11211', time_zone='America/New_York')

## Command-Line Quick-start(provision OpenStack mitaka on xenil or trusty)

### Requirements

* The OpenStack bare metal hosts are in MAAS environment(recommend)
* All hosts are two NICs at least(external and internal)
* We assume that you have ceph installed, the cinder bachend default using ceph, the running instace default to using ceph as it's local storage. About ceph please visit: http://docs.ceph.com/docs/master/rbd/rbd-openstack/ or see the (Option)Ceph Guide below.
* For resize instance nova user can be login to each compute node via ssh passwordless(include sudo), and all compute nodes need to restart libvirt-bin to enable live migration
* The playback node is the same as ceph-deploy node where can be login to each openstack node passwordless and sudo-passwordless
* The playback node default using ~/.ssh/id_rsa ssh private key to logon remote server
* You need to restart the `nova-compute`, `cinder-volume` and `glance-api` services to finalize the installation if you have selected the ceph as that backend
* playback support consistency groups for future use but the default LVM and Ceph driver does not support consistency groups yet because the consistency technology is not available at that storage level

### Install playback

Install playback on PLAYBACK-NODE

    pip install playback

### Prepare environment

Prepare the OpenStack environment.
(NOTE) DO NOT setup eth1 in /etc/network/interfaces

    playback environment prepare-hosts --user ubuntu --hosts \
    HAPROXY1,\
    HAPROXY2,\
    CONTROLLER1,\
    CONTROLLER2,\
    COMPUTE1,\
    COMPUTE2,\
    COMPUTE3,\
    COMPUTE4,\
    COMPUTE5,\
    COMPUTE6,\
    COMPUTE7,\
    COMPUTE8,\
    COMPUTE9,\
    COMPUTE10 \
    --public-interface eth1

### MySQL HA

Deploy to CONTROLLER1

    playback mysql install --user ubuntu --hosts CONTROLLER1
    playback mysql config --user ubuntu --hosts CONTROLLER1 --wsrep-cluster-address "gcomm://CONTROLLER1,CONTROLLER2" --wsrep-node-name="galera1" --wsrep-node-address="CONTROLLER1"

Deploy to CONTROLLER2

    playback mysql install --user ubuntu --hosts CONTROLLER2
    playback mysql config --user ubuntu --hosts CONTROLLER2 --wsrep-cluster-address "gcomm://CONTROLLER1,CONTROLLER2" --wsrep-node-name="galera2" --wsrep-node-address="CONTROLLER2"

Start the cluster

    playback mysql manage --user ubuntu --hosts CONTROLLER1 --wsrep-new-cluster
    playback mysql manage --user ubuntu --hosts CONTROLLER2 --start
    playback mysql manage --user ubuntu --hosts CONTROLLER1 --change-root-password changeme

Show the cluster status

    playback mysql manage --user ubuntu --hosts CONTROLLER1 --show-cluster-status --root-db-pass changeme


### HAProxy HA

Deploy to HAPROXY1

    playback haproxy install --user ubuntu --hosts HAPROXY1

Deploy to HAPROXY2

    playback haproxy install --user ubuntu --hosts HAPROXY2

Generate the HAProxy configuration and upload to target hosts(Do not forget to edit the generated configuration)

    playback haproxy gen-conf
    playback haproxy config --user ubuntu --hosts HAPROXY1,HAPROXY2 --upload-conf haproxy.cfg

Configure Keepalived

    playback haproxy config --user ubuntu --hosts HAPROXY1 --configure-keepalived --router_id lb1 --priority 150 --state MASTER --interface eth0 --vip CONTROLLER_VIP
    playback haproxy config --user ubuntu --hosts HAPROXY2 --configure-keepalived --router_id lb2 --priority 100 --state SLAVE --interface eth0 --vip CONTROLLER_VIP

### RabbitMQ HA

Deploy to CONTROLLER1 and CONTROLLER2

    playback rabbitmq install --user ubuntu --hosts CONTROLLER1,CONTROLLER2 --erlang-cookie changemechangeme --rabbit-user openstack --rabbit-pass changeme

Create cluster(Ensure CONTROLLER2 can access CONTROLLER1 via hostname)

    playback rabbitmq join-cluster --user ubuntu --hosts CONTROLLER2 --name rabbit@CONTROLLER1

### Keystone HA

Create keystone database

    playback keystone create db --user ubuntu --hosts CONTROLLER1 --root-db-pass changeme --keystone-db-pass changeme

Install keystone on CONTROLLER1 and CONTROLLER2

    playback keystone install --user ubuntu --hosts CONTROLLER1 --admin-token changeme --connection mysql+pymysql://keystone:changeme@CONTROLLER_VIP/keystone --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --populate
    playback keystone install --user ubuntu --hosts CONTROLLER2 --admin-token changeme --connection mysql+pymysql://keystone:changeme@CONTROLLER_VIP/keystone --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211

Create the service entity and API endpoints

    playback keystone create entity-and-endpoint --user ubuntu --hosts CONTROLLER1 --os-token changeme --os-url http://CONTROLLER_VIP:35357/v3 --public-endpoint http://CONTROLLER_VIP:5000/v3 --internal-endpoint http://CONTROLLER_VIP:5000/v3 --admin-endpoint http://CONTROLLER_vip:35357/v3

Create projects, users, and roles

    playback keystone create projects-users-roles --user ubuntu --hosts CONTROLLER1 --os-token changeme --os-url http://CONTROLLER_VIP:35357/v3 --admin-pass changeme --demo-pass changeme

(OPTION) you will need to create OpenStack client environment scripts
admin-openrc.sh

    export OS_PROJECT_DOMAIN_NAME=default
    export OS_USER_DOMAIN_NAME=default
    export OS_PROJECT_NAME=admin
    export OS_TENANT_NAME=admin
    export OS_USERNAME=admin
    export OS_PASSWORD=changeme
    export OS_AUTH_URL=http://CONTROLLER_VIP:35357/v3
    export OS_IDENTITY_API_VERSION=3
    export OS_IMAGE_API_VERSION=2
    export OS_AUTH_VERSION=3

demo-openrc.sh

    export OS_PROJECT_DOMAIN_NAME=default
    export OS_USER_DOMAIN_NAME=default
    export OS_PROJECT_NAME=demo
    export OS_TENANT_NAME=demo
    export OS_USERNAME=demo
    export OS_PASSWORD=changeme
    export OS_AUTH_URL=http://CONTROLLER_VIP:5000/v3
    export OS_IDENTITY_API_VERSION=3
    export OS_IMAGE_API_VERSION=2
    export OS_AUTH_VERSION=3

### Glance HA

Create glance database

    playback glance create db --user ubuntu --hosts CONTROLLER1 --root-db-pass changeme --glance-db-pass changeme

Create service credentials

    playback glance create service-credentials --user ubuntu --hosts CONTROLLER1 --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --glance-pass changeme --public-endpoint http://CONTROLLER_VIP:9292 --internal-endpoint http://CONTROLLER_VIP:9292 --admin-endpoint http://CONTROLLER_VIP:9292

Install glance on CONTROLLER1 and CONTROLLER2

    playback glance install --user ubuntu --hosts CONTROLLER1 --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --populate
    playback glance install --user ubuntu --hosts CONTROLLER2 --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211

### Nova HA

Create nova database

    playback nova create db --user ubuntu --hosts CONTROLLER1 --root-db-pass changeme --nova-db-pass changeme

Create service credentials

    playback nova create service-credentials --user ubuntu --hosts CONTROLLER1 --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --nova-pass changeme --public-endpoint 'http://CONTROLLER_VIP:8774/v2.1/%\(tenant_id\)s' --internal-endpoint 'http://CONTROLLER_VIP:8774/v2.1/%\(tenant_id\)s' --admin-endpoint 'http://CONTROLLER_VIP:8774/v2.1/%\(tenant_id\)s'

Install nova on CONTROLLER1

    playback nova install --user ubuntu --hosts CONTROLLER1 --connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova --api-connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova_api --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --my-ip MANAGEMENT_IP --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass changeme --glance-api-servers http://CONTROLLER_VIP:9292 --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --metadata-proxy-shared-secret changeme --populate

Install nova on CONTROLLER2

    playback nova install --user ubuntu --hosts CONTROLLER2 --connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova --api-connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova_api --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --my-ip MANAGEMENT_IP --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass changeme --glance-api-servers http://CONTROLLER_VIP:9292 --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --metadata-proxy-shared-secret changeme

### Nova Compute

Add nova computes(use `uuidgen` to generate the ceph uuid)

    playback nova-compute install --user ubuntu --hosts COMPUTE1 --my-ip MANAGEMENT_IP --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --novncproxy-base-url http://CONTROLLER_VIP:6080/vnc_auto.html --glance-api-servers http://CONTROLLER_VIP:9292 --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --rbd-secret-uuid changeme-changeme-changeme-changeme --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211
    playback nova-compute install --user ubuntu --hosts COMPUTE2 --my-ip MANAGEMENT_IP --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --novncproxy-base-url http://CONTROLLER_VIP:6080/vnc_auto.html --glance-api-servers http://CONTROLLER_VIP:9292 --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --rbd-secret-uuid changeme-changeme-changeme-changeme --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211

The libvirt defaults to using ceph as shared storage, the ceph pool for running instance is vms. if you do not using ceph as it's bachend, you must remove the following param:

    images_type = rbd
    images_rbd_pool = vms
    images_rbd_ceph_conf = /etc/ceph/ceph.conf
    rbd_user = cinder
    rbd_secret_uuid = changeme-changeme-changeme-changeme
    disk_cachemodes="network=writeback"
    live_migration_flag="VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_LIVE,VIR_MIGRATE_PERSIST_DEST,VIR_MIGRATE_TUNNELLED"


### Neutron HA

Create nova database

    playback neutron create db --user ubuntu --hosts CONTROLLER1 --root-db-pass changeme --neutron-db-pass changeme

Create service credentials

    playback neutron create service-credentials --user ubuntu --hosts CONTROLLER1 --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --neutron-pass changeme --public-endpoint http://CONTROLLER_VIP:9696 --internal-endpoint http://CONTROLLER_VIP:9696 --admin-endpoint http://CONTROLLER_VIP:9696

Install Neutron for self-service

    playback neutron install --user ubuntu --hosts CONTROLLER1 --connection mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --nova-url http://CONTROLLER_VIP:8774/v2.1 --nova-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP --nova-metadata-ip CONTROLLER_VIP --metadata-proxy-shared-secret changeme-changeme-changeme-changeme --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --populate
    playback neutron install --user ubuntu --hosts CONTROLLER2 --connection mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --nova-url http://CONTROLLER_VIP:8774/v2.1 --nova-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP --nova-metadata-ip CONTROLLER_VIP --metadata-proxy-shared-secret changeme-changeme-changeme-changeme --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211


### Neutron Agent

Install neutron agent on compute nodes

    playback neutron-agent install --user ubuntu --hosts COMPUTE1 --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211
    playback neutron-agent install --user ubuntu --hosts COMPUTE2 --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211


### Horizon HA

Install horizon on controller nodes

    playback horizon install --user ubuntu --hosts CONTROLLER1,CONTROLLER2 --openstack-host CONTROLLER_VIP  --memcached-servers CONTROLLER1:11211 --time-zone Asia/Shanghai


### Cinder HA

Create cinder database

    playback cinder create db --user ubuntu --hosts CONTROLLER1 --root-db-pass changeme --cinder-db-pass changeme

Create cinder service creadentials

    playback cinder create service-credentials --user ubuntu --hosts CONTROLLER1 --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --cinder-pass changeme --public-endpoint-v1 'http://CONTROLLER_VIP:8776/v1/%\(tenant_id\)s' --internal-endpoint-v1 'http://CONTROLLER_VIP:8776/v1/%\(tenant_id\)s' --admin-endpoint-v1 'http://CONTROLLER_VIP:8776/v1/%\(tenant_id\)s' --public-endpoint-v2 'http://CONTROLLER_VIP:8776/v2/%\(tenant_id\)s' --internal-endpoint-v2 'http://CONTROLLER_VIP:8776/v2/%\(tenant_id\)s' --admin-endpoint-v2 'http://CONTROLLER_VIP:8776/v2/%\(tenant_id\)s'

Install cinder-api and cinder-volume on controller nodes, the volume backend defaults to ceph (you must have ceph installed)

    playback cinder install --user ubuntu --hosts CONTROLLER1 --connection mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder --rabbit-user openstack --rabbit-pass changeme --rabbit-hosts CONTROLLER1,CONTROLLER2 --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --cinder-pass changeme --my-ip MANAGEMENT_INTERFACE_IP --glance-api-servers http://CONTROLLER_VIP:9292 --rbd-secret-uuid changeme-changeme-changeme-changeme --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --populate
    playback cinder install --user ubuntu --hosts CONTROLLER2 --connection mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder --rabbit-user openstack --rabbit-pass changeme --rabbit-hosts CONTROLLER1,CONTROLLER2 --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --cinder-pass changeme --my-ip MANAGEMENT_INTERFACE_IP --glance-api-servers http://CONTROLLER_VIP:9292 --rbd-secret-uuid changeme-changeme-changeme-changeme --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211

### Swift proxy HA

Create the Identity service credentials

    playback swift create service-credentials --user ubuntu --hosts CONTROLLER1 --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --swift-pass changeme --public-endpoint 'http://CONTROLLER_VIP:8080/v1/AUTH_%\(tenant_id\)s' --internal-endpoint 'http://CONTROLLER_VIP:8080/v1/AUTH_%\(tenant_id\)s' --admin-endpoint http://CONTROLLER_VIP:8080/v1

Install swift proxy

    playback swift install --user ubuntu --hosts CONTROLLER1,CONTROLLER2 --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --swift-pass changeme --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211


### Swift storage

Prepare disks on storage node

    playback swift-storage prepare-disks --user ubuntu --hosts OBJECT1,OBJECT2 --name sdb,sdc,sdd,sde

Install swift storage on storage node

    playback swift-storage install --user ubuntu --hosts OBJECT1 --address MANAGEMENT_INTERFACE_IP --bind-ip MANAGEMENT_INTERFACE_IP
    playback swift-storage install --user ubuntu --hosts OBJECT2 --address MANAGEMENT_INTERFACE_IP --bind-ip MANAGEMENT_INTERFACE_IP

Create account ring on controller node

    playback swift-storage create account-builder-file --user ubuntu --hosts CONTROLLER1 --partitions 10 --replicas 3 --moving 1
    playback swift-storage account-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sdb --weight 100
    playback swift-storage account-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sdc --weight 100
    playback swift-storage account-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sdd --weight 100
    playback swift-storage account-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sde --weight 100
    playback swift-storage account-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sdb --weight 100
    playback swift-storage account-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sdc --weight 100
    playback swift-storage account-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sdd --weight 100
    playback swift-storage account-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sde --weight 100
    playback swift-storage account-builder-rebalance --user ubuntu --hosts CONTROLLER1

Create container ring on controller node

    playback swift-storage create container-builder-file --user ubuntu --hosts CONTROLLER1 --partitions 10 --replicas 3 --moving 1
    playback swift-storage container-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sdb --weight 100
    playback swift-storage container-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sdc --weight 100
    playback swift-storage container-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sdd --weight 100
    playback swift-storage container-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sde --weight 100
    playback swift-storage container-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sdb --weight 100
    playback swift-storage container-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sdc --weight 100
    playback swift-storage container-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sdd --weight 100
    playback swift-storage container-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sde --weight 100
    playback swift-storage container-builder-rebalance --user ubuntu --hosts CONTROLLER1

Create object ring on controller node

    playback swift-storage create object-builder-file --user ubuntu --hosts CONTROLLER1 --partitions 10 --replicas 3 --moving 1
    playback swift-storage object-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sdb --weight 100
    playback swift-storage object-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sdc --weight 100
    playback swift-storage object-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sdd --weight 100
    playback swift-storage object-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT1_MANAGEMENT_IP --device sde --weight 100
    playback swift-storage object-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sdb --weight 100
    playback swift-storage object-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sdc --weight 100
    playback swift-storage object-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sdd --weight 100
    playback swift-storage object-builder-add --user ubuntu --hosts CONTROLLER1 --region 1 --zone 1 --ip OBJECT2_MANAGEMENT_IP --device sde --weight 100
    playback swift-storage object-builder-rebalance --user ubuntu --hosts CONTROLLER1

 Sync the builder file from controller node to each storage node and other any proxy node

    playback swift-storage sync-builder-file --user ubuntu --host CONTROLLER1 --to CONTROLLER2,OBJECT1,OBJECT2

Finalize installation on all nodes

    playback swift finalize --user ubuntu --hosts CONTROLLER1,CONTROLLER2,OBJECT1,OBJECT2 --swift-hash-path-suplaybackix changeme --swift-hash-path-prefix changeme

### Ceph Guide

For more information about ceph backend visit:

[preflight](http://docs.ceph.com/docs/jewel/start/quick-start-preflight/)

[Cinder and Glance driver](http://docs.ceph.com/docs/jewel/rbd/rbd-openstack/)

On Xenial please using ceph-deploy version 1.5.34

Install ceph-deploy(1.5.34)

    wget -q -O- 'https://download.ceph.com/keys/release.asc' | sudo apt-key add -
    echo deb http://download.ceph.com/debian-jewel/ $(lsb_release -sc) main | sudo tee /etc/apt/sources.list.d/ceph.list
    sudo apt-get update && sudo apt-get install ceph-deploy

Create ceph cluster directory

    mkdir ceph-cluster
    cd ceph-cluster

Create cluster and add initial monitor(s) to the ceph.conf

    ceph-deploy new  CONTROLLER1 CONTROLLER2 COMPUTE1 COMPUTE2 BLOCK1 BLOCK2
    echo "osd pool default size = 2" | tee -a ceph.conf

Install ceph client(Optionaly you can use `--release jewel` to install jewel version, the ceph-deploy 1.5.34 default release is jewel) and you can use `--repo-url http://your-local-repo.example.org/mirror/download.ceph.com/debian-jewel` to specify the local repository.

    ceph-deploy install PLAYBACK-NODE CONTROLLER1 CONTROLLER2 COMPUTE1 COMPUTE2 BLOCK1 BLOCK2

Add the initial monitor(s) and gather the keys

    ceph-deploy mon create-initial

If you want to add additional monitors, do that

    ceph-deploy mon add {additional-monitor}

Add ceph osd(s)

    ceph-deploy osd create --zap-disk BLOCK1:/dev/sdb
    ceph-deploy osd create --zap-disk BLOCK1:/dev/sdc
    ceph-deploy osd create --zap-disk BLOCK2:/dev/sdb
    ceph-deploy osd create --zap-disk BLOCK2:/dev/sdc

Sync admin key

    ceph-deploy admin PLAYBACK-NODE CONTROLLER1 CONTROLLER2 COMPUTE1 COMPUTE2 BLOCK1 BLOCK2
    sudo chmod +r /etc/ceph/ceph.client.admin.keyring # On all ceph clients node

Create osd pool for cinder and running instance

    ceph osd pool create volumes 512
    ceph osd pool create vms 512
    ceph osd pool create images 512

Setup ceph client authentication

    ceph auth get-or-create client.cinder mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=volumes, allow rwx pool=vms, allow rx pool=images'
    ceph auth get-or-create client.glance mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=images'

Add the keyrings for `client.cinder` and `client.glance` to appropriate nodes and change their ownership

    ceph auth get-or-create client.cinder | sudo tee /etc/ceph/ceph.client.cinder.keyring # On all cinder-volume nodes
    sudo chown cinder:cinder /etc/ceph/ceph.client.cinder.keyring" # On all cinder-volume nodes

    ceph auth get-or-create client.glance | sudo tee /etc/ceph/ceph.client.glance.keyring # On all glance-api nodes
    sudo chown glance:glance /etc/ceph/ceph.client.glance.keyring" # On all glance-api nodes

Nodes running `nova-compute` need the keyring file for the `nova-compute` process

    ceph auth get-or-create client.cinder | sudo tee /etc/ceph/ceph.client.cinder.keyring # On all nova-compute nodes

They also need to store the secret key of the `client.cinder user` in `libvirt`. The libvirt process needs it to access the cluster while attaching a block device from Cinder.
Create a temporary copy of the secret key on the nodes running `nova-compute`

    ceph auth get-key client.cinder | tee client.cinder.key # On all nova-compute nodes

Then, on the `compute nodes`, add the secret key to `libvirt` and remove the temporary copy of the key(the uuid is the same as your --rbd-secret-uuid option, you have to save the uuid for later)

    uuidgen
    457eb676-33da-42ec-9a8c-9293d545c337

    # The following steps on all nova-compute nodes
    cat > secret.xml <<EOF
    <secret ephemeral='no' private='no'>
      <uuid>457eb676-33da-42ec-9a8c-9293d545c337</uuid>
      <usage type='ceph'>
        <name>client.cinder secret</name>
      </usage>
    </secret>
    EOF
    sudo virsh secret-define --file secret.xml
    Secret 457eb676-33da-42ec-9a8c-9293d545c337 created
    sudo virsh secret-set-value --secret 457eb676-33da-42ec-9a8c-9293d545c337 --base64 $(cat client.cinder.key) && rm client.cinder.key secret.xml

(optional)Now on every compute nodes edit your Ceph configuration file, add the client section

    [client]
    rbd cache = true
    rbd cache writethrough until flush = true
    rbd concurrent management ops = 20

    [client.cinder]
    keyring = /etc/ceph/ceph.client.cinder.keyring

(optional)On every glance-api nodes edit your Ceph configuration file, add the client section

    [client.glance]
    keyring= /etc/ceph/ceph.client.glance.keyring

(optional)If you want to remove osd

    sudo stop ceph-mon-all && sudo stop ceph-osd-all # On osd node
    ceph osd out {OSD-NUM}
    ceph osd crush remove osd.{OSD-NUM}
    ceph auth del osd.{OSD-NUM}
    ceph osd rm {OSD-NUM}
    ceph osd crush remove {HOST}

(optional)If you want to remove monitor

    ceph mon remove {MON-ID}

Notes: you need to restart the `nova-compute`, `cinder-volume` and `glance-api` services to finalize the installation.

### Shared File Systems service(DEPRECATED)

Create manila database and service credentials

    playback --user ubuntu --hosts CONTROLLER1 provision manila create-manila-db --root-db-pass CHANGEME --manila-db-pass CHANGEME
    playback --user ubuntu --hosts CONTROLLER1 provision manila create-service-credentials --os-password CHANGEME --os-auth-url http://CONTROLLER_VIP:35357/v3 --manila-pass CHANGEME --public-endpoint-v1 "http://CONTROLLER_VIP:8786/v1/%\(tenant_id\)s" --internal-endpoint-v1 "http://CONTROLLER_VIP:8786/v1/%\(tenant_id\)s" --admin-endpoint-v1 "http://CONTROLLER_VIP:8786/v1/%\(tenant_id\)s" --public-endpoint-v2 "http://CONTROLLER_VIP:8786/v2/%\(tenant_id\)s" --internal-endpoint-v2 "http://CONTROLLER_VIP:8786/v2/%\(tenant_id\)s" --admin-endpoint-v2 "http://CONTROLLER_VIP:8786/v2/%\(tenant_id\)s"

Install manila on CONTROLLER1 and CONTROLLER2

    playback --user ubuntu --hosts CONTROLLER1 provision manila install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip CONTROLLER1 --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass CHANGEME --populate
    playback --user ubuntu --hosts CONTROLLER2 provision manila install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip CONTROLLER2 --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass CHANGEME

Install manila share on CONTROLLER1 and CONTROLLER2

    playback --user ubuntu --hosts CONTROLLER1 provision manila-share install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip CONTROLLER1 --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass CHANGEME --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass CHANGEME --nova-pass CHANGEME --cinder-pass CHANGEME
    playback --user ubuntu --hosts CONTROLLER2 provision manila-share install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip CONTROLLER2 --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2 --rabbit-user openstack --rabbit-pass CHANGEME --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass CHANGEME --nova-pass CHANGEME --cinder-pass CHANGEME

Create the service image for manila

http://docs.openstack.org/mitaka/install-guide-ubuntu/launch-instance-manila.html

Create shares with share servers management support

http://docs.openstack.org/mitaka/install-guide-ubuntu/launch-instance-manila-dhss-true-option2.html



## Current version

* v0.4.0 (Ris)
  New command line interface
