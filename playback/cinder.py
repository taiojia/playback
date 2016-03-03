from fabric.api import *
from fabric.contrib import files
from fabric.tasks import Task
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

parser.add_argument('--user', 
                    help='the target user', 
                    action='store', 
                    default='ubuntu', 
                    dest='user')
parser.add_argument('--hosts', 
                    help='the target address', 
                    action='store', 
                    dest='hosts')
group.add_argument('--create-cinder-db', 
                    help='create the cinder database', 
                    action='store_true', 
                    default=False, 
                    dest='create_cinder_db')
parser.add_argument('--root-db-pass', 
                    help='the openstack database root passowrd',
                   action='store', 
                   default=None, 
                   dest='root_db_pass')
parser.add_argument('--cinder-db-pass', 
                    help='cinder db passowrd',
                    action='store', 
                    default=None, 
                    dest='cinder_db_pass')
group.add_argument('--create-service-credentials',
                   help='create the cinder service credentials',
                   action='store_true',
                   default=False,
                   dest='create_service_credentials')
parser.add_argument('--os-password',
                    help='the password for admin user',
                    action='store',
                    default=None,
                    dest='os_password')
parser.add_argument('--os-auth-url',
                    help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                    action='store',
                    default=None,
                    dest='os_auth_url')
parser.add_argument('--cinder-pass',
                    help='password for cinder user',
                    action='store',
                    default=None,
                    dest='cinder_pass')
parser.add_argument('--endpoint-v1',
                    help='public, internal and admin endpoint for volume service e.g. http://CONTROLLER_VIP:8776/v1/%%\(tenant_id\)s',
                    action='store',
                    default=None,
                    dest='endpoint_v1')
parser.add_argument('--endpoint-v2',
                    help='public, internal and admin endpoint v2 for volumev2 service e.g. http://CONTROLLER_VIP:8776/v2/%%\(tenant_id\)s',
                    action='store',
                    default=None,
                    dest='endpoint_v2')
group.add_argument('--install',
                   help='install cinder api and volume',
                   action='store_true',
                   default=False,
                   dest='install')
parser.add_argument('--connection',
                    help='mysql database connection string e.g. mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder',
                    action='store',
                    default=None,
                    dest='connection')
parser.add_argument('--rabbit-hosts',
                    help='rabbit hosts e.g. CONTROLLER1,CONTROLLER2',
                    action='store',
                    default=None,
                    dest='rabbit_hosts')
parser.add_argument('--rabbit-pass',
                    help='the password for rabbit openstack user',
                    action='store',
                    default=None,
                    dest='rabbit_pass')
parser.add_argument('--auth-uri',
                    help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                    action='store',
                    default=None,
                    dest='auth_uri')
parser.add_argument('--auth-url',
                    help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                    action='store',
                    default=None,
                    dest='auth_url')
parser.add_argument('--my-ip',
                    help='the host management ip',
                    action='store',
                    default=None,
                    dest='my_ip')
parser.add_argument('--glance-host',
                    help='glance host e.g. CONTROLLER_VIP',
                    action='store',
                    default=None,
                    dest='glance_host')
parser.add_argument('--rbd-secret-uuid',
                    help='ceph rbd secret uuid',
                    action='store',
                    default=None,
                    dest='rbd_secret_uuid')
parser.add_argument('--populate',
                    help='Populate the cinder database',
                    action='store_true',
                    default=False,
                    dest='populate')

args = parser.parse_args()

conf_cinder_conf = """[DEFAULT]
rootwrap_config = /etc/cinder/rootwrap.conf
api_paste_confg = /etc/cinder/api-paste.ini
iscsi_helper = tgtadm
volume_name_template = volume-%s
volume_group = cinder-volumes
verbose = True
auth_strategy = keystone
state_path = /var/lib/cinder
lock_path = /var/lock/cinder
volumes_dir = /var/lib/cinder/volumes
rpc_backend = rabbit
auth_strategy = keystone
my_ip = {{ my_ip }}
glance_host = {{ glance_host }}

volume_driver = cinder.volume.drivers.rbd.RBDDriver
rbd_pool = volumes
rbd_ceph_conf = /etc/ceph/ceph.conf
rbd_flatten_volume_from_snapshot = False
rbd_max_clone_depth = 5
rbd_store_chunk_size = 4
rados_connect_timeout = -1
rbd_user = cinder
rbd_secret_uuid = {{ rbd_secret_uuid }}
glance_api_version = 2


[database]
connection = {{ connection }}

[oslo_messaging_rabbit]
rabbit_hosts = {{ rabbit_hosts }}
rabbit_userid = openstack
rabbit_password = {{ rabbit_password }}

[keystone_authtoken]
auth_uri = {{ auth_uri }}
auth_url = {{ auth_url }}
auth_plugin = password
project_domain_id = default
user_domain_id = default
project_name = service
username = cinder
password = {{ cinder_pass }}

[oslo_concurrency]
lock_path = /var/lib/cinder/tmp
"""

class Cinder(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(Cinder, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    @runs_once
    def _create_cinder_db(self, root_db_pass, cinder_db_pass):
        print red(env.host_string + ' | Create cinder database')
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE cinder;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, cinder_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, cinder_db_pass), shell=False)

    @runs_once
    def _create_service_credentials(self, os_password, os_auth_url, cinder_pass, endpoint_v1, endpoint_v2):
        with shell_env(OS_PROJECT_DOMAIN_ID='default',
                       OS_USER_DOMAIN_ID='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2'):
            print red(env.host_string + ' | Create the cinder user')
            sudo('openstack user create --domain default --password {0} cinder'.format(cinder_pass))
            print red(env.host_string + ' | Add the admin role to the cinder user and service project')
            sudo('openstack role add --project service --user cinder admin')
            print red(env.host_string + ' | Create the cinder and cinderv2 service entity')
            sudo('openstack service create --name cinder --description "OpenStack Block Storage" volume')
            sudo('openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2')
            print red(env.host_string + ' | Create the Block Storage service API endpoints')
            sudo('openstack endpoint create --region RegionOne volume public {0}'.format(endpoint_v1))
            sudo('openstack endpoint create --region RegionOne volume internal {0}'.format(endpoint_v1))
            sudo('openstack endpoint create --region RegionOne volume admin {0}'.format(endpoint_v1))
            sudo('openstack endpoint create --region RegionOne volumev2 public {0}'.format(endpoint_v2))
            sudo('openstack endpoint create --region RegionOne volumev2 internal {0}'.format(endpoint_v2))
            sudo('openstack endpoint create --region RegionOne volumev2 admin {0}'.format(endpoint_v2))

    def _install(self, connection, rabbit_hosts, rabbit_pass, auth_uri, auth_url, cinder_pass, my_ip, glance_host, rbd_secret_uuid, populate=False):
        print red(env.host_string + ' | Install the cinder-api and cinder-volume')
        sudo('apt-get update')
        sudo('apt-get -y install cinder-api cinder-scheduler python-cinderclient cinder-volume python-mysqldb')

        print red(env.host_string + ' | Update /etc/cinder/cinder.conf')
        with open('tmp_cinder_conf_' + env.host_string, 'w') as f:
            f.write(conf_cinder_conf)
        files.upload_template(filename='tmp_cinder_conf_' + env.host_string,
                              destination='/etc/cinder/cinder.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'connection': connection,
                                       'rabbit_hosts': rabbit_hosts,
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'cinder_pass': cinder_pass,
                                       'my_ip': my_ip,
                                       'glance_host': glance_host,
                                       'rbd_secret_uuid': rbd_secret_uuid})
        os.remove('tmp_cinder_conf_' + env.host_string)

        if populate:
            print red(env.host_string + ' | Populate the Block Storage database')
            sudo('su -s /bin/sh -c "cinder-manage db sync" cinder', shell=False)

        print red(env.host_string + ' | Restart the services')
        sudo('service nova-api restart', warn_only=True)
        sudo('service cinder-scheduler restart')
        sudo('service cinder-api restart')
        sudo('service tgt restart', warn_only=True)
        sudo('service cinder-volume restart')
        print red(env.host_string + ' | Remove the SQLite database file')
        sudo('rm -f /var/lib/cinder/cinder.sqlite')



def main():
    try:
        target = Cinder(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')

    if args.create_cinder_db:
        execute(target._create_cinder_db,
                args.root_db_pass, 
                args.cinder_db_pass)
    if args.create_service_credentials:
        execute(target._create_service_credentials,
                 args.os_password, 
                 args.os_auth_url, 
                 args.cinder_pass, 
                 args.endpoint_v1, 
                 args.endpoint_v2)
    if args.install:
        execute(target._install,
                args.connection,
                args.rabbit_hosts,
                args.rabbit_pass, 
                args.auth_uri, 
                args.auth_url, 
                args.cinder_pass, 
                args.my_ip, 
                args.glance_host, 
                args.rbd_secret_uuid, 
                args.populate)

if __name__ == '__main__':
    main()