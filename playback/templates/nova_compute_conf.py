conf_nova_compute_conf = """[DEFAULT]
compute_driver = libvirt.LibvirtDriver
glance_api_version = 2
[libvirt]
virt_type = kvm
inject_password = False
inject_key = False
inject_partition = -2
images_type = rbd
images_rbd_pool = vms
images_rbd_ceph_conf = /etc/ceph/ceph.conf
rbd_user = cinder
rbd_secret_uuid = {{ rbd_secret_uuid }}
disk_cachemodes= "network=writeback"
block_migration_flag = "VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_LIVE,VIR_MIGRATE_NON_SHARED_INC"
live_migration_flag = "VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_LIVE,VIR_MIGRATE_PERSIST_DEST,VIR_MIGRATE_TUNNELLED"
live_migration_uri = qemu+tcp://%s/system
"""
