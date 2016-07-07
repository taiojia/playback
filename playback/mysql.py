import argparse
from fabric.api import *
from fabric.network import disconnect_all
from fabric.colors import red
import sys
from playback.cli import cli_description
from playback import __version__

def install(args):
    from playback import mysql_installation
    try:
        target = mysql_installation.MysqlInstallation(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        err_hosts = red('No hosts found. Please using --hosts param.')
        sys.stderr.write(err_hosts)
        sys.exit(1)
    execute(target._enable_repo)
    execute(target._install)

def config(args):
    from playback import mysql_config
    try:
        target = mysql_config.MysqlConfig(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        err_hosts = red('No hosts found. Please using --hosts param.')
        sys.stderr.write(err_hosts)
        sys.exit(1)
    execute(target._update_mysql_config, args.wsrep_cluster_address, 
            args.wsrep_node_name, args.wsrep_node_address)

def manage(args):
    from playback import mysql_manage
    try:
        target = mysql_manage.MysqlManage(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        err_hosts = red('No hosts found. Please using --hosts param.')
        sys.stderr.write(err_hosts)
        sys.exit(1)
    if args.wsrep_new_cluster:
        execute(target._start_wsrep_new_cluster)
    if args.start:
        execute(target._start_mysql)
    if args.stop:
        execute(target._stop_mysql)
    if args.change_root_password:
        execute(target._change_root_password, args.change_root_password)
    if args.show_cluster_status:
        if args.root_db_pass == None:
            raise Exception('--root-db-pass is empty\n')
        execute(target._show_cluster_status, args.root_db_pass)

def install_subparser(s):
    install_parser = s.add_parser('install', help='install Galera Cluster for MySQL')
    return install_parser

def config_subparser(s):
    config_parser = s.add_parser('config', help='setup Galera Cluster for MySQL')
    config_parser.add_argument('--wsrep-cluster-address', help='the IP addresses for each cluster node e.g. gcomm://CONTROLLER1_IP,CONTROLLER2_IP', 
                                action='store', dest='wsrep_cluster_address')
    config_parser.add_argument('--wsrep-node-name', help='the logical name of the cluster node e.g. galera1', 
                                action='store', dest='wsrep_node_name')
    config_parser.add_argument('--wsrep-node-address', help='the IP address of the cluster node e.g. CONTROLLER1_IP', 
                                action='store', dest='wsrep_node_address')
    return config_parser

def manage_subparser(s):
    manage_parser = s.add_parser('manage', help='manage Galera Cluster for MySQL')
    manage_parser.add_argument('--wsrep-new-cluster', help='initialize the Primary Component on one cluster node',
                                action='store_true', default=False, dest='wsrep_new_cluster')
    manage_parser.add_argument('--start', help='start the database server on all other cluster nodes',
                                action='store_true', default=False, dest='start')
    manage_parser.add_argument('--stop', help='stop the database server',
                                action='store_true', default=False, dest='stop')
    manage_parser.add_argument('--change-root-password', help='change the root password',
                                action='store', default=False, dest='change_root_password')
    manage_parser.add_argument('--show-cluster-status', help='show the cluster status',
                                action='store_true', default=False, dest='show_cluster_status')
    manage_parser.add_argument('--root-db-pass', help='the password of root user',
                                action='store', default=None, dest='root_db_pass')
    return manage_parser

def parser():
    p = argparse.ArgumentParser(prog='mysql-deploy', description=cli_description+'this command used for provision Galera Cluster for MySQL')
    p.add_argument('-v', '--version',
                    action='version',
                    version=__version__)
    p.add_argument('--user', help='the target user', 
                    action='store', default='ubuntu', dest='user')
    p.add_argument('--hosts', help='the target address', 
                    action='store', dest='hosts')
    p.add_argument('-i', '--key-filename', help='referencing file paths to SSH key files to try when connecting', default=None,
                    action='store', dest='key_filename')
    p.add_argument('--password', help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password', default=None)
    s = p.add_subparsers(dest="subparser_name")

    def install_f(args):
        install(args)
    install_parser = install_subparser(s)
    install_parser.set_defaults(func=install_f)

    def config_f(args):
        config(args)
    config_parser = config_subparser(s)
    config_parser.set_defaults(func=config_f)

    def manage_f(args):
        manage(args)
    manage_parser = manage_subparser(s)
    manage_parser.set_defaults(func=manage_f)

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
