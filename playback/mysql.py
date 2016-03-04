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
group.add_argument('--manage', help='manage Galera Cluster for MySQL',
                   action='store_true', default=False, dest='manage')
parser.add_argument('--wsrep-new-cluster', help='initialize the Primary Component on one cluster node',
                    action='store_true', default=False, dest='wsrep_new_cluster')
parser.add_argument('--start', help='start the database server on all other cluster nodes',
                    action='store_true', default=False, dest='start')
parser.add_argument('--stop', help='stop the database server',
                    action='store_true', default=False, dest='stop')
parser.add_argument('--change-root-password', help='change the root password',
                    action='store', default=False, dest='change_root_password')
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
                args.wsrep_node_name, args.wsrep_node_address)

    if args.manage:
        from playback import mysql_manage
        target = mysql_manage.MysqlManage(user=args.user, hosts=args.hosts.split(','))
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
