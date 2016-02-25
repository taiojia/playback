from fabric.api import *
from fabric.contrib import files
import os
import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

parser.add_argument('--root-db-pass', 
                    help='the openstack database root passowrd',
                   action='store', 
                   default=None, 
                   dest='root_db_pass')
parser.add_argument('--keystone-db-pass', 
                    help='keystone db passowrd',
                    action='store', 
                    default=None, 
                    dest='keystone_db_pass')
group.add_argument('--create-keystone-db', 
                    help='create the keystone database', 
                    action='store_true', 
                    default=False, 
                    dest='create_keystone_db')
parser.add_argument('--user', 
                    help='the target user', 
                    action='store', 
                    default='ubuntu', 
                    dest='user')
parser.add_argument('--hosts', 
                    help='the target address', 
                    action='store', 
                    dest='hosts')
group.add_argument('--install',
                   help='install keystone',
                   action='store_true',
                   default=False,
                   dest='install')
parser.add_argument('--admin_token',
                    help='define the value of the initial administration token',
                    action='store',
                    default=None,
                    dest='admin_token')
parser.add_argument('--connection',
                    help='database connection string',
                    action='store',
                    default=None,
                    dest='connection')
parser.add_argument('--memcached_servers',
                    help='memcached servers',
                    action='store',
                    default=None,
                    dest='memcached_servers')
group.add_argument('--create-entity-and-endpoint',
                   help='create the service entity and API endpoints',
                   action='store_true',
                   default=False,
                   dest='create_entity_and_endpoint')
parser.add_argument('--os-token',
                    help='the admin token',
                    action='store',
                    default=None,
                    dest='os_token')
parser.add_argument('--os-url',
                    help='keystone endpoint url e.g. http://controller:35357/v3',
                    action='store',
                    default=None,
                    dest='os_url')
parser.add_argument('--public_endpoint',
                    help='the public endpoint e.g. http://controller:5000/v2.0',
                    action='store',
                    default=None,
                    dest='public_endpoint')
parser.add_argument('--internal-endpoint',
                    help='the internal endpoint e.g. http://controller:5000/v2.0',
                    action='store',
                    default=None,
                    dest='internal_endpoint')
parser.add_argument('--admin-endpoint',
                    help='the admin endpoint e.g. http://controller:35357/v2.0',
                    action='store',
                    default=None,
                    dest='admin_endpoint')

args = parser.parse_args()

conf_keystone_conf = """/etc/keystone/keystone.conf 
"""
# TODO conig file edit

conf_wsgi_keystone_conf = """Listen 5000
Listen 35357

<VirtualHost *:5000>
    WSGIDaemonProcess keystone-public processes=5 threads=1 user=keystone group=keystone display-name=%{GROUP}
    WSGIProcessGroup keystone-public
    WSGIScriptAlias / /usr/bin/keystone-wsgi-public
    WSGIApplicationGroup %{GLOBAL}
    WSGIPassAuthorization On
    <IfVersion >= 2.4>
      ErrorLogFormat "%{cu}t %M"
    </IfVersion>
    ErrorLog /var/log/apache2/keystone.log
    CustomLog /var/log/apache2/keystone_access.log combined

    <Directory /usr/bin>
        <IfVersion >= 2.4>
            Require all granted
        </IfVersion>
        <IfVersion < 2.4>
            Order allow,deny
            Allow from all
        </IfVersion>
    </Directory>
</VirtualHost>

<VirtualHost *:35357>
    WSGIDaemonProcess keystone-admin processes=5 threads=1 user=keystone group=keystone display-name=%{GROUP}
    WSGIProcessGroup keystone-admin
    WSGIScriptAlias / /usr/bin/keystone-wsgi-admin
    WSGIApplicationGroup %{GLOBAL}
    WSGIPassAuthorization On
    <IfVersion >= 2.4>
      ErrorLogFormat "%{cu}t %M"
    </IfVersion>
    ErrorLog /var/log/apache2/keystone.log
    CustomLog /var/log/apache2/keystone_access.log combined

    <Directory /usr/bin>
        <IfVersion >= 2.4>
            Require all granted
        </IfVersion>
        <IfVersion < 2.4>
            Order allow,deny
            Allow from all
        </IfVersion>
    </Directory>
</VirtualHost>
"""

class Keystone(object):
    def __init__(self, user, hosts=None, parallel=True):
        self.user = user
        self.hosts = hosts
        env.user = self.user
        env.hosts = self.hosts

    @serial
    def _create_keystone_db(self, root_db_pass, keystone_db_pass):
        sudo("mysql -uroot -p{root_db_pass} -e \"CREATE DATABASE keystone;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{root_db_pass} -e \"GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '{keystone_db_pass}';\"".format(root_db_pass, keystone_db_pass), shell_env=False)
        sudo("mysql -uroot -p{root_db_pass} -e \"GRANT ALL PRIVILEGES ON keystone.* TO 'keystone\'@\'%\' IDENTIFIED BY \'{keystone_db_pass}';\"".format(root_db_pass, keystone_db_pass), shell_env=False)
        # TODO test shell_env=False

    def _install_keystone(self, admin_token, connection, memcached_servers):
        # Disable the keystone service from starting automatically after installation
        sudo('echo "manual" > /etc/init/keystone.override', shell=False)
        
        sudo("apt-get update")
        sudo("apt-get install keystone apache2 libapache2-mod-wsgi memcached python-memcache -y")

        # Configure /etc/keysone/keystone.conf
        with open('tmp_keystone_conf') as f:
            f.write(conf_keystone_conf)
        files.upload_template(filename='tmp_keystone_conf',
                              destination='/etc/keystone/keystone.conf',
                              context={'admin_token': admin_token,
                              'connection': connection,
                              'servers': memcached_servers,},
                              )
        os.remove('tmp_keystone_conf')

        # Populate the Identity service database
        sudo('su -s /bin/sh -c "keystone-manage db_sync" keystone', shell=False)

        # Configure /etc/apache2/sites-available/wsgi-keystone.conf
        with open('tmp_wsgi_keystone_conf') as f:
            f.write(conf_wsgi_keystone_conf)
        files.upload_template(filename='tmp_wsgi_keystone_conf',
                              destination='/etc/apache2/sites-available/wsgi-keystone.conf')
        os.remove('tmp_wsgi_keystone_conf')

        # Enable the Identity service virtual hosts
        sudo('ln -s /etc/apache2/sites-available/wsgi-keystone.conf /etc/apache2/sites-enabled')

        # Restart the Apache HTTP server
        sudo('service apache2 restart')
        
        # Remove the SQLite database file
        sudo('rm -f /var/lib/keystone/keystone.db')

    # Create the service entity and API endpoints
    def _create_entity_and_endpoint(self, os_token, os_url, public_endpoint, internal_endpoint, admin_endpoint):
        sudo('openstack --os-token {os_token} --os-url {os_url} service create --name keystone --description "OpenStack Identity" identity'.format(os_token, os_url))
        sudo('openstack --os-token {os_token} --os-url {os_url} --region RegionOne identity public {public_endpoint}'.format(os_token, os_url, public_endpoint))
        sudo('openstack --os-token {os_token} --os-url {os_url} --region RegionOne identity internal {internal_endpoint}'.format(os_token, os_url, internal_endpoint))
        sudo('openstack --os-token {os_token} --os-url {os_url} --region RegionOne identity admin {admin_endpoint}'.format(os_token, os_url, admin_endpoint))

def main():
    target = Keystone(user=args.user, hosts=args.hosts)
    if args.create_keystone_db:
        execute(target._create_keystone_db, 
                args.root_db_pass, 
                args.keystone_db_pass)
    if args.install:
        execute(target._install_keystone, 
                args.admin_token, 
                args.connection, 
                args.memcached_servers)
    if args.creat_entity_and_endpoint:
        execute(target._create_entity_and_endpoint, 
                args.os_token,
                args.os_url,
                args.public_endpoint,
                args.internal_endpoint,
                args.admin_endpoint)

if __name__ == '__main__':
    main()