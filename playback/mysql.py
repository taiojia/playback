import argparse
from fabric.api import *

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

parser.add_argument('--user', help='the target user', 
                    action='store', default='ubuntu', dest='user')
parser.add_argument('--hosts', help='the target address', 
                    action='store', dest='hosts')
parser.add_argument('--wsrep_cluster_address', help='the IP addresses for each cluster node', 
                    action='store', dest='wsrep_cluster_address')
parser.add_argument('--wsrep_node_name', help='the logical name of the cluster node', 
                    action='store', dest='wsrep_node_name')
parser.add_argument('--wsrep_node_address', help='the IP address of the cluster node', 
                    action='store', dest='wsrep_node_address')
group.add_argument('--install', help='install Galera Cluster for MySQL', 
                   action='store_true', default=False, dest='install')
group.add_argument('--config', help='setup Galera Cluster for MySQL', 
                   action='store_true', default=False, dest='config')
args = parser.parse_args()

def main():
    if args.install:
        from playback import mysql_installation
        target = mysql_installation.MysqlInstallation(user=args.user, hosts=args.hosts.split(','))
        execute(target._enable_repo)
        execute(target._install)
    if args.config:
        from playback import mysql_config
        target = mysql_config.MysqlConfig(user=args.user, hosts=args.hosts.split(','))
        execute(target._update_mysql_config, args.wsrep_cluster_address, 
                args.wsrep_node_name, args.wsrep_node_address)# TODO


if __name__ == '__main__':
    main()
