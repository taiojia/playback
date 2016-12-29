import sys, logging
from playback.api import MysqlConfig
from playback.api import MysqlManage
from playback.api import MysqlInstallation
from cliff.command import Command


def install(args):
    try:
        target = MysqlInstallation(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        err_hosts = 'No hosts found. Please using --hosts param.'
        sys.stderr.write(err_hosts)
        sys.exit(1)
    target.enable_repo()
    target.install()

def config(args):
    try:
        target = MysqlConfig(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        err_hosts = 'No hosts found. Please using --hosts param.'
        sys.stderr.write(err_hosts)
        sys.exit(1)
    target.update_mysql_config(args.wsrep_cluster_address,
            args.wsrep_node_name, args.wsrep_node_address)

def manage(args):
    try:
        target = MysqlManage(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        err_hosts = 'No hosts found. Please using --hosts param.'
        sys.stderr.write(err_hosts)
        sys.exit(1)
    if args.wsrep_new_cluster:
        target.start_wsrep_new_cluster()
    if args.start:
        target.start_mysql()
    if args.stop:
        target.stop_mysql()
    if args.change_root_password:
        target.change_root_password(args.change_root_password)
    if args.show_cluster_status:
        if args.root_db_pass == None:
            raise Exception('--root-db-pass is empty\n')
        target.show_cluster_status(args.root_db_pass)


class Install(Command):
    """install Galera Cluster for MySQL"""

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
        return parser

    def take_action(self, parsed_args):
        install(parsed_args)


class Config(Command):
    """setup Galera Cluster for MySQL"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Config, self).get_parser(prog_name)
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
        parser.add_argument('--wsrep-cluster-address',
                            help='the IP addresses for each cluster node e.g. gcomm://CONTROLLER1_IP,CONTROLLER2_IP',
                            action='store', dest='wsrep_cluster_address')
        parser.add_argument('--wsrep-node-name', help='the logical name of the cluster node e.g. galera1',
                            action='store', dest='wsrep_node_name')
        parser.add_argument('--wsrep-node-address',
                            help='the IP address of the cluster node e.g. CONTROLLER1_IP',
                            action='store', dest='wsrep_node_address')
        return parser

    def take_action(self, parsed_args):
        config(parsed_args)


class Manage(Command):
    """manage Galera Cluster for MySQL"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Manage, self).get_parser(prog_name)
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
        parser.add_argument('--wsrep-new-cluster',
                            help='initialize the Primary Component on one cluster node',
                            action='store_true', default=False, dest='wsrep_new_cluster')
        parser.add_argument('--start',
                            help='start the database server on all other cluster nodes',
                            action='store_true', default=False, dest='start')
        parser.add_argument('--stop',
                            help='stop the database server',
                            action='store_true', default=False, dest='stop')
        parser.add_argument('--change-root-password',
                            help='change the root password',
                            action='store', default=False, dest='change_root_password')
        parser.add_argument('--show-cluster-status',
                            help='show the cluster status',
                            action='store_true', default=False, dest='show_cluster_status')
        parser.add_argument('--root-db-pass',
                            help='the password of root user',
                            action='store', default=None, dest='root_db_pass')
        return parser

    def take_action(self, parsed_args):
        manage(parsed_args)

