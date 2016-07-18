from fabric.api import *
from fabric.contrib import files
from fabric.colors import red
from fabric.network import disconnect_all
import os
import argparse
import sys
from playback import __version__
from playback.templates.keystone_conf import conf_keystone_conf
from playback.templates.wsgi_keystone_conf import conf_wsgi_keystone_conf
from playback.templates.keystone_paste_ini import conf_keystone_paste_ini
from playback.templates.memcached_conf import conf_memcached_conf
from playback import common

class Keystone(common.Common):
    """
    Install keystone
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """

    @runs_once
    def _create_keystone_db(self, root_db_pass, keystone_db_pass):
        sudo("mysql -uroot -p{root_db_pass} -e \"CREATE DATABASE keystone;\"".format(root_db_pass=root_db_pass), shell=False)
        sudo("mysql -uroot -p{root_db_pass} -e \"GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '{keystone_db_pass}';\"".format(root_db_pass=root_db_pass, 
                                                                                                                                                            keystone_db_pass=keystone_db_pass), shell=False)
        sudo("mysql -uroot -p{root_db_pass} -e \"GRANT ALL PRIVILEGES ON keystone.* TO 'keystone\'@\'%\' IDENTIFIED BY \'{keystone_db_pass}';\"".format(root_db_pass=root_db_pass, 
                                                                                                                                                        keystone_db_pass=keystone_db_pass), shell=False)
    def create_keystone_db(self, *args, **kwargs):
        """
        Create the `keystone` database and the user named keystone

        :param root_db_pass: the mysql database `root` passowrd
        :param keystone_db_pass: the password of `keystone` database user
        :returns: None
        """
        return execute(self._create_keystone_db, *args, **kwargs)

    def _install_keystone(self, admin_token, connection, memcached_servers, populate):
        # Disable the keystone service from starting automatically after installation
        sudo('echo "manual" > /etc/init/keystone.override')
        
        sudo("apt-get update")
        sudo("apt-get install keystone apache2 libapache2-mod-wsgi memcached python-memcache -y")

        if self._release() == 'xenial':
            sudo('systemctl stop keystone')
            sudo('update-rc.d keystone disable')

        # Configure /etc/keysone/keystone.conf
        with open('tmp_keystone_conf_'+env.host_string,'w') as f:
            f.write(conf_keystone_conf)
        files.upload_template(filename='tmp_keystone_conf_'+env.host_string,
                              destination='/etc/keystone/keystone.conf',
                              context={'admin_token': admin_token,
                              'connection': connection,
                              'memcached_servers': memcached_servers,},
                              use_jinja=True,
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_keystone_conf_'+env.host_string)

        # Configure /etc/memcached.conf to listen 0.0.0.0
        with open('tmp_memcached_conf_'+env.host_string, 'w') as f:
            f.write(conf_memcached_conf)
        files.upload_template(filename='tmp_memcached_conf_'+env.host_string,
                                destination='/etc/memcached.conf',
                                use_sudo=True,
                                backup=True)
        os.remove('tmp_memcached_conf_'+env.host_string)
        sudo('service memcached restart')

        # Populate the Identity service database
        if populate:
            sudo('su -s /bin/sh -c "keystone-manage db_sync" keystone', shell=False)
            # Initialize Fernet Keys
            sudo('keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone', shell=False)
        


        # Configure /etc/apache2/sites-available/wsgi-keystone.conf
        with open('tmp_wsgi_keystone_conf_'+env.host_string, 'w') as f:
            f.write(conf_wsgi_keystone_conf)
        files.upload_template(filename='tmp_wsgi_keystone_conf_'+env.host_string,
                              destination='/etc/apache2/sites-available/wsgi-keystone.conf',
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_wsgi_keystone_conf_'+env.host_string)

        # Enable the Identity service virtual hosts
        sudo('ln -s /etc/apache2/sites-available/wsgi-keystone.conf /etc/apache2/sites-enabled')

        # Add ServerName to apache configuration
        files.append('/etc/apache2/apache2.conf', 'ServerName localhost', use_sudo=True)
        # Restart the Apache HTTP server
        sudo('service apache2 restart')
        
        # Remove the SQLite database file
        sudo('rm -f /var/lib/keystone/keystone.db')
    
    def install_keystone(self, *args, **kwargs):
        """
        Install keystone

        :param admin_token: define the value of the initial administration token
        :param connection: database connection string e.g. `mysql+pymysql://keystone:PASS@CONTROLLER_VIP/keystone`
        :param memcached_servers: memcached servers. e.g. `CONTROLLER1:11211,CONTROLLER2:11211`
        :param populate: populate the `keystone` database
        :returns: None
        """
        return execute(self._install_keystone, *args, **kwargs)

    # Create the service entity and API endpoints
    @runs_once
    def _create_entity_and_endpoint(self, os_token, os_url, public_endpoint, internal_endpoint, admin_endpoint):
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} service create --name keystone --description "OpenStack Identity" identity'.format(os_token=os_token, 
                                                                                                                                                                            os_url=os_url))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} endpoint create --region RegionOne identity public {public_endpoint}'.format(os_token=os_token, 
                                                                                                                                                                            os_url=os_url, 
                                                                                                                                                                            public_endpoint=public_endpoint))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} endpoint create --region RegionOne identity internal {internal_endpoint}'.format(os_token=os_token, 
                                                                                                                                                                            os_url=os_url, 
                                                                                                                                                                            internal_endpoint=internal_endpoint))
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} endpoint create --region RegionOne identity admin {admin_endpoint}'.format(os_token=os_token, 
                                                                                                                                                                            os_url=os_url, 
                                                                                                                                                                            admin_endpoint=admin_endpoint))

    def create_entity_and_endpoint(self, *args, **kwargs):
        """
        Create the service entity and API endpoints

        :param os_token: the openstack admin token
        :param os_url: keystone endpoint url e.g. `http://CONTROLLER_VIP:35357/v3`
        :param public_endpoint: the public endpoint e.g. `http://CONTROLLER_VIP:5000/v3`
        :param internal_endpoint: the internal endpoint e.g. `http://CONTROLLER_VIP:5000/v3`
        :param admin_endpoint: the admin endpoint e.g. `http://CONTROLLER_VIP:35357/v3`
        :returns: None
        """
        return execute(self._create_entity_and_endpoint, *args, **kwargs)

    # Create projects, users, and roles
    @runs_once
    def _create_projects_users_roles(self, os_token, os_url, admin_pass, demo_pass):
        # Create the default domain
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} domain create --description "Default Domain" default'.format(os_token=os_token,
                                                                                                                                                        os_url=os_url))
        # Create the admin project
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} project create --domain default --description "Admin Project" admin'.format(os_token=os_token,
                                                                                                                                                                        os_url=os_url))
        # Create the admin user
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} user create --domain default --password {admin_pass} admin'.format(os_token=os_token,
                                                                                                                                                                os_url=os_url,
                                                                                                                                                                admin_pass=admin_pass))
        # Create the admin role
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role create admin'.format(os_token=os_token,
                                                                                                                      os_url=os_url))
        # Add the admin role to the admin project and user
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role add --project admin --user admin admin'.format(os_token=os_token,
                                                                                                                                                os_url=os_url))

        # Create the service project
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} project create --domain default --description "Service Project" service'.format(os_token=os_token,
                                                                                                                                                                            os_url=os_url))
        # Create the demo project
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} project create --domain default --description "Demo Project" demo'.format(os_token=os_token,
                                                                                                                                                                      os_url=os_url))
        # Create the demo user
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} user create --domain default --password {demo_pass} demo'.format(os_token=os_token,
                                                                                                                                                             os_url=os_url,
                                                                                                                                                             demo_pass=demo_pass))
        # Create the user role
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role create user'.format(os_token=os_token,
                                                                                                                     os_url=os_url))
        # Add the user role to the demo project and user
        sudo('openstack --os-identity-api-version 3 --os-token {os_token} --os-url {os_url} role add --project demo --user demo user'.format(os_token=os_token,
                                                                                                                                             os_url=os_url))
    def create_projects_users_roles(self, *args, **kwargs):
        """
        Create an administrative and demo project, user, and role for administrative and testing operations in your environment

        :param os_token: the openstack admin token
        :param os_url: keystone endpoint url e.g. `http://CONTROLLER_VIP:35357/v3`
        :param admin_pass: passowrd of openstack `admin` user
        :param demo_pass: passowrd of openstack `demo` user
        :returns: None
        """
        return execute(self._create_projects_users_roles, *args, **kwargs)

    def _update_keystone_paste_ini(self):
        """remove admin_token_auth from the [pipeline:public_api], 
        [pipeline:admin_api], and [pipeline:api_v3] sections"""
        with open('tmp_keystone_paste_ini_'+env.host_string, 'w') as f:
            f.write(conf_keystone_paste_ini)
        files.upload_template(filename='tmp_keystone_paste_ini_'+env.host_string,
                              destination='/etc/keystone/keystone-paste.ini',
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_keystone_paste_ini_'+env.host_string)

    def update_keystone_paste_ini(self):
        """
        Remove admin_token_auth from the [pipeline:public_api], 
        [pipeline:admin_api], and [pipeline:api_v3] sections in `/etc/keystone/keystone-paste.ini`

        :returns: None
        """
        return execute(self._update_keystone_paste_ini, *args, **kwargs)

