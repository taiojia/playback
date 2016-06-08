from fabric.api import *
from fabric.contrib import files
from fabric.tasks import Task
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
from tqdm import *
import sys
from playback.cli import cli_description
from playback.swift_storage_conf import conf_rsyncd_conf, conf_rsync, conf_account_server_conf, conf_container_server_conf, conf_object_server_conf
from playback import __version__

parser = argparse.ArgumentParser(description=cli_description+'this command used for provision Swift Storage')
parser.add_argument('-v', '--version',
                   action='version',
                   version=__version__)
parser.add_argument('--user', 
                    help='the target user', 
                    action='store', 
                    default='ubuntu', 
                    dest='user')
parser.add_argument('--hosts', 
                    help='the target address', 
                    action='store', 
                    dest='hosts')
subparsers = parser.add_subparsers(dest='subparser_name')
prepare_disks = subparsers.add_parser('prepare-disks',
                                      help='prepare the disks for storage')
prepare_disks.add_argument('--name',
                           help='the device name, e.g. sdb,sdc',
                           action='store',
                           default=None,
                           dest='name')

install = subparsers.add_parser('install',
                                help='install swift storage')
install.add_argument('--address', 
                    help='the management interface ip for rsync', 
                    action='store', 
                    dest='address')
install.add_argument('--bind-ip', 
                    help='the management interface ip for swift storage binding', 
                    action='store', 
                    dest='bind_ip')

create_account_builder_file = subparsers.add_parser('create-account-builder-file',
                                                    help='create account ring')
create_account_builder_file.add_argument('--partitions', 
                                        help='2^10 (1024) maximum partitions e.g. 10', 
                                        action='store', 
                                        default=None,
                                        dest='partitions')
create_account_builder_file.add_argument('--replicas', 
                                        help='3 replicas of each object e.g. 3', 
                                        action='store', 
                                        default=None,
                                        dest='replicas')
create_account_builder_file.add_argument('--moving', 
                                        help='1 hour minimum time between moving a partition more than once e.g. 1', 
                                        action='store',
                                        default=None, 
                                        dest='moving')
account_builder_add = subparsers.add_parser('account-builder-add',
                                            help='Add each storage node to the account ring')
account_builder_add.add_argument('--region', 
                                help='swift storage region e.g. 1', 
                                action='store', 
                                default=None,
                                dest='region')
account_builder_add.add_argument('--zone', 
                                help='swift storage zone e.g. 1', 
                                action='store', 
                                default=None,
                                dest='zone')
account_builder_add.add_argument('--ip', 
                                help='the IP address of the management network on the storage node e.g. STORAGE_NODE_IP', 
                                action='store', 
                                default=None,
                                dest='ip')
account_builder_add.add_argument('--device', 
                                help='a storage device name on the same storage node e.g. sdb', 
                                action='store', 
                                default=None,
                                dest='device')
account_builder_add.add_argument('--weight',
                                help='the storage device weight e.g. 100',
                                action='store',
                                default=None,
                                dest='weight')

create_container_builder_file = subparsers.add_parser('create-container-builder-file',
                                                      help='create container ring')
create_container_builder_file.add_argument('--partitions', 
                                           help='2^10 (1024) maximum partitions e.g. 10', 
                                           action='store', 
                                           default=None,
                                           dest='partitions')
create_container_builder_file.add_argument('--replicas', 
                                           help='3 replicas of each object e.g. 3', 
                                           action='store', 
                                           default=None,
                                           dest='replicas')
create_container_builder_file.add_argument('--moving', 
                                           help='1 hour minimum time between moving a partition more than once e.g. 1', 
                                           action='store',
                                           default=None, 
                                           dest='moving')

container_builder_add = subparsers.add_parser('container-builder-add',
                                              help='Add each storage node to the container ring')
container_builder_add.add_argument('--region', 
                                help='swift storage region e.g. 1', 
                                action='store', 
                                default=None,
                                dest='region')
container_builder_add.add_argument('--zone', 
                                help='swift storage zone e.g. 1', 
                                action='store', 
                                default=None,
                                dest='zone')
container_builder_add.add_argument('--ip', 
                                help='the IP address of the management network on the storage node e.g. STORAGE_NODE_IP', 
                                action='store', 
                                default=None,
                                dest='ip')
container_builder_add.add_argument('--device', 
                                help='a storage device name on the same storage node e.g. sdb', 
                                action='store', 
                                default=None,
                                dest='device')
container_builder_add.add_argument('--weight',
                                help='the storage device weight e.g. 100',
                                action='store',
                                default=None,
                                dest='weight')

create_object_builder_file = subparsers.add_parser('create-object-builder-file',
                                                   help='create object ring')
create_object_builder_file.add_argument('--partitions', 
                                        help='2^10 (1024) maximum partitions e.g. 10', 
                                        action='store', 
                                        default=None,
                                        dest='partitions')
create_object_builder_file.add_argument('--replicas', 
                                        help='3 replicas of each object e.g. 3', 
                                        action='store', 
                                        default=None,
                                        dest='replicas')
create_object_builder_file.add_argument('--moving', 
                                        help='1 hour minimum time between moving a partition more than once e.g. 1', 
                                        action='store',
                                        default=None, 
                                        dest='moving')

object_builder_add = subparsers.add_parser('object-builder-add',
                                           help='Add each storage node to the object ring')
object_builder_add.add_argument('--region', 
                                help='swift storage region e.g. 1', 
                                action='store', 
                                default=None,
                                dest='region')
object_builder_add.add_argument('--zone', 
                                help='swift storage zone e.g. 1', 
                                action='store', 
                                default=None,
                                dest='zone')
object_builder_add.add_argument('--ip', 
                                help='the IP address of the management network on the storage node e.g. STORAGE_NODE_IP', 
                                action='store', 
                                default=None,
                                dest='ip')
object_builder_add.add_argument('--device', 
                                help='a storage device name on the same storage node e.g. sdb', 
                                action='store', 
                                default=None,
                                dest='device')
object_builder_add.add_argument('--weight',
                                help='the storage device weight e.g. 100',
                                action='store',
                                default=None,
                                dest='weight')
sync_builder_file = subparsers.add_parser('sync-builder-file',
                                          help='copy the account.ring.gz, container.ring.gz, and object.ring.gz files to the /etc/swift directory on each storage node and any additional nodes running the proxy service')
sync_builder_file.add_argument('--to', 
                               help='the target hosts where the *.ring.gz file to be added', 
                               action='store', 
                               default=None,
                               dest='to')
account_builder_rebalance = subparsers.add_parser('account-builder-rebalance',
                                                  help='Rebalance the account ring')
container_builder_rebalance = subparsers.add_parser('container-builder-rebalance',
                                                    help='Rebalance the container ring')
object_builder_rebalance = subparsers.add_parser('object-builder-rebalance',
                                                 help='Rebalance the object ring')

args = parser.parse_args()




class SwiftStorage(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(SwiftStorage, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _prepare_disks(self, prepare_disks):
        """format disks to xfs and mount it"""
        fstab = '/etc/fstab'
        for disk in tqdm(prepare_disks.split(',')):
            sudo('umount /dev/{0}'.format(disk), warn_only=True)
            if sudo('mkfs.xfs -f /dev/{0}'.format(disk), warn_only=True).failed:
                sudo('apt-get update')
                sudo('apt-get -y install xfsprogs')
                sudo('mkfs.xfs -f /dev/{0}'.format(disk))
            sudo('mkdir -p /srv/node/{0}'.format(disk))
            files.append(fstab, '/dev/{0} /srv/node/{1} xfs noatime,nodiratime,nobarrier,logbufs=8 0 2'.format(disk,disk), use_sudo=True)
            sudo('mount /srv/node/{0}'.format(disk))


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
                              context={'address': address})
        os.remove('tmp_rsyncd_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/default/rsync')
        with open('tmp_rsync_' + env.host_string, 'w') as f:
            f.write(conf_rsync)
        files.upload_template(filename='tmp_rsync_' + env.host_string,
                              destination='/etc/default/rsync',
                              use_jinja=True,
                              use_sudo=True,)
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
                              context={'bind_ip': bind_ip})
        os.remove('tmp_account_server_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/swift/container-server.conf')
        with open('tmp_container_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_container_server_conf)
        files.upload_template(filename='tmp_container_server_conf_' + env.host_string,
                              destination='/etc/swift/container-server.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'bind_ip': bind_ip})
        os.remove('tmp_container_server_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/swift/object-server.conf')
        with open('tmp_object_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_object_server_conf)
        files.upload_template(filename='tmp_object_server_conf_' + env.host_string,
                              destination='/etc/swift/object-server.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'bind_ip': bind_ip})
        os.remove('tmp_object_server_conf_' + env.host_string)

        print red(env.host_string + ' | Ensure proper ownership of the mount point directory structure')
        sudo('chown -R swift:swift /srv/node')

        print red(env.host_string + ' | Create the recon directory and ensure proper ownership of it')
        sudo('mkdir -p /var/cache/swift')
        sudo('chown -R root:swift /var/cache/swift')

    def _create_account_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder account.builder create {0} {1} {2}'.format(partitions, replicas, moving))


    def _account_builder_add(self, region, zone, ip, device, weight):
        with cd('/etc/swift'):
            sudo('swift-ring-builder account.builder add --region {0} --zone {1} --ip {2} --port 6002 --device {3} --weight {4}'.format(region,
                                                                                                                                        zone,
                                                                                                                                        ip,
                                                                                                                                        device,
                                                                                                                                        weight))
            print red(env.host_string + ' | Verify the ring contents')
            sudo('swift-ring-builder account.builder')
             
    def _account_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder account.builder rebalance')


    def _create_container_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder container.builder create {0} {1} {2}'.format(partitions, replicas, moving))

    def _container_builder_add(self, region, zone, ip, device, weight):
        with cd('/etc/swift'):
            sudo('swift-ring-builder container.builder add --region {0} --zone {1} --ip {2} --port 6001 --device {3} --weight {4}'.format(region,
                                                                                                                                        zone,
                                                                                                                                        ip,
                                                                                                                                        device,
                                                                                                                                        weight))
            print red(env.host_string + ' | Verify the ring contents')
            sudo('swift-ring-builder container.builder')
            
    def _container_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder container.builder rebalance')

    def _create_object_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder object.builder create {0} {1} {2}'.format(partitions, replicas, moving))

    def _object_builder_add(self, region, zone, ip, device, weight):
        with cd('/etc/swift'):
            sudo('swift-ring-builder object.builder add --region {0} --zone {1} --ip {2} --port 6000 --device {3} --weight {4}'.format(region,
                                                                                                                                        zone,
                                                                                                                                        ip,
                                                                                                                                        device,
                                                                                                                                        weight))
            print red(env.host_string + ' | Verify the ring contents')
            sudo('swift-ring-builder object.builder')

    def _object_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder object.builder rebalance')
    
    def _get_builder_file(self):
        get('/etc/swift/account.ring.gz', './account.ring.gz')
        get('/etc/swift/container.ring.gz', './container.ring.gz')
        get('/etc/swift/object.ring.gz', './object.ring.gz')

    def _sync_builder_file(self):
        put('./account.ring.gz', '/etc/swift/account.ring.gz', use_sudo=True)
        put('./container.ring.gz', '/etc/swift/container.ring.gz', use_sudo=True)
        put('./object.ring.gz', '/etc/swift/object.ring.gz', use_sudo=True)
        



def main():
    try:
        target = SwiftStorage(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')
        parser.print_help()
        sys.exit(1)

    if args.subparser_name == 'prepare-disks':
        execute(target._prepare_disks, 
                args.name)
    if args.subparser_name == 'install':
        execute(target._install,
                args.address, 
                args.bind_ip)
    if args.subparser_name == 'create-account-builder-file':
        execute(target._create_account_builder_file,
                args.partitions, 
                args.replicas, 
                args.moving)
    if args.subparser_name == 'account-builder-add':
        execute(target._account_builder_add,
                args.region, 
                args.zone, 
                args.ip, 
                args.device, 
                args.weight)
    if args.subparser_name == 'account-builder-rebalance':
        execute(target._account_builder_rebalance)
    if args.subparser_name == 'create-container-builder-file':
        execute(target._create_container_builder_file,
                args.partitions,
                args.replicas,
                args.moving)
    if args.subparser_name == 'container-builder-add':
        execute(target._container_builder_add,
                args.region, 
                args.zone, 
                args.ip, 
                args.device, 
                args.weight)
    if args.subparser_name == 'container-builder-rebalance':
        execute(target._container_builder_rebalance)
    if args.subparser_name == 'create-object-builder-file':
        execute(target._create_object_builder_file,
                args.partitions,
                args.replicas,
                args.moving)
    if args.subparser_name == 'object-builder-add':
        execute(target._object_builder_add,
                args.region, 
                args.zone, 
                args.ip, 
                args.device, 
                args.weight)
    if args.subparser_name == 'object-builder-rebalance':
        execute(target._object_builder_rebalance)
    if args.subparser_name == 'sync-builder-file':
        execute(target._get_builder_file)
        execute(target._sync_builder_file, hosts=args.to.split(','))
        os.remove('account.ring.gz')
        os.remove('container.ring.gz')
        os.remove('object.ring.gz')
    

if __name__ == '__main__':
    main()