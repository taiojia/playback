import sys
import logging
import os
from playback.cli.cliutil import priority
from playback.api import SwiftStorage
from cliff.command import Command


def make_target(args):
    try:
        target = SwiftStorage(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename,
                              password=args.password)
    except AttributeError:
        sys.stderr.write('No hosts found. Please using --hosts param.')
        sys.exit(1)
    return target


def prepare_disks(args):
    target = make_target(args)
    target.prepare_disks(args.name)


def install(args):
    target = make_target(args)
    target.install(args.address, args.bind_ip)


def create_account_builder_file(args):
    target = make_target(args)
    target.create_account_builder_file(args.partitions, args.replicas, args.moving)


def account_builder_add(args):
    target = make_target(args)
    target.account_builder_add(args.region, args.zone,
                               args.ip, args.device, args.weight)


def create_container_builder_file(args):
    target = make_target(args)
    target.create_container_builder_file(args.partitions,
                                         args.replicas,
                                         args.moving)


def container_builder_add(args):
    target = make_target(args)
    target.container_builder_add(args.region,
                                 args.zone, args.ip,
                                 args.device, args.weight)


def create_object_builder_file(args):
    target = make_target(args)
    target.create_object_builder_file(args.partitions,
                                      args.replicas, args.moving)


def object_builder_add(args):
    target = make_target(args)
    target.object_builder_add(args.region, args.zone,
                              args.ip, args.device, args.weight)


def sync_builder_file(args):
    target = make_target(args)
    target.get_builder_file()
    target.sync_builder_file(hosts=args.to.split(','))
    os.remove('account.ring.gz')
    os.remove('container.ring.gz')
    os.remove('object.ring.gz')


def account_builder_rebalance(args):
    target = make_target(args)
    target.account_builder_rebalance()


def container_builder_rebalance(args):
    target = make_target(args)
    target.container_builder_rebalance()


def object_builder_rebalance(args):
    target = make_target(args)
    target.object_builder_rebalance()


class PrepareDisks(Command):
    """prepare the disks for storage"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PrepareDisks, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--name',
                            help='the device name, e.g. sdb,sdc',
                            action='store', default=None, dest='name')
        return parser

    def take_action(self, parsed_args):
        prepare_disks(parsed_args)


class Install(Command):
    """install swift storage"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Install, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--address',
                            help='the management interface ip for rsync',
                            action='store',
                            dest='address')
        parser.add_argument('--bind-ip',
                            help='the management interface ip for swift storage binding',
                            action='store',
                            dest='bind_ip')
        return parser

    def take_action(self, parsed_args):
        install(parsed_args)


class CreateAccountBuilderFile(Command):
    """create account ring"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateAccountBuilderFile, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--partitions',
                            help='2^10 (1024) maximum partitions e.g. 10',
                            action='store', default=None, dest='partitions')
        parser.add_argument('--replicas',
                            help='3 replicas of each object e.g. 3',
                            action='store', default=None, dest='replicas')
        parser.add_argument('--moving',
                            help='1 hour minimum time between moving a partition more than once e.g. 1',
                            action='store', default=None, dest='moving')
        return parser

    def take_action(self, parsed_args):
        create_account_builder_file(parsed_args)


class AccountBuilderAdd(Command):
    """add each storage node to the account ring"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(AccountBuilderAdd, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--region',
                            help='swift storage region e.g. 1',
                            action='store', default=None, dest='region')
        parser.add_argument('--zone',
                            help='swift storage zone e.g. 1',
                            action='store', default=None, dest='zone')
        parser.add_argument('--ip',
                            help='the IP address of the management network on the storage node e.g. STORAGE_NODE_IP',
                            action='store', default=None, dest='ip')
        parser.add_argument('--device',
                            help='a storage device name on the same storage node e.g. sdb',
                            action='store', default=None, dest='device')
        parser.add_argument('--weight',
                            help='the storage device weight e.g. 100',
                            action='store', default=None, dest='weight')
        return parser

    def take_action(self, parsed_args):
        account_builder_add(parsed_args)


class CreateContainerBuilderFile(Command):
    """create container ring"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateContainerBuilderFile, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--partitions',
                            help='2^10 (1024) maximum partitions e.g. 10',
                            action='store', default=None, dest='partitions')
        parser.add_argument('--replicas',
                            help='3 replicas of each object e.g. 3',
                            action='store', default=None, dest='replicas')
        parser.add_argument('--moving',
                            help='1 hour minimum time between moving a partition more than once e.g. 1',
                            action='store', default=None, dest='moving')
        return parser

    def take_action(self, parsed_args):
        create_container_builder_file(parsed_args)


class ContainerBuilderAdd(Command):
    """add each storage node to the container ring"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ContainerBuilderAdd, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--region',
                            help='swift storage region e.g. 1',
                            action='store', default=None, dest='region')
        parser.add_argument('--zone',
                            help='swift storage zone e.g. 1',
                            action='store', default=None, dest='zone')
        parser.add_argument('--ip',
                            help='the IP address of the management network on the storage node e.g. STORAGE_NODE_IP',
                            action='store', default=None, dest='ip')
        parser.add_argument('--device',
                            help='a storage device name on the same storage node e.g. sdb',
                            action='store', default=None, dest='device')
        parser.add_argument('--weight',
                            help='the storage device weight e.g. 100',
                            action='store', default=None, dest='weight')
        return parser

    def take_action(self, parsed_args):
        container_builder_add(parsed_args)


class CreateObjectBuilderFile(Command):
    """create object ring"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateObjectBuilderFile, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--partitions',
                            help='2^10 (1024) maximum partitions e.g. 10',
                            action='store', default=None, dest='partitions')
        parser.add_argument('--replicas',
                            help='3 replicas of each object e.g. 3',
                            action='store', default=None, dest='replicas')
        parser.add_argument('--moving',
                            help='1 hour minimum time between moving a partition more than once e.g. 1',
                            action='store', default=None, dest='moving')
        return parser

    def take_action(self, parsed_args):
        create_object_builder_file(parsed_args)


class ObjectBuilderAdd(Command):
    """add each storage node to the object ring"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ObjectBuilderAdd, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--region',
                            help='swift storage region e.g. 1',
                            action='store', default=None, dest='region')
        parser.add_argument('--zone',
                            help='swift storage zone e.g. 1',
                            action='store', default=None, dest='zone')
        parser.add_argument('--ip',
                            help='the IP address of the management network on the storage node e.g. STORAGE_NODE_IP',
                            action='store', default=None, dest='ip')
        parser.add_argument('--device',
                            help='a storage device name on the same storage node e.g. sdb',
                            action='store', default=None, dest='device')
        parser.add_argument('--weight',
                            help='the storage device weight e.g. 100',
                            action='store', default=None, dest='weight')
        return parser

    def take_action(self, parsed_args):
        object_builder_add(parsed_args)


class SyncBuilderFile(Command):
    """copy the account.ring.gz, container.ring.gz, and object.ring.gz files to the /etc/swift directory on each storage node and any additional nodes running the proxy service"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SyncBuilderFile, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        parser.add_argument('--to',
                            help='the target hosts where the *.ring.gz file to be added',
                            action='store', default=None, dest='to')
        return parser

    def take_action(self, parsed_args):
        sync_builder_file(parsed_args)


class AccountBuilderRebalance(Command):
    """rebalance the account ring"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(AccountBuilderRebalance, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        return parser

    def take_action(self, parsed_args):
        account_builder_rebalance(parsed_args)


class ContainerBuilderRebalance(Command):
    """rebalance the container ring"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ContainerBuilderRebalance, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        return parser

    def take_action(self, parsed_args):
        container_builder_rebalance(parsed_args)


class ObjectBuilderRebalance(Command):
    """rebalance the object ring"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ObjectBuilderRebalance, self).get_parser(prog_name)
        parser.add_argument('--user',
                            help='the username to connect to the remote host',
                            action='store', default='ubuntu', dest='user')
        parser.add_argument('--hosts',
                            help='the remote host to connect to ',
                            action='store', default=None, dest='hosts')
        parser.add_argument('-i', '--key-filename',
                            help='referencing file paths to SSH key files to try when connecting',
                            action='store', dest='key_filename', default=None)
        parser.add_argument('--password',
                            help='the password used by the SSH layer when connecting to remote hosts',
                            action='store', dest='password', default=None)
        return parser

    def take_action(self, parsed_args):
        object_builder_rebalance(parsed_args)
