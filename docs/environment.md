#### Requirements
* The OpenStack bare metal hosts are in MAAS environment(recommend)
* All hosts are two NICs at least(external and internal)
* We assume that you have ceph installed, the cinder bachend default using ceph, the running instace default to using ceph as it's local storage. About ceph please visit: http://docs.ceph.com/docs/master/rbd/rbd-openstack/ or see the (Option)Ceph Guide below.
* nova user can be login to each compute node via ssh passwordless
* The playback node is the same as ceph-deploy node where can be login to each openstack node passwordless
* The playback node default using ~/.ssh/id_rsa ssh private key to logon remote server

