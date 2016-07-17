# Ceph Guide

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

    ceph-deploy new compute1.maas compute2.maas compute3.maas compute4.maas compute5.maas
    echo "osd pool default size = 2" | tee -a ceph.conf

Install ceph client(Optionaly you can use `--release jewel` to install jewel version, the ceph-deploy 1.5.34 default release is jewel) and you can use `--repo-url http://your-local-repo.example.org/mirror/download.ceph.com/debian-jewel` to specify the local repository.

    ceph-deploy install playback.maas controller1.maas controller2.maas controller3.maas compute1.maas compute2.maas compute3.maas compute4.maas compute5.maas compue6.maas comupte7.maas compute8.maas compute9.maas compute10.maas

Add the initial monitor(s) and gather the keys

    ceph-deploy mon create-initial

If you want to add additional monitors, do that

    ceph-deploy mon add {additional-monitor}

Add ceph osd(s)

    ceph-deploy osd create --zap-disk compute1.maas:/dev/sdb
    ceph-deploy osd create --zap-disk compute1.maas:/dev/sdc
    ceph-deploy osd create --zap-disk compute2.maas:/dev/sdb
    ceph-deploy osd create --zap-disk compute2.maas:/dev/sdc
    ceph-deploy osd create --zap-disk compute3.maas:/dev/sdb
    ceph-deploy osd create --zap-disk compute3.maas:/dev/sdc
    ceph-deploy osd create --zap-disk compute4.maas:/dev/sdb
    ceph-deploy osd create --zap-disk compute4.maas:/dev/sdc
    ceph-deploy osd create --zap-disk compute5.maas:/dev/sdb
    ceph-deploy osd create --zap-disk compute5.maas:/dev/sdc

Sync admin key

    ceph-deploy admin playback.maas controller1.maas controller2.maas controller3.maas compute1.maas compute2.maas compute3.maas compute4.maas compute5.maas compue6.maas comupte7.maas compute8.maas compute9.maas compute10.maas
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

Then, on the `compute nodes`, add the secret key to `libvirt` and remove the temporary copy of the key(the uuid is the same as your --rbd-uuid option, you have to save the uuid for later)

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
    keyring= /etc/ceph/client.glance.keyring

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
