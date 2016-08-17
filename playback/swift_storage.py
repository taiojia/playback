from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
from tqdm import *
import sys
from playback.templates.rsyncd_conf import conf_rsyncd_conf
from playback.templates.rsync import conf_rsync
from playback.templates.account_server_conf import conf_account_server_conf
from playback.templates.container_server_conf import conf_container_server_conf
from playback.templates.object_server_conf import conf_object_server_conf
from playback import __version__
from playback import common

class SwiftStorage(common.Common):
    """
    Deploy swift storage node

    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    :examples:

        .. code-block:: python
            
            # create storage instances
            swift_storage1 = SwiftStorage(user='ubuntu', hosts=['compute1'])
            swift_storage2 = SwiftStorage(user='ubuntu', hosts=['compute2'])

            # prepare disks on storage nodes
            swift_storage1.prepare_disks('sdb,sdc,sdd,sde')
            swift_storage2.prepare_disks('sdb,sdc,sdd,sde')

            # install swift storage
            swift_storage1.install(
                address='192.168.1.11'
                bind_ip='192.168.1.11'
            )
            swift_storage2.install(
                address='192.168.1.12'
                bind_ip='192.168.1.12'
            )

            # create a ring instance
            ring = SwiftStorage(user='ubuntu', hosts=['controller1'])

            # create account ring
            ring.create_account_builder_file(
                partitions=10,
                replicas=3,
                moving=1
            )
            ring.account_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sdb',
                weight=100
            )
            ring.account_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sdc',
                weight=100
            )
            ring.account_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sdd',
                weight=100
            )
            ring.account_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sde',
                weight=100
            )
            ring.account_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sdb',
                weight=100
            )
            ring.account_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sdc',
                weight=100
            )
            ring.account_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sdd',
                weight=100
            )
            ring.account_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sde',
                weight=100
            )
            ring.account_builder_rebalance()

            # create container ring
            ring.create_container_builder_file(
                partitions=10,
                replicas=3,
                moving=1
            )
            ring.container_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sdb',
                weight=100
            )
            ring.container_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sdc',
                weight=100
            )
            ring.container_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sdd',
                weight=100
            )
            ring.container_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sde',
                weight=100
            )
            ring.container_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sdb',
                weight=100
            )
            ring.container_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sdc',
                weight=100
            )
            ring.container_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sdd',
                weight=100
            )
            ring.container_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sde',
                weight=100
            )
            ring.container_builder_rebalance()

            # create object ring
            ring.create_object_builder_file(
                partitions=10,
                replicas=3,
                moving=1
            )
            ring.object_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sdb',
                weight=100
            )
            ring.object_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sdc',
                weight=100
            )
            ring.object_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sdd',
                weight=100
            )
            ring.object_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.11',
                device='sde',
                weight=100
            )
            ring.object_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sdb',
                weight=100
            )
            ring.object_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sdc',
                weight=100
            )
            ring.object_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sdd',
                weight=100
            )
            ring.object_builder_add(
                region=1,
                zone=1,
                ip='192.168.1.12',
                device='sde',
                weight=100
            )
            ring.object_builder_rebalance()

            # sync the builder file from controller node to each storage node and other any proxy node
            ring.sync_builder_file(
                hosts=['controller2', 'compute1', 'compute2']
            )

            # finalize installation on all nodes
            from playback.swift import Swift
            finalize = Swift(user='ubuntu', hosts=['controller1','controller2', 'compute1', 'compute2'])
            finalize.finalize_install(
                swift_hash_path_suffix='changeme',
                swift_hash_path_prefix='changeme'
            )
    """

    def _prepare_disks(self, disks_name):
        """format disks to xfs and mount it"""
        fstab = '/etc/fstab'
        for disk in tqdm(disks_name.split(',')):
            sudo('umount /dev/{0}'.format(disk), warn_only=True)
            if sudo('mkfs.xfs -f /dev/{0}'.format(disk), warn_only=True).failed:
                sudo('apt-get update')
                sudo('apt-get -y install xfsprogs')
                sudo('mkfs.xfs -f /dev/{0}'.format(disk))
            sudo('mkdir -p /srv/node/{0}'.format(disk))
            files.append(fstab, '/dev/{0} /srv/node/{1} xfs noatime,nodiratime,nobarrier,logbufs=8 0 2'.format(disk,disk), use_sudo=True)
            sudo('mount /srv/node/{0}'.format(disk))

    def prepare_disks(self, *args, **kwargs):
        """
        Prepare the disks for storage

        :param disks_name: the device name, e.g. `sdb,sdc`
        :returns: None
        """
        return execute(self._prepare_disks, *args, **kwargs)

    def _install(self, address, bind_ip):
        print red(env.host_string + ' | Install the supporting utility packages')
        sudo('apt-get update')
        sudo('apt-get -y install xfsprogs rsync')

        print red(env.host_string + ' | Update /etc/rsyncd.conf')
        with open('tmp_rsyncd_conf_' + env.host_string, 'w') as f:
            f.write(conf_rsyncd_conf)
        files.upload_template(filename='tmp_rsyncd_conf_' + env.host_string,
                              destination='/etc/rsyncd.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'address': address})
        os.remove('tmp_rsyncd_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/default/rsync')
        with open('tmp_rsync_' + env.host_string, 'w') as f:
            f.write(conf_rsync)
        files.upload_template(filename='tmp_rsync_' + env.host_string,
                              destination='/etc/default/rsync',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_rsync_' + env.host_string)

        print red(env.host_string + ' | Start the rsync service')
        if sudo('service rsync start', warn_only=True).failed:
            sudo('service rsync restart')

        print red(env.host_string + ' | Install swift storage')
        sudo('apt-get -y install swift swift-account swift-container swift-object')

        print red(env.host_string + ' | Update /etc/swift/account-server.conf')
        with open('tmp_account_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_account_server_conf)
        files.upload_template(filename='tmp_account_server_conf_' + env.host_string,
                              destination='/etc/swift/account-server.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'bind_ip': bind_ip})
        os.remove('tmp_account_server_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/swift/container-server.conf')
        with open('tmp_container_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_container_server_conf)
        files.upload_template(filename='tmp_container_server_conf_' + env.host_string,
                              destination='/etc/swift/container-server.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'bind_ip': bind_ip})
        os.remove('tmp_container_server_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/swift/object-server.conf')
        with open('tmp_object_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_object_server_conf)
        files.upload_template(filename='tmp_object_server_conf_' + env.host_string,
                              destination='/etc/swift/object-server.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'bind_ip': bind_ip})
        os.remove('tmp_object_server_conf_' + env.host_string)

        print red(env.host_string + ' | Ensure proper ownership of the mount point directory structure')
        sudo('chown -R swift:swift /srv/node')

        print red(env.host_string + ' | Create the recon directory and ensure proper ownership of it')
        sudo('mkdir -p /var/cache/swift')
        sudo('chown -R root:swift /var/cache/swift')
        sudo('chmod -R 755 /var/cache/swift')

    def install(self, *args, **kwargs):
        """
        Install swift storage

        :param address: the management interface ip for rsync
        :param bind_ip: the management interface ip for swift storage binding
        :returns: None
        """
        return execute(self._install, *args, **kwargs)

    @runs_once
    def _create_account_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder account.builder create {0} {1} {2}'.format(partitions, replicas, moving))

    def create_account_builder_file(self, *args, **kwargs):
        """
        Create account ring
        
        :param partitions: 2^10 (1024) maximum partitions e.g. `10`
        :param replicas: 3 replicas of each object e.g. `3`
        :param moving: 1 hour minimum time between moving a partition more than once e.g. `1`
        :returns: None
        """
        return execute(self._create_account_builder_file, *args, **kwargs)

    @runs_once
    def _account_builder_add(self, region, zone, ip, device, weight):
        with cd('/etc/swift'):
            sudo('swift-ring-builder account.builder add --region {0} --zone {1} --ip {2} --port 6002 --device {3} --weight {4}'.format(region,
                                                                                                                                        zone,
                                                                                                                                        ip,
                                                                                                                                        device,
                                                                                                                                        weight))
            print red(env.host_string + ' | Verify the ring contents')
            sudo('swift-ring-builder account.builder')
             
    def account_builder_add(self, *args, **kwargs):
        """
        Add each storage node to the account ring

        :param region: swift storage region e.g. `1`
        :param zone: swift storage zone e.g. `1`
        :param ip: the IP address of the management network on the each storage node e.g. `STORAGE_NODE_IP`
        :param device: a storage device name on the same storage node e.g. `sdb`
        :param weight: the storage device weight e.g. `100`
        :returns: None
        """
        return execute(self._account_builder_add, *args, **kwargs)

    @runs_once
    def _account_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder account.builder rebalance')

    def account_builder_rebalance(self):
        """
        Rebalance account builder
        
        :returns: None
        """
        return execute(self._account_builder_rebalance)

    @runs_once
    def _create_container_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder container.builder create {0} {1} {2}'.format(partitions, replicas, moving))

    def create_container_builder_file(self, *args, **kwargs):
        """
        Create container ring

        :param partitions: 2^10 (1024) maximum partitions e.g. `10`
        :param replicas: 3 replicas of each object e.g. `3`
        :param moving: 1 hour minimum time between moving a partition more than once e.g. `1`
        :returns: None
        """
        return execute(self._create_container_builder_file, *args, **kwargs)

    @runs_once
    def _container_builder_add(self, region, zone, ip, device, weight):
        with cd('/etc/swift'):
            sudo('swift-ring-builder container.builder add --region {0} --zone {1} --ip {2} --port 6001 --device {3} --weight {4}'.format(region,
                                                                                                                                        zone,
                                                                                                                                        ip,
                                                                                                                                        device,
                                                                                                                                        weight))
            print red(env.host_string + ' | Verify the ring contents')
            sudo('swift-ring-builder container.builder')
            
    def container_builder_add(self, *args, **kwargs):
        """
        Add each storage node to the container ring

        :param region: swift storage region e.g. `1`
        :param zone: swift storage zone e.g. `1`
        :param ip: the IP address of the management network on the storage node e.g. `STORAGE_NODE_IP`
        :param device: a storage device name on the same storage node e.g. `sdb`
        :param weight: the storage device weight e.g. `100`
        :returns: None
        """
        return execute(self._container_builder_add, *args, **kwargs)

    @runs_once
    def _container_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder container.builder rebalance')

    def container_builder_rebalance(self):
        """
        Rebalance container builder

        :returns: None
        """
        return execute(self._container_builder_rebalance)

    @runs_once
    def _create_object_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder object.builder create {0} {1} {2}'.format(partitions, replicas, moving))

    def create_object_builder_file(self, *args, **kwargs):
        """
        Create object ring

        :param partitions: 2^10 (1024) maximum partitions e.g. `10`
        :param replicas: 3 replicas of each object e.g. `3`
        :param moving: 1 hour minimum time between moving a partition more than once e.g. `1`
        :returns: None
        """
        return execute(self._create_object_builder_file, *args, **kwargs)

    @runs_once
    def _object_builder_add(self, region, zone, ip, device, weight):
        with cd('/etc/swift'):
            sudo('swift-ring-builder object.builder add --region {0} --zone {1} --ip {2} --port 6000 --device {3} --weight {4}'.format(region,
                                                                                                                                        zone,
                                                                                                                                        ip,
                                                                                                                                        device,
                                                                                                                                        weight))
            print red(env.host_string + ' | Verify the ring contents')
            sudo('swift-ring-builder object.builder')

    def object_builder_add(self, *args, **kwargs):
        """
        Add each storage node to the object ring

        :param region: swift storage region e.g. `1`
        :param zone: swift storage zone e.g. `1`
        :param ip: the IP address of the management network on the storage node e.g. `STORAGE_NODE_IP`
        :param device: a storage device name on the same storage node e.g. `sdb`
        :param weight: the storage device weight e.g. `100`
        :returns: None
        """
        return execute(self._object_builder_add, *args, **kwargs)

    @runs_once
    def _object_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder object.builder rebalance')
    
    def object_builder_rebalance(self):
        """
        Rebalance object builder

        :returns: None
        """
        return execute(self._object_builder_rebalance)

    def _get_builder_file(self):
        get('/etc/swift/account.ring.gz', './account.ring.gz')
        get('/etc/swift/container.ring.gz', './container.ring.gz')
        get('/etc/swift/object.ring.gz', './object.ring.gz')

    def get_builder_file(self):
        """
        Copy *.ring.gz to local

        :returns: None
        """
        return execute(self._get_builder_file)

    def _sync_builder_file(self):
        put('./account.ring.gz', '/etc/swift/account.ring.gz', use_sudo=True)
        put('./container.ring.gz', '/etc/swift/container.ring.gz', use_sudo=True)
        put('./object.ring.gz', '/etc/swift/object.ring.gz', use_sudo=True)

    def sync_builder_file(self, hosts):
        """
        Copy the account.ring.gz, container.ring.gz, and object.ring.gz files from local to the /etc/swift directory on each storage node and any additional nodes running the proxy service

        :returns: None
        """
        return execute(self._sync_builder_file, hosts=hosts)
        
