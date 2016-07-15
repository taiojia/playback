from fabric.api import *
from fabric.contrib import files
import os
from playback.templates.my_cnf import conf_my_cnf
from playback.templates.my_cnf_xenial import conf_my_cnf_xenial
from playback import common


class MysqlConfig(common.Common):
    """Setup Galera Cluster for MySQL"""
    
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
        return execute(self._update_mysql_config, *args, **kwargs)