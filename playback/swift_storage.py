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

    @runs_once
    def _create_account_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder account.builder create {0} {1} {2}'.format(partitions, replicas, moving))

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
             
    @runs_once
    def _account_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder account.builder rebalance')


    @runs_once
    def _create_container_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder container.builder create {0} {1} {2}'.format(partitions, replicas, moving))

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
            
    @runs_once
    def _container_builder_rebalance(self):
        with cd('/etc/swift'):
            print red(env.host_string + ' | Rebalance the ring')
            sudo('swift-ring-builder container.builder rebalance')

    @runs_once
    def _create_object_builder_file(self, partitions, replicas, moving):
        with cd('/etc/swift'):
            sudo('swift-ring-builder object.builder create {0} {1} {2}'.format(partitions, replicas, moving))

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

    @runs_once
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
        
def prepare_disks_subparser(s):
    prepare_disks_parser = s.add_parser('prepare-disks',
                                        help='prepare the disks for storage')
    prepare_disks_parser.add_argument('--name',
                                        help='the device name, e.g. sdb,sdc',
                                        action='store',
                                        default=None,
                                        dest='name')
    return prepare_disks_parser

def install_subparser(s):
    install_parser = s.add_parser('install', help='install swift storage')
    install_parser.add_argument('--address', 
                                help='the management interface ip for rsync', 
                                action='store', 
                                dest='address')
    install_parser.add_argument('--bind-ip', 
                                help='the management interface ip for swift storage binding', 
                                action='store', 
                                dest='bind_ip')
    return install_parser

def create_account_builder_file_subparser(s):
    create_account_builder_file_parser = s.add_parser('create-account-builder-file', help='create account ring')
    create_account_builder_file_parser.add_argument('--partitions', 
                                                    help='2^10 (1024) maximum partitions e.g. 10', 
                                                    action='store', 
                                                    default=None,
                                                    dest='partitions')
    create_account_builder_file_parser.add_argument('--replicas', 
                                                    help='3 replicas of each object e.g. 3', 
                                                    action='store', 
                                                    default=None,
                                                    dest='replicas')
    create_account_builder_file_parser.add_argument('--moving', 
                                                    help='1 hour minimum time between moving a partition more than once e.g. 1', 
                                                    action='store',
                                                    default=None, 
                                                    dest='moving')
    return create_account_builder_file_parser

def account_builder_add_subparser(s):
    account_builder_add_parser= s.add_parser('account-builder-add', help='Add each storage node to the account ring')
    account_builder_add_parser.add_argument('--region', 
                                            help='swift storage region e.g. 1', 
                                            action='store', 
                                            default=None,
                                            dest='region')
    account_builder_add_parser.add_argument('--zone', 
                                            help='swift storage zone e.g. 1', 
                                            action='store', 
                                            default=None,
                                            dest='zone')
    account_builder_add_parser.add_argument('--ip', 
                                            help='the IP address of the management network on the storage node e.g. STORAGE_NODE_IP', 
                                            action='store', 
                                            default=None,
                                            dest='ip')
    account_builder_add_parser.add_argument('--device', 
                                            help='a storage device name on the same storage node e.g. sdb', 
                                            action='store', 
                                            default=None,
                                            dest='device')
    account_builder_add_parser.add_argument('--weight',
                                            help='the storage device weight e.g. 100',
                                            action='store',
                                            default=None,
                                            dest='weight')
    return account_builder_add_parser

def create_container_builder_file_subparser(s):
    create_container_builder_file_parser = s.add_parser('create-container-builder-file', help='create container ring')
    create_container_builder_file_parser.add_argument('--partitions', 
                                                        help='2^10 (1024) maximum partitions e.g. 10', 
                                                        action='store', 
                                                        default=None,
                                                        dest='partitions')
    create_container_builder_file_parser.add_argument('--replicas', 
                                                        help='3 replicas of each object e.g. 3', 
                                                        action='store', 
                                                        default=None,
                                                        dest='replicas')
    create_container_builder_file_parser.add_argument('--moving', 
                                                        help='1 hour minimum time between moving a partition more than once e.g. 1', 
                                                        action='store',
                                                        default=None, 
                                                        dest='moving')
    return create_container_builder_file_parser

def container_builder_add_subparser(s):
    container_builder_add_parser = s.add_parser('container-builder-add', help='Add each storage node to the container ring')
    container_builder_add_parser.add_argument('--region', 
                                                help='swift storage region e.g. 1', 
                                                action='store', 
                                                default=None,
                                                dest='region')
    container_builder_add_parser.add_argument('--zone', 
                                                help='swift storage zone e.g. 1', 
                                                action='store', 
                                                default=None,
                                                dest='zone')
    container_builder_add_parser.add_argument('--ip', 
                                                help='the IP address of the management network on the storage node e.g. STORAGE_NODE_IP', 
                                                action='store', 
                                                default=None,
                                                dest='ip')
    container_builder_add_parser.add_argument('--device', 
                                                help='a storage device name on the same storage node e.g. sdb', 
                                                action='store', 
                                                default=None,
                                                dest='device')
    container_builder_add_parser.add_argument('--weight',
                                                help='the storage device weight e.g. 100',
                                                action='store',
                                                default=None,
                                                dest='weight')
    return container_builder_add_parser

def create_object_builder_file_subparser(s):
    create_object_builder_file_parser = s.add_parser('create-object-builder-file', help='create object ring')
    create_object_builder_file_parser.add_argument('--partitions', 
                                                    help='2^10 (1024) maximum partitions e.g. 10', 
                                                    action='store', 
                                                    default=None,
                                                    dest='partitions')
    create_object_builder_file_parser.add_argument('--replicas', 
                                                    help='3 replicas of each object e.g. 3', 
                                                    action='store', 
                                                    default=None,
                                                    dest='replicas')
    create_object_builder_file_parser.add_argument('--moving', 
                                                    help='1 hour minimum time between moving a partition more than once e.g. 1', 
                                                    action='store',
                                                    default=None, 
                                                    dest='moving')
    return create_object_builder_file_parser

def object_builder_add_subparser(s):
    object_builder_add_parser = s.add_parser('object-builder-add', help='Add each storage node to the object ring')
    object_builder_add_parser.add_argument('--region', 
                                            help='swift storage region e.g. 1', 
                                            action='store', 
                                            default=None,
                                            dest='region')
    object_builder_add_parser.add_argument('--zone', 
                                            help='swift storage zone e.g. 1', 
                                            action='store', 
                                            default=None,
                                            dest='zone')
    object_builder_add_parser.add_argument('--ip', 
                                            help='the IP address of the management network on the storage node e.g. STORAGE_NODE_IP', 
                                            action='store', 
                                            default=None,
                                            dest='ip')
    object_builder_add_parser.add_argument('--device', 
                                            help='a storage device name on the same storage node e.g. sdb', 
                                            action='store', 
                                            default=None,
                                            dest='device')
    object_builder_add_parser.add_argument('--weight',
                                            help='the storage device weight e.g. 100',
                                            action='store',
                                            default=None,
                                            dest='weight')
    return object_builder_add_parser

def sync_builder_file_subparser(s):
    sync_builder_file_parser = s.add_parser('sync-builder-file',
                                            help='copy the account.ring.gz, container.ring.gz, and object.ring.gz files to the /etc/swift directory on each storage node and any additional nodes running the proxy service')
    sync_builder_file_parser.add_argument('--to', 
                                            help='the target hosts where the *.ring.gz file to be added', 
                                            action='store', 
                                            default=None,
                                            dest='to')
    return sync_builder_file_parser

def account_builder_rebalance_subparser(s):
    account_builder_rebalance_parser = s.add_parser('account-builder-rebalance', help='Rebalance the account ring')
    return account_builder_rebalance_parser

def container_builder_rebalance_subparser(s):
    container_builder_rebalance_parser = s.add_parser('container-builder-rebalance', help='Rebalance the container ring')
    return container_builder_rebalance_parser

def object_builder_rebalance_subparser(s):
    object_builder_rebalance_parser = s.add_parser('object-builder-rebalance', help='Rebalance the object ring')
    return object_builder_rebalance_parser

def make_target(args):
    try:
        target = SwiftStorage(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    return target

def prepare_disks(args):
    target = make_target(args)
    execute(target._prepare_disks, args.name)

def install(args):
    target = make_target(args)
    execute(target._install, args.address, args.bind_ip)

def create_account_builder_file(args):
    target = make_target(args)
    execute(target._create_account_builder_file, args.partitions, args.replicas, args.moving)

def account_builder_add(args):
    target = make_target(args)
    execute(target._account_builder_add, args.region, args.zone, 
            args.ip, args.device, args.weight)

def create_container_builder_file(args):
    target = make_target(args)
    execute(target._create_container_builder_file, args.partitions,
            args.replicas,
            args.moving)

def container_builder_add(args):
    target = make_target(args)
    execute(target._container_builder_add, args.region, 
            args.zone, args.ip, 
            args.device, args.weight)

def create_object_builder_file(args):
    target = make_target(args)
    execute(target._create_object_builder_file, args.partitions,
            args.replicas, args.moving)

def object_builder_add(args):
    target = make_target(args)
    execute(target._object_builder_add, args.region, args.zone, 
            args.ip, args.device, args.weight)

def sync_builder_file(args):
    target = make_target(args)
    execute(target._get_builder_file)
    execute(target._sync_builder_file, hosts=args.to.split(','))
    os.remove('account.ring.gz')
    os.remove('container.ring.gz')
    os.remove('object.ring.gz')

def account_builder_rebalance(args):
    target = make_target(args)
    execute(target._account_builder_rebalance)

def container_builder_rebalance(args):
    target = make_target(args)
    execute(target._container_builder_rebalance)

def object_builder_rebalance(args):
    target = make_target(args)
    execute(target._object_builder_rebalance)

def parser():
    p = argparse.ArgumentParser(prog='swift-storage-deploy', description=cli_description+'this command used for provision Swift Storage')
    p.add_argument('-v', '--version',
                    action='version',
                    version=__version__)
    p.add_argument('--user', 
                    help='the target user', 
                    action='store', 
                    default='ubuntu', 
                    dest='user')
    p.add_argument('--hosts', 
                    help='the target address', 
                    action='store', 
                    dest='hosts')
    p.add_argument('-i', '--key-filename', help='referencing file paths to SSH key files to try when connecting', action='store', dest='key_filename', default=None)
    p.add_argument('--password', help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password', default=None)

    s = p.add_subparsers(dest='subparser_name')

    def prepare_disks_f(args):
        prepare_disks(args)
    prepare_disks_parser = prepare_disks_subparser(s)
    prepare_disks_parser.set_defaults(func=prepare_disks_f)

    def install_f(args):
        install(args)
    install_parser = install_subparser(s)
    install_parser.set_defaults(func=install_f)

    def create_account_builder_file_f(args):
        create_account_builder_file(args)
    create_account_builder_file_parser = create_account_builder_file_subparser(s)
    create_account_builder_file_parser.set_defaults(func=create_account_builder_file_f)

    def account_builder_add_f(args):
        account_builder_add(args)
    account_builder_add_parser = account_builder_add_subparser(s)
    account_builder_add_parser.set_defaults(func=account_builder_add_f)

    def create_container_builder_file_f(args):
        create_container_builder_file(args)
    create_container_builder_file_parser = create_container_builder_file_subparser(s)
    create_container_builder_file_parser.set_defaults(func=create_container_builder_file_f)

    def container_builder_add_f(args):
        container_builder_add(args)
    container_builder_add_parser = container_builder_add_subparser(s)
    container_builder_add_parser.set_defaults(func=container_builder_add_f)

    def create_object_builder_file_f(args):
        create_object_builder_file(args)
    create_object_builder_file_parser = create_object_builder_file_subparser(s)
    create_object_builder_file_parser.set_defaults(func=create_object_builder_file_f)

    def object_builder_add_f(args):
        object_builder_add(args)
    object_builder_add_parser = object_builder_add_subparser(s)
    object_builder_add_parser.set_defaults(func=object_builder_add_f)

    def sync_builder_file_f(args):
        sync_builder_file(args)
    sync_builder_file_parser = sync_builder_file_subparser(s)
    sync_builder_file_parser.set_defaults(func=sync_builder_file_f)

    def account_builder_rebalance_f(args):
        account_builder_rebalance(args)
    account_builder_rebalance_parser = account_builder_rebalance_subparser(s)
    account_builder_rebalance_parser.set_defaults(func=account_builder_rebalance_f)

    def container_builder_rebalance_f(args):
        container_builder_rebalance(args)
    container_builder_rebalance_parser = container_builder_rebalance_subparser(s)
    container_builder_rebalance_parser.set_defaults(func=container_builder_rebalance_f)

    def object_builder_rebalance_f(args):
        object_builder_rebalance(args)
    object_builder_rebalance_parser = object_builder_rebalance_subparser(s)
    object_builder_rebalance_parser.set_defaults(func=object_builder_rebalance_f)

    return p

def main():
    p = parser()
    args = p.parse_args()
    if not hasattr(args, 'func'):
        p.print_help()
    else:
        # XXX on Python 3.3 we get 'args has no func' rather than short help.
        try:
            args.func(args)
            disconnect_all()
            return 0
        except Exception as e:
            sys.stderr.write(e.message)
    return 1

if __name__ == '__main__':
    main()