from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.templates.proxy_server_conf import conf_proxy_server_conf
from playback.templates.swift_conf import conf_swift_conf
from playback import __version__
from playback import common

class Swift(common.Common):
    """
    Deploy swift proxy node

    :param user(str): the user for remote server to login 
    :param hosts(list): this is a second param
    :param key_filename(str): the ssh private key to used, default None
    :param password(str): the password for remote server
    :param parallel(bool): paralleler execute on remote server, default True
    :returns: None
    """

    @runs_once
    def _create_service_credentials(self, os_password, os_auth_url, swift_pass, public_endpoint, internal_endpoint, admin_endpoint):
        with shell_env(OS_PROJECT_DOMAIN_NAME='default',
                       OS_USER_DOMAIN_NAME='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2',
                       OS_AUTH_VERSION='3'):
            print red(env.host_string + ' | Create the swift user')
            sudo('openstack user create --domain default --password {0} swift'.format(swift_pass))
            print red(env.host_string + ' | Add the admin role to the swift user and service project')
            sudo('openstack role add --project service --user swift admin')
            print red(env.host_string + ' | Create the swift service entity')
            sudo('openstack service create --name swift --description "OpenStack Object Storage" object-store')
            print red(env.host_string + ' | Create the Object Storage service API endpoints')
            sudo('openstack endpoint create --region RegionOne object-store public {0}'.format(public_endpoint))
            sudo('openstack endpoint create --region RegionOne object-store internal {0}'.format(internal_endpoint))
            sudo('openstack endpoint create --region RegionOne object-store admin {0}'.format(admin_endpoint))

    def create_service_credentials(self, *args, **kwargs):
        r"""
        Create the swift service credentials

        :param os_password: the password of openstack `admin` user
        :param os_auth_url: keystone endpoint url e.g. `http://CONTROLLER_VIP:35357/v3`
        :param swift_pass: password of `swift` user
        :param public_endpoint: public endpoint for swift service e.g. `http://CONTROLLER_VIP:8080/v1/AUTH_%\\(tenant_id\\)s`
        :param internal_endpoint: internal endpoint for swift service e.g. `http://CONTROLLER_VIP:8080/v1/AUTH_%\\(tenant_id\\)s`
        :param admin_endpoint: admin endpoint for swift service e.g. `http://CONTROLLER_VIP:8080/v1`
        :returns: None
        """
        return execute(self._create_service_credentials, *args, **kwargs)

    def _install(self, auth_uri, auth_url, swift_pass, memcached_servers, with_memcached):
        print red(env.host_string + ' | Install swift proxy')
        sudo('apt-get update')
        sudo('apt-get -y install swift swift-proxy python-swiftclient python-keystoneclient python-keystonemiddleware')
        # Install memcached
        if with_memcached:
            sudo('apt-get -y install memcached')
            # Configure /etc/memcached.conf to listen 0.0.0.0
            with open('tmp_memcached_conf_'+env.host_string, 'w') as f:
                f.write(conf_memcached_conf)
            files.upload_template(filename='tmp_memcached_conf_'+env.host_string,
                                    destination='/etc/memcached.conf',
                                    use_sudo=True,
                                    backup=True)
            os.remove('tmp_memcached_conf_'+env.host_string)
            sudo('service memcached restart')

        sudo('mkdir /etc/swift')

        print red(env.host_string + ' | Update /etc/swift/proxy-server.conf')
        with open('tmp_proxy_server_conf_' + env.host_string, 'w') as f:
            f.write(conf_proxy_server_conf)
        files.upload_template(filename='tmp_proxy_server_conf_' + env.host_string,
                              destination='/etc/swift/proxy-server.conf',
                              use_sudo=True,
                              use_jinja=True,
                              backup=True,
                              context={'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'swift_pass': swift_pass,
                                       'memcached_servers': memcached_servers})
        os.remove('tmp_proxy_server_conf_' + env.host_string)

    def install(self, *args, **kwargs):
        """
        Install swift proxy service

        :param auth_uri: keystone internal endpoint e.g. `http://CONTROLLER_VIP:5000`
        :param auth_url: keystone admin endpoint e.g. `http://CONTROLLER_VIP:35357`
        :param swift_pass: password of `swift` user
        :param memcached_servers: memcache servers e.g. `CONTROLLER1:11211,CONTROLLER2:11211`
        :param with_memcached: install memcached on remote server, if you have other memcached on the controller node, you can use `memcached_serser`
        :returns: None
        """
        return execute(self._install, *args, **kwargs)

    def _finalize_install(self, swift_hash_path_suffix, swift_hash_path_prefix):
        print red(env.host_string + ' | Update /etc/swift/swift.conf')
        with open('tmp_swift_conf_' + env.host_string, 'w') as f:
            f.write(conf_swift_conf)
        files.upload_template(filename='tmp_swift_conf_' + env.host_string,
                              destination='/etc/swift/swift.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'swift_hash_path_suffix': swift_hash_path_suffix,
                                       'swift_hash_path_prefix': swift_hash_path_prefix})
        os.remove('tmp_swift_conf_' + env.host_string)
        print red(env.host_string + ' | On all nodes, ensure proper ownership of the configuration directory')
        sudo('chown -R root:swift /etc/swift')
        print red(env.host_string + ' | On the controller node and any other nodes running the proxy service, restart the Object Storage proxy service including its dependencies')
        sudo('service memcached restart', warn_only=True)
        sudo('service swift-proxy restart', warn_only=True)
        print red(env.host_string + ' | On the storage nodes, start the Object Storage services')
        sudo('swift-init all start', warn_only=True)

    def finalize_install(self, *args, **kwargs):
        """
        Finalize swift installation

        :param swift_hash_path_suffix: `swift_hash_path_suffix` and `swift_hash_path_prefix` are used as part of the hashing algorithm when determining data placement in the cluster. These values should remain secret and MUST NOT change once a cluster has been deployed
        :param swift_hash_path_prefix: `swift_hash_path_suffix` and `swift_hash_path_prefix` are used as part of the hashing algorithm when determining data placement in the cluster. These values should remain secret and MUST NOT change once a cluster has been deployed
        :returns None
        """
        return execute(self._finalize_install, *args, **kwargs)

