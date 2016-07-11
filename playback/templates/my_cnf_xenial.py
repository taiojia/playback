conf_my_cnf_xenial = """[mysqld]
bind-address = 0.0.0.0
default-storage-engine = innodb
innodb_file_per_table
max_connections = 4096
collation-server = utf8_general_ci
character-set-server = utf8

# MariaDB Galera Cluster in Xenial
wsrep_cluster_name="galera_cluster"
wsrep_cluster_address="{{ wsrep_cluster_address }}"
wsrep_node_name="{{ wsrep_node_name }}"
wsrep_node_address="{{ wsrep_node_address }}"
wsrep_provider=/usr/lib/libgalera_smm.so
binlog_format=ROW
"""
