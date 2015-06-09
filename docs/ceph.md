# on maas:
    vi /etc/hosts
    mkdir ceph-cluster && cd ceph-cluster
    ceph-deploy --username ubuntu new compute01
    ceph-deploy --username ubuntu install compute01 compute02 compute03
    ceph-deploy --username ubuntu mon create-initial
    ceph-deploy --username ubuntu disk list compute01
    ceph-deploy --username ubuntu disk list compute02
    ceph-deploy --username ubuntu disk list compute03
    ceph-deploy --username ubuntu disk zap compute01:sdb
    ceph-deploy --username ubuntu disk zap compute01:sdc
    ceph-deploy --username ubuntu disk zap compute02:sdb
    ceph-deploy --username ubuntu disk zap compute02:sdc
    ceph-deploy --username ubuntu disk zap compute03:sdb
    ceph-deploy --username ubuntu disk zap compute03:sdc
    ceph-deploy --username ubuntu osd prepare compute01:sdb compute01:sdc
    ceph-deploy --username ubuntu osd prepare compute02:sdb compute02:sdc
    ceph-deploy --username ubuntu osd prepare compute03:sdb compute03:sdc
    ceph-deploy --username ubuntu osd activate compute01:/dev/sdb1 compute01:/dev/sdc1
    ceph-deploy --username ubuntu osd activate compute02:/dev/sdb1 compute02:/dev/sdc1
    ceph-deploy --username ubuntu osd activate compute03:/dev/sdb1 compute03:/dev/sdc1

# user ceph for ceph
## on osd and admin node:
    adduser ceph
    echo ceph ALL = \(root\) NOPASSWD:ALL | sudo tee /etc/sudoers.d/ceph
    sudo chmod 0440 /etc/sudoers.d/ceph
    ssh-key-gen
    ssh-copy-id ceph@node

## ceph.conf in admin-node:
    osd pool default size = 2
    public network = 10.32.150.0/24
    cluster network = 192.168.1.0/24

## purge data:
    ceph-deploy purge compute01 compute02 compute03
    ceph-deploy purgedata compute01 compute02 compute03
    ceph-deploy forgetkeys

## create mon:
    ceph-deploy new compute01

## install ceph client:
    ceph-deploy install MAAS compute01 compute02 compute03

## init mon:
    ceph-deploy mon create-initial

## prepare osd:
    ceph-deploy osd prepare compute02:sdb compute03:sdb

## active osd:
    ceph-deploy osd activate compute02:/dev/sdb1 compute03:/dev/sdb1

## copy conf and key to nodes:
    ceph-deploy admin MAAS compute01 compute02 compute03

## change permissions:
    sudo chmod +r /etc/ceph/ceph.client.admin.keyring

##  add an osd:
    ceph-deploy osd prepare compute01:sdb
    ceph-deploy osd activate compute01:/dev/sdb1
    ceph-deploy osd prepare compute01:sdc compute02:sdc compute03:sdc
    ceph-deploy osd activate compute01:/dev/sdc1 compute02:/dev/sdc1 compute03:/dev/sdc1

## add an mon:
    ceph-deploy mon create compute02 compute03

## check quorum status:
    ceph quorum_status --format json-pretty


