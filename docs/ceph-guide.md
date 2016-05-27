# Ceph Guide

Create ceph cluster directory

    mkdir ceph-cluster
    cd ceph-cluster

Create cluster and add initial monitor(s) to the ceph.conf

    playback-ceph-deploy new compute1.maas compute2.maas compute3.maas compute4.maas compute5.maas
    echo "osd pool default size = 2" | tee -a ceph.conf

Install ceph client

    playback-ceph-deploy install playback.maas controller1.maas controller2.maas controller3.maas compute1.maas compute2.maas compute3.maas compute4.maas compute5.maas compue6.maas comupte7.maas compute8.maas compute9.maas compute10.maas

Add the initial monitor(s) and gather the keys

    playback-ceph-deploy mon create-initial

If you want to add additional monitors, do that

    playback-ceph-deploy mon add {additional-monitor}

Add ceph osd(s)

    playback-ceph-deploy osd create --zap-disk --fs-type ext4 compute1.maas:/dev/sdb
    playback-ceph-deploy osd create --zap-disk --fs-type ext4 compute1.maas:/dev/sdc
    playback-ceph-deploy osd create --zap-disk --fs-type ext4 compute2.maas:/dev/sdb
    playback-ceph-deploy osd create --zap-disk --fs-type ext4 compute2.maas:/dev/sdc
    playback-ceph-deploy osd create --zap-disk --fs-type ext4 compute3.maas:/dev/sdb
    playback-ceph-deploy osd create --zap-disk --fs-type ext4 compute3.maas:/dev/sdc
    playback-ceph-deploy osd create --zap-disk --fs-type ext4 compute4.maas:/dev/sdb
    playback-ceph-deploy osd create --zap-disk --fs-type ext4 compute4.maas:/dev/sdc
    playback-ceph-deploy osd create --zap-disk --fs-type ext4 compute5.maas:/dev/sdb
    playback-ceph-deploy osd create --zap-disk --fs-type ext4 compute5.maas:/dev/sdc

Sync admin key

    playback-ceph-deploy admin playback.maas controller1.maas controller2.maas controller3.maas compute1.maas compute2.maas compute3.maas compute4.maas compute5.maas compue6.maas comupte7.maas compute8.maas compute9.maas compute10.maas
    ssh {ceph-client-node} sudo chmod +r /etc/ceph/ceph.client.admin.keyring

Create osd pool for cinder and running instance

    ceph osd pool create volumes 512
    ceph osd pool create vms 512

Setup ceph client authentication

    ceph auth get-or-create client.cinder mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=volumes, allow rwx pool=vms'

Add the keyrings for `client.cinder` to appropriate nodes and change their ownership

    ceph auth get-or-create client.cinder | ssh {CINDER-VOLUME-NODE} sudo tee /etc/ceph/ceph.client.cinder.keyring
    ssh {CINDER-VOLUME-NODE} sudo chown cinder:cinder /etc/ceph/ceph.client.cinder.keyring

Nodes running `nova-compute` need the keyring file for the `nova-compute` process

    ceph auth get-or-create client.cinder | ssh {COMPUTE-NODE} sudo tee /etc/ceph/ceph.client.cinder.keyring

They also need to store the secret key of the `client.cinder user` in `libvirt`. The libvirt process needs it to access the cluster while attaching a block device from Cinder.
Create a temporary copy of the secret key on the nodes running `nova-compute`

    ceph auth get-key client.cinder | ssh {COMPUTE-NODE} tee client.cinder.key

Then, on the `compute nodes`, add the secret key to `libvirt` and remove the temporary copy of the key(the uuid is the same as your --rbd-secret-uuid option, you have to save the uuid for later)

    uuidgen
    457eb676-33da-42ec-9a8c-9293d545c337

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

Now on every compute nodes edit your Ceph configuration file, add the client section

    [client]
    rbd cache = true
    rbd cache writethrough until flush = true
    rbd concurrent management ops = 20


If you want to remove osd

    ssh {OSD-NODE} sudo stop ceph-mon-all && sudo stop ceph-osd-all
    ceph osd out {OSD-NUM}
    ceph osd crush remove osd.{OSD-NUM}
    ceph auth del osd.{OSD-NUM}
    ceph osd rm {OSD-NUM}
    ceph osd crush remove {HOST}

If you want to remove monitor

    ceph mon remove {MON-ID}