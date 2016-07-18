from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback import __version__
from playback.templates.glance_api_conf import conf_glance_api_conf
from playback.templates.glance_registry_conf import conf_glance_registry_conf
from playback import common

class Glance(common.Common):
    """
    Install glance

    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """

    @runs_once
    def _create_glance_db(self, root_db_pass, glance_db_pass):
        """Create the glance database"""
        print red(env.host_string + ' | Create glance database')
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE glance;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, glance_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, glance_db_pass), shell=False)

    def create_glance_db(self, *args, **kwargs):
        """
        Create the `glance` database and the user named `glance`

        :param root_db_pass: the mysql database `root` passowrd
        :param glance_db_pass: the password of `glance` user
        :returns: None
        """
        execute(self._create_glance_db, *args, **kwargs)

    @runs_once
    def _create_service_credentials(self, os_password, os_auth_url, glance_pass, public_endpoint, internal_endpoint, admin_endpoint):
        with shell_env(OS_PROJECT_DOMAIN_NAME='default',
                       OS_USER_DOMAIN_NAME='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2'):
            print red(env.host_string + ' | Create the glance user')
            sudo('openstack user create --domain default --password {0} glance'.format(glance_pass))
            print red(env.host_string + ' | Add the admin role to the glance user and service project')
            sudo('openstack role add --project service --user glance admin')
            print red(env.host_string + ' | Create the glance service entity')
            sudo('openstack service create --name glance --description "OpenStack Image service" image')
            print red(env.host_string + ' | Create the Image service API endpoints')
            sudo('openstack endpoint create --region RegionOne image public {0}'.format(public_endpoint))
            sudo('openstack endpoint create --region RegionOne image internal {0}'.format(internal_endpoint))
            sudo('openstack endpoint create --region RegionOne image admin {0}'.format(admin_endpoint))

    def create_service_credentials(self, *args, **kwargs):
        """
        Create the glance service credentials

        :param os_password: the password of openstack `admin` user
        :param os_auth_url: keystone endpoint url e.g. `http://CONTROLLER_VIP:35357/v3`
        :param glance_pass: create a passowrd of `glance` user
        :param public_endpoint: public endpoint for glance service e.g. `http://CONTROLLER_VIP:9292`
        :param internal_endpoint: internal endpoint for glance service e.g. `http://CONTROLLER_VIP:9292`
        :param admin_endpoint: admin endpoint for glance service e.g. `http://CONTROLLER_VIP:9292`
        :returns: None
        """
        return execute(self._create_service_credentials, *args, **kwargs)

    def _install_glance(self, connection, auth_uri, auth_url, glance_pass, swift_store_auth_address, memcached_servers, populate):
        print red(env.host_string + ' | Install glance')
        sudo('apt-get update')
        sudo('apt-get -y install glance')

        print red(env.host_string + ' | Update configuration for /etc/glance/glance-api.conf')
        with open("tmp_glance_api_conf_" + env.host_string, "w") as f:
            f.write(conf_glance_api_conf)

        files.upload_template(filename='tmp_glance_api_conf_'+env.host_string,
                              destination='/etc/glance/glance-api.conf',
                              context={'connection': connection,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': glance_pass,
                                       'swift_store_auth_address': None,
                                       'swift_store_key': glance_pass,
                                       'memcached_servers': memcached_servers},
                              use_jinja=True,
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_glance_api_conf_' + env.host_string)

        print red(env.host_string + ' | Update configuration for /etc/glance/glance-registry.conf')
        with open('tmp_glance_registry_conf_' + env.host_string, 'w') as f:
            f.write(conf_glance_registry_conf)
        
        files.upload_template(filename='tmp_glance_registry_conf_'+env.host_string,
                              destination='/etc/glance/glance-registry.conf',
                              context={'connection': connection,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': glance_pass,
                                       'memcached_servers': memcached_servers},
                              use_jinja=True,
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_glance_registry_conf_' + env.host_string)
   
        if populate:
            print red(env.host_string + ' | Populate the Image service database')
            sudo('su -s /bin/sh -c "glance-manage db_sync" glance', shell=False)

        
        print red(env.host_string + ' | Restart the Image services')
        sudo('service glance-registry restart')
        sudo('service glance-api restart')

        print red(env.host_string + ' | Remove the SQLite database file')
        sudo('rm -f /var/lib/glance/glance.sqlite')

    def install_glance(self, *args, **kwargs):
        """
        Install glance, default store is ceph

        :param connection: mysql database connection string e.g. `mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance`
        :param auth_uri: keystone internal endpoint e.g. `http://CONTROLLER_VIP:5000`
        :param auth_url: keystone admin endpoint e.g. `http://CONTROLLER_VIP:35357`
        :param glance_pass: passowrd of `glance` user
        :param swift_store_auth_address: DEPRECATED! the address where the Swift authentication service is listening e.g. `http://CONTROLLER_VIP:5000/v3/`
        :param memcached_servers: memcached servers e.g. `CONTROLLER1:11211,CONTROLLER2:11211`
        :param populate: populate the glance database
        :returns: None
        """
        return execute(self._install_glance, *args, **kwargs)
