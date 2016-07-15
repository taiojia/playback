# OpenStack Environment

## Requirements

* The OpenStack bare metal hosts are in MAAS environment(recommend)
* All hosts are two NICs at least(external and internal)
* We assume that you have ceph installed, the cinder bachend default using ceph, the running instace default to using ceph as it's local storage. About ceph please visit: http://docs.ceph.com/docs/master/rbd/rbd-openstack/ or see the (Option)Ceph Guide below.
* For resize instance nova user can be login to each compute node via ssh passwordless(include sudo), and all compute nodes need to restart libvirt-bin to enable live migration
* The playback node is the same as ceph-deploy node where can be login to each openstack node passwordless and sudo-passwordless
* The playback node default using ~/.ssh/id_rsa ssh private key to logon remote server
* You need to restart the `nova-compute`, `cinder-volume` and `glance-api` services to finalize the installation if you have selected the ceph as that backend
* Playback support consistency groups for future use but the default LVM and Ceph driver does not support consistency groups yet because the consistency technology is not available at that storage level

## Define environment

We define an environment with 10 nodes which three controllers and two computes, all storage components on the compute nodes. We assume that you have installed maas and ceph on that servers.

| Roles         | IP/FQDN           | Components                                                                                    |
| ------------- | ----------------- | --------------------------------------------------------------------------------------------- |
| deploy node   | playback.maas     | playback maas                                                                                 |
| haproxy       | haproxy1.maas     | haproxy keepalived                                                                            |
| haproxy       | haproxy2.maas     | haproxy keepalived                                                                            |
| controller    | controller1.maas  | db rabbitmq keystone glance nova-api neutron-api horizon cinder-api cinder-volume swift-proxy |
| controller    | controller2.maas  | db rabbitmq keystone glance nova-api neutron-api horizon cinder-api cinder-volume swift-proxy |
| controller    | controller3.maas  | db rabbitmq keystone glance nova-api neutron-api horizon cinder-api cinder-volume swift-proxy |
| compute       | compute1.maas     | nova-compute ceph-osd ceph-mon                                                                |
| compute       | compute2.maas     | nova-compute ceph-osd ceph-mon                                                                |
| compute       | compute3.maas     | nova-compute ceph-osd ceph-mon                                                                |
| compute       | compute4.maas     | nova-compute ceph-osd ceph-mon                                                                |
| compute       | compute5.maas     | nova-compute ceph-osd ceph-mon                                                                |
| compute       | compute6.maas     | nova-compute swift-storage                                                                    |
| compute       | compute7.maas     | nova-compute swift-storage                                                                    |
| compute       | compute8.maas     | nova-compute swift-storage                                                                    |
| compute       | compute9.maas     | nova-compute swift-storage                                                                    |
| compute       | compute10.maas    | nova-compute swift-storage                                                                    |

## Install playback

The playback.maas is that deployment node, we can install playback on it or using your bash on ubuntu on windows.

    ssh ubuntu@playback.maas
    sudo apt-get update
    sudo apt-get python-pip python-dev
    sudo pip install playback

If you are using bash on ubuntu on windows, do the following steps.

    bash
    sudo apt-get update
    sudo apt-get python-pip python-dev
    sudo pip install playback

## Prepare environment

Prepare the OpenStack environment.

(NOTE) DO NOT setup `eth1` in `/etc/network/interfaces`, Playback will appends `eth1` configurations to `/etc/network/interfaces`.

The following command will help you to prepare the OpenStack environment and all hosts will be rebooted no confirmed.

    env-deploy --user ubuntu --hosts \
    haproxy1.maas,\
    haproxy2.maas,\
    controller1.maas,\
    controller2.maas,\
    controller3.maas,\
    compute1.maas,\
    compute2.maas,\
    compute3.maas,\
    compute4.maas,\
    compute5.maas,\
    compute6.maas,\
    compute7.maas,\
    compute8.maas,\
    compute9.maas,\
    compute10.maas \
    prepare-host --public-interface eth1

Using `env-deploy --help` to see details.
