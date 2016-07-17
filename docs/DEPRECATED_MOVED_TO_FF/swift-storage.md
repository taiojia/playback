# OpenStack Swift Storage

## Deploy Swift Storage

Prepare disks on storage node, this commmand will format the sdb, sdc, sdd, sde disks.

    swift-storage-deploy --user ubuntu --hosts compute6.maas,compute7.maas,compute8.maas,compute9.maas,compute10.maas prepare-disks --name sdb,sdc,sdd,sde

Install swift storage on storage node, `--address` and `--bind-ip` are management interface ip on the current node.

    swift-storage-deploy --user ubuntu --hosts compute6.maas install --address MANAGEMENT_INTERFACE_IP --bind-ip MANAGEMENT_INTERFACE_IP
    swift-storage-deploy --user ubuntu --hosts compute7.maas install --address MANAGEMENT_INTERFACE_IP --bind-ip MANAGEMENT_INTERFACE_IP
    swift-storage-deploy --user ubuntu --hosts compute8.maas install --address MANAGEMENT_INTERFACE_IP --bind-ip MANAGEMENT_INTERFACE_IP
    swift-storage-deploy --user ubuntu --hosts compute9.maas install --address MANAGEMENT_INTERFACE_IP --bind-ip MANAGEMENT_INTERFACE_IP
    swift-storage-deploy --user ubuntu --hosts compute10.maas install --address MANAGEMENT_INTERFACE_IP --bind-ip MANAGEMENT_INTERFACE_IP

Create account ring on controller node

    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas create-account-builder-file --partitions 10 --replicas 3 --moving 1
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute6.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute6.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute6.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute6.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute7.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute7.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute7.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute7.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute8.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute8.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute8.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute8.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute9.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute9.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute9.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute9.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute10.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute10.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute10.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-add --region 1 --zone 1 --ip compute10.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas.maas account-builder-rebalance

Create container ring on controller node

    swift-storage-deploy --user ubuntu --hosts controller1.maas create-container-builder-file --partitions 10 --replicas 3 --moving 1
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute6.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute6.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute6.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute6.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute7.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute7.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute7.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute7.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute8.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute8.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute8.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute8.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute9.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute9.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute9.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute9.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute10.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute10.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute10.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-add --region 1 --zone 1 --ip compute10.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas container-builder-rebalance

Create object ring on controller node

    swift-storage-deploy --user ubuntu --hosts controller1.maas create-object-builder-file --partitions 10 --replicas 3 --moving 1
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute6.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute6.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute6.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute6.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute7.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute7.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute7.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute7.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute8.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute8.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute8.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute8.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute9.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute9.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute9.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute9.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute10.maas --device sdb --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute10.maas --device sdc --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute10.maas --device sdd --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-add --region 1 --zone 1 --ip compute10.maas --device sde --weight 100
    swift-storage-deploy --user ubuntu --hosts controller1.maas object-builder-rebalance

 Sync the builder file from controller node to each storage node and other any proxy node

    swift-storage-deploy --user ubuntu --host controller1.maas sync-builder-file --to controller2.maas,controller3.maas,compute6.maas,compute7.maas,compute8.maas,compute9.maas,compute10.maas

Finalize installation on all nodes

    playback-swift --user ubuntu --hosts controller1.maas,controller2.maas,controller3.maas,compute6.maas,compute7.maas,compute8.maas,compute9.maas,compute10.maas finalize-install --swift-hash-path-suffix changeme --swift-hash-path-prefix changeme

Using `swift-storage-deploy --help` to see the details.