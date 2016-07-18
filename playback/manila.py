from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback import __version__
from playback import common
from playback.templates.manila_conf import conf_manila_conf

class Manila(common.Common):
    """
    Install manila service
    
    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """

    @runs_once
    def _create_manila_db(self, root_db_pass, manila_db_pass):
        sys.stdout.write(red(env.host_string + ' | Create manila database\n'))
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE manila;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON manila.* TO 'manila'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, manila_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON manila.* TO 'manila'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, manila_db_pass), shell=False)

    def create_manila_db(self, *args, **kwargs):
        """
        Create manila database and the user named manila

        :param root_db_pass: the password of mysql root user 
        :param manila_db_pass: the password of manila database user
        :returns: None
        """
        return execute(self._create_manila_db, *args, **kwargs)

    @runs_once
    def _create_service_credentials(self, os_password, os_auth_url, manila_pass, public_endpoint_v1, internal_endpoint_v1, admin_endpoint_v1, public_endpoint_v2, internal_endpoint_v2, admin_endpoint_v2):
        with shell_env(OS_PROJECT_DOMAIN_NAME='default',
                       OS_USER_DOMAIN_NAME='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2'):
            sys.stdout.write(red(env.host_string + ' | Create a manila user\n'))
            sudo('openstack user create --domain default --password {0} manila'.format(manila_pass))
            sys.stdout.write(red(env.host_string + ' | Add the admin role to the manila user\n'))
            sudo('openstack role add --project service --user manila admin')
            sys.stdout.write(red(env.host_string + ' | Create the manila and manilav2 service entities\n'))
            sudo('openstack service create --name manila --description "OpenStack Shared File Systems" share')
            sudo('openstack service create --name manilav2 --description "OpenStack Shared File Systems" sharev2')
            sys.stdout.write(red(env.host_string + ' | Create the Shared File Systems service API endpoints v1\n'))
            sudo('openstack endpoint create --region RegionOne share public {0}'.format(public_endpoint_v1))
            sudo('openstack endpoint create --region RegionOne share internal {0}'.format(internal_endpoint_v1))
            sudo('openstack endpoint create --region RegionOne share admin {0}'.format(admin_endpoint_v1))
            sys.stdout.write(red(env.host_string + ' | Create the Shared File Systems service API endpoints v2\n'))
            sudo('openstack endpoint create --region RegionOne sharev2 public {0}'.format(public_endpoint_v2))
            sudo('openstack endpoint create --region RegionOne sharev2 internal {0}'.format(internal_endpoint_v2))
            sudo('openstack endpoint create --region RegionOne sharev2 admin {0}'.format(admin_endpoint_v2))

    def create_service_credentials(self, *args, **kwargs):
        r"""
        create the manila service credentials

        :param os_password: the password of openstack `admin` user
        :param os_auth_url: keystone endpoint url e.g. `http://CONTROLLER_VIP:35357/v3`
        :param manila_pass: passowrd of `manila` user
        :param public_endpoint_v1: public endpoint for manila service e.g. `http://CONTROLLER_VIP:8786/v1/%\\(tenant_id\\)s`
        :param internal_endpoint_v1: internal endpoint for manila service e.g. `http://CONTROLLER_VIP:8786/v1/%\\(tenant_id\\)s`
        :param admin_endpoint_v1: admin endpoint for manila service e.g. `http://CONTROLLER_VIP:8786/v1/%\\(tenant_id\\)s`
        :param public_endpoint_v2: public endpoint for manila service e.g. `http://CONTROLLER_VIP:8786/v2/%\\(tenant_id\\)s`
        :param internal_endpoint_v2: internal endpoint for manila service e.g. `http://CONTROLLER_VIP:8786/v2/%\\(tenant_id\\)s`
        :param admin_endpoint_v2: admin endpoint for manila service e.g. `http://CONTROLLER_VIP:8786/v2/%\\(tenant_id\\)s`
        :returns: None
        """
        return execute(self._create_service_credentials, *args, **kwargs)

    def _install_manila(self, connection, auth_uri, auth_url, manila_pass, my_ip, memcached_servers, rabbit_hosts, rabbit_user, rabbit_pass, populate):
        sys.stdout.write(red(env.host_string + ' | Install manila-api manila-scheduler python-manilaclient\n'))
        sudo('apt update')
        sudo('apt install manila-api manila-scheduler python-manilaclient -y')

        sys.stdout.write(red(env.host_string + ' | Update /etc/manila/manila.conf\n'))
        with open('tmp_manila_conf_' + env.host_string ,'w') as f:
            f.write(conf_manila_conf)
        files.upload_template(filename='tmp_manila_conf_' + env.host_string,
                                destination='/etc/manila/manila.conf',
                                use_jinja=True,
                                use_sudo=True,
                                backup=True,
                                context={
                                    'connection': connection,
                                    'rabbit_hosts': rabbit_hosts,
                                    'rabbit_userid': rabbit_user,
                                    'rabbit_password': rabbit_pass,
                                    'memcached_servers': memcached_servers,
                                    'auth_uri': auth_uri,
                                    'auth_url': auth_url,
                                    'manila_pass': manila_pass,
                                    'my_ip': my_ip
                                })
        os.remove('tmp_manila_conf_' + env.host_string)

        if populate and env.host_string == self.hosts[0]:
            sys.stdout.write(red(env.host_string + ' | Populate the Share File System database\n'))
            sudo('su -s /bin/sh -c "manila-manage db sync" manila', shell=False)
        
        sys.stdout.write(red(env.host_string + ' | Restart the Share File Systems services\n'))
        finalize = sudo('systemctl restart manila-scheduler manila-api')
        if finalize.failed or self._release == 'trusty':
            sudo('service manila-scheduler restart')
            sudo('service manila-api restart')

    def install_manila(self, *args, **kwargs):
        """
        Install manila

        :param connection: mysql manila database connection string e.g. `mysql+pymysql://manila:MANILA_PASS@CONTROLLER_VIP/manila`
        :param auth_uri: keystone internal endpoint e.g. `http://CONTROLLER_VIP:5000`
        :param auth_url: keystone admin endpoint e.g. `http://CONTROLLER_VIP:35357`
        :param manila_pass: passowrd of `manila` user
        :param my_ip: the host management ip
        :param memcached_servers: memcached servers e.g. `CONTROLLER1:11211,CONTROLLER2:11211`
        :param rabbit_hosts: rabbit hosts e.g. `CONTROLLER1,CONTROLLER2`
        :param rabbit_user: the user of rabbit openstack user, e.g. `openstack`
        :param rabbit_pass: the password of `rabbit_user`
        :param populate: populate the manila database
        :returns: None
        """
        return execute(self._install_manila, *args, **kwargs)

