from fabric.api import *
from fabric.contrib import files
import os
from playback.templates.my_cnf import conf_my_cnf
from playback.templates.my_cnf_xenial import conf_my_cnf_xenial
from playback import common


class MysqlConfig(common.Common):
    """
    Config Galera Cluster for MySQL
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """
    
    def _update_mysql_config(self, wsrep_cluster_address, wsrep_node_name, wsrep_node_address):
        if self._release() == "xenial":
            conf_my_cnf = conf_my_cnf_xenial
        with open('tmp_my_cnf_'+env.host_string, 'w') as f:
            f.write(conf_my_cnf)
        if self._release() == "trusty":
            files.upload_template(filename='tmp_my_cnf_'+env.host_string, 
                                destination='/etc/mysql/my.cnf', 
                                context={'wsrep_cluster_address': wsrep_cluster_address, 
                                        'wsrep_node_name': wsrep_node_name, 
                                        'wsrep_node_address': wsrep_node_address}, 
                                use_jinja=True, use_sudo=True, backup=True)
        if self._release() == "xenial":
            files.upload_template(filename='tmp_my_cnf_'+env.host_string, 
                                destination='/etc/mysql/conf.d/openstack.cnf', 
                                context={'wsrep_cluster_address': wsrep_cluster_address, 
                                        'wsrep_node_name': wsrep_node_name, 
                                        'wsrep_node_address': wsrep_node_address}, 
                                use_jinja=True, use_sudo=True, backup=False)
        try:
            os.remove('tmp_my_cnf_'+env.host_string)
        except Exception:
            pass

    def update_mysql_config(self, *args, **kwargs):
        """
        If trusty setup Galera Cluster for MySQL. If xenial setup MariaDB Galera Cluster

        :param wsrep_cluster_address: the IP addresses for each cluster node e.g. `gcomm://CONTROLLER1_IP,CONTROLLER2_IP`
        :param wsrep_node_name: the logical name of the cluster node e.g. `galera1`
        :param wsrep_node_address: the IP address of the cluster node e.g. `CONTROLLER1_IP`
        :returns: None
        """
        return execute(self._update_mysql_config, *args, **kwargs)