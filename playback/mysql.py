import argparse
from fabric.api import *
import sys
from playback.cli import cli_description

parser = argparse.ArgumentParser(description=cli_description+'this command used for provision Galera Cluster for MySQL')
parser.add_argument('--user', help='the target user', 
                    action='store', default='ubuntu', dest='user')
parser.add_argument('--hosts', help='the target address', 
                    action='store', dest='hosts')
subparsers = parser.add_subparsers(dest="subparser_name") 

install = subparsers.add_parser('install', help='install Galera Cluster for MySQL')

config = subparsers.add_parser('config', help='setup Galera Cluster for MySQL')
config.add_argument('--wsrep-cluster-address', help='the IP addresses for each cluster node e.g. gcomm://CONTROLLER1_IP,CONTROLLER2_IP', 
                    action='store', dest='wsrep_cluster_address')
config.add_argument('--wsrep-node-name', help='the logical name of the cluster node e.g. galera1', 
                    action='store', dest='wsrep_node_name')
config.add_argument('--wsrep-node-address', help='the IP address of the cluster node e.g. CONTROLLER1_IP', 
                    action='store', dest='wsrep_node_address')

manage = subparsers.add_parser('manage', help='manage Galera Cluster for MySQL')
manage.add_argument('--wsrep-new-cluster', help='initialize the Primary Component on one cluster node',
                    action='store_true', default=False, dest='wsrep_new_cluster')
manage.add_argument('--start', help='start the database server on all other cluster nodes',
                    action='store_true', default=False, dest='start')
manage.add_argument('--stop', help='stop the database server',
                    action='store_true', default=False, dest='stop')
manage.add_argument('--change-root-password', help='change the root password',
                    action='store', default=False, dest='change_root_password')

args = parser.parse_args()

def main():
    if args.subparser_name == 'install':
        from playback import mysql_installation
        try:
            target = mysql_installation.MysqlInstallation(user=args.user, hosts=args.hosts.split(','))
        except AttributeError:
            parser.print_help()
            sys.exit(1)
        execute(target._enable_repo)
        execute(target._install)

    if args.subparser_name == 'config':
        from playback import mysql_config
        try:
            target = mysql_config.MysqlConfig(user=args.user, hosts=args.hosts.split(','))
        except AttributeError:
            parser.print_help()
            sys.exit(1)
        execute(target._update_mysql_config, args.wsrep_cluster_address, 
                args.wsrep_node_name, args.wsrep_node_address)

    if args.subparser_name == 'manage':
        from playback import mysql_manage
        try:
            target = mysql_manage.MysqlManage(user=args.user, hosts=args.hosts.split(','))
        except AttributeError:
            parser.print_help()
            sys.exit(1)
        if args.wsrep_new_cluster:
            execute(target._start_wsrep_new_cluster)
        if args.start:
            execute(target._start_mysql)
        if args.stop:
            execute(target._stop_mysql)
        if args.change_root_password:
            execute(target._change_root_password, args.change_root_password)
        


if __name__ == '__main__':
    main()
