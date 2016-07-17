from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
from tqdm import *
import sys
from playback.cli import cli_description
from playback.templates.rsyncd_conf import conf_rsyncd_conf
from playback.templates.rsync import conf_rsync
from playback.templates.account_server_conf import conf_account_server_conf
from playback.templates.container_server_conf import conf_container_server_conf
from playback.templates.object_server_conf import conf_object_server_conf
from playback import __version__
from playback import common

class SwiftStorage(common.Common):

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
        return execute(self._install, *args, **kwargs)

    @runs_once
    def _create_account_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder account.builder create {0} {1} {2}'.format(partitions, replicas, moving))

    def create_account_builder_file(self, *args, **kwargs):
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
        return execute(self._account_builder_add, *args, **kwargs)

    @runs_once
    def _account_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder account.builder rebalance')

    def account_builder_rebalance(self):
        return execute(self._account_builder_rebalance)

    @runs_once
    def _create_container_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder container.builder create {0} {1} {2}'.format(partitions, replicas, moving))

    def create_container_builder_file(self, *args, **kwargs):
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
        return execute(self._container_builder_add, *args, **kwargs)

    @runs_once
    def _container_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder container.builder rebalance')

    def container_builder_rebalance(self):
        return execute(self._container_builder_rebalance)

    @runs_once
    def _create_object_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder object.builder create {0} {1} {2}'.format(partitions, replicas, moving))

    def create_object_builder_file(self, *args, **kwargs):
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
        return execute(self._object_builder_add, *args, **kwargs)

    @runs_once
    def _object_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder object.builder rebalance')
    
    def object_builder_rebalance(self):
        return execute(self._object_builder_rebalance)

    def _get_builder_file(self):
        get('/etc/swift/account.ring.gz', './account.ring.gz')
        get('/etc/swift/container.ring.gz', './container.ring.gz')
        get('/etc/swift/object.ring.gz', './object.ring.gz')

    def get_builder_file(self):
        return execute(self._get_builder_file)

    def _sync_builder_file(self):
        put('./account.ring.gz', '/etc/swift/account.ring.gz', use_sudo=True)
        put('./container.ring.gz', '/etc/swift/container.ring.gz', use_sudo=True)
        put('./object.ring.gz', '/etc/swift/object.ring.gz', use_sudo=True)

    def sync_builder_file(self):
        return execute(self.sync_builder_file)
        
