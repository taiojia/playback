from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import sys
import argparse
from playback.cli import cli_description
from playback import __version__
from playback.templates.cinder_conf import conf_cinder_conf
from playback.templates.policy_json_for_cinder import conf_policy_json
from playback import common

class Cinder(common.Common):

    @runs_once
    def _create_cinder_db(self, root_db_pass, cinder_db_pass):
        print red(env.host_string + ' | Create cinder database')
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE cinder;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, cinder_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, cinder_db_pass), shell=False)

    @runs_once
    def _create_service_credentials(self, os_password, os_auth_url, cinder_pass, public_endpoint_v1, internal_endpoint_v1, admin_endpoint_v1, public_endpoint_v2, internal_endpoint_v2, admin_endpoint_v2):
        with shell_env(OS_PROJECT_DOMAIN_NAME='default',
                       OS_USER_DOMAIN_NAME='default',
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
            sudo('openstack endpoint create --region RegionOne volume public {0}'.format(public_endpoint_v1))
            sudo('openstack endpoint create --region RegionOne volume internal {0}'.format(internal_endpoint_v1))
            sudo('openstack endpoint create --region RegionOne volume admin {0}'.format(admin_endpoint_v1))
            sudo('openstack endpoint create --region RegionOne volumev2 public {0}'.format(public_endpoint_v2))
            sudo('openstack endpoint create --region RegionOne volumev2 internal {0}'.format(internal_endpoint_v2))
            sudo('openstack endpoint create --region RegionOne volumev2 admin {0}'.format(admin_endpoint_v2))

    def _install(self, connection, rabbit_hosts, rabbit_user, rabbit_pass, auth_uri, auth_url, cinder_pass, my_ip, glance_api_servers, rbd_secret_uuid, memcached_servers, populate=False):
        print red(env.host_string + ' | Install the cinder-api and cinder-volume')
        sudo('apt-get update')
        sudo('apt-get -y install cinder-api cinder-scheduler cinder-volume')

        print red(env.host_string + ' | Update /etc/cinder/cinder.conf')
        with open('tmp_cinder_conf_' + env.host_string, 'w') as f:
            f.write(conf_cinder_conf)
        files.upload_template(filename='tmp_cinder_conf_' + env.host_string,
                              destination='/etc/cinder/cinder.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'connection': connection,
                                       'rabbit_hosts': rabbit_hosts,
                                       'rabbit_user': rabbit_user,
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'cinder_pass': cinder_pass,
                                       'my_ip': my_ip,
                                       'glance_api_servers': glance_api_servers,
                                       'rbd_secret_uuid': rbd_secret_uuid,
                                       'memcached_servers': memcached_servers})
        os.remove('tmp_cinder_conf_' + env.host_string)

        print red(env.host_string + ' | Enable Consistency groups')
        with open('tmp_policy_json_' + env.host_string, 'w') as f:
            f.write(conf_policy_json)
        files.upload_template(filename='tmp_policy_json_' + env.host_string,
                                destination='/etc/cinder/policy.json',
                                use_sudo=True,
                                backup=True)
        os.remove('tmp_policy_json_' + env.host_string)

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

def make_target(user, hosts, key_filename, password):
    try:
        target = Cinder(user, hosts, key_filename, password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    
    return target
    
def create_cinder_db(user, hosts, key_filename, password, root_db_pass, cinder_db_pass):
    target = make_target(user, hosts, key_filename, password)
    execute(target._create_cinder_db, root_db_pass, cinder_db_pass)

def create_service_credentials(user ,hosts, key_filename, password, os_password, os_auth_url, cinder_pass, public_endpoint_v1, internal_endpoint_v1, admin_endpoint_v1, public_endpoint_v2, internal_endpoint_v2, admin_endpoint_v2):
    target =make_target(user, hosts, key_filename, password)
    execute(target._create_service_credentials, os_password, 
            os_auth_url, cinder_pass, public_endpoint_v1, internal_endpoint_v1, admin_endpoint_v1, public_endpoint_v2, internal_endpoint_v2, admin_endpoint_v2)

def install(user, hosts, key_filename, password, connection, rabbit_hosts, rabbit_user, rabbit_pass, auth_uri, auth_url, cinder_pass, my_ip, glance_api_servers, rbd_secret_uuid, memcached_servers, populate):
    target = make_target(user, hosts, key_filename, password)
    execute(target._install,
            connection,
            rabbit_hosts,
            rabbit_user,
            rabbit_pass, 
            auth_uri, 
            auth_url, 
            cinder_pass, 
            my_ip, 
            glance_api_servers, 
            rbd_secret_uuid,
            memcached_servers, 
            populate)
            
def parser():
    p = argparse.ArgumentParser(prog='cinder-deploy',description=cli_description+'this command used for privision Cinder')
    p.add_argument('-v', '--version', action='version', version=__version__)
    p.add_argument('--user', help='the target user', action='store', default='ubuntu', dest='user')
    p.add_argument('--hosts', help='the target address', action='store', dest='hosts')
    p.add_argument('-i', '--key-filename', help='referencing file paths to SSH key files to try when connecting', action='store', dest='key_filename', default=None)
    p.add_argument('--password', help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password', default=None)

    s = p.add_subparsers(dest="subparser_name", help="commands")
    
    def create_cinder_db_f(args):
        create_cinder_db(args.user, args.hosts.split(','), args.key_filename, args.password, args.root_db_pass, args.cinder_db_pass)
    create_cinder_db_parser = s.add_parser('create-cinder-db', help='create the cinder database')
    create_cinder_db_parser.add_argument('--root-db-pass', help='the openstack database root passowrd', action='store', default=None, dest='root_db_pass')
    create_cinder_db_parser.add_argument('--cinder-db-pass', help='cinder db passowrd', action='store', default=None, dest='cinder_db_pass')
    create_cinder_db_parser.set_defaults(func=create_cinder_db_f)
    
    def create_service_credentials_f(args):
        create_service_credentials(args.user, args.hosts.split(','), args.key_filename, args.password, args.os_password, args.os_auth_url, args.cinder_pass, args.public_endpoint_v1, args.internal_endpoint_v1, args.admin_endpoint_v1, args.public_endpoint_v2, args.internal_endpoint_v2, args.admin_endpoint_v2)
    create_service_credentials_parser = s.add_parser('create-service-credentials',help='create the cinder service credentials')
    create_service_credentials_parser.add_argument('--os-password', help='the password for admin user', action='store', default=None, dest='os_password')
    create_service_credentials_parser.add_argument('--os-auth-url', help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3', action='store', default=None, dest='os_auth_url')
    create_service_credentials_parser.add_argument('--cinder-pass', help='password for cinder user', action='store', default=None, dest='cinder_pass')
    create_service_credentials_parser.add_argument('--public-endpoint-v1', help=r'public endpoint for volume service e.g. "http://CONTROLLER_VIP:8776/v1/%%\(tenant_id\)s"', action='store', default=None, dest='public_endpoint_v1')
    create_service_credentials_parser.add_argument('--internal-endpoint-v1', help=r'internal endpoint for volume service e.g. "http://CONTROLLER_VIP:8776/v1/%%\(tenant_id\)s"', action='store', default=None, dest='internal_endpoint_v1')
    create_service_credentials_parser.add_argument('--admin-endpoint-v1', help=r'admin endpoint for volume service e.g. "http://CONTROLLER_VIP:8776/v1/%%\(tenant_id\)s"', action='store', default=None, dest='admin_endpoint_v1')
    create_service_credentials_parser.add_argument('--public-endpoint-v2', help=r'public endpoint v2 for volumev2 service e.g. "http://CONTROLLER_VIP:8776/v2/%%\(tenant_id\)s"', action='store', default=None, dest='public_endpoint_v2')
    create_service_credentials_parser.add_argument('--internal-endpoint-v2', help=r'internal endpoint v2 for volumev2 service e.g. "http://CONTROLLER_VIP:8776/v2/%%\(tenant_id\)s"', action='store', default=None, dest='internal_endpoint_v2')
    create_service_credentials_parser.add_argument('--admin-endpoint-v2', help=r'admin endpoint v2 for volumev2 service e.g. "http://CONTROLLER_VIP:8776/v2/%%\(tenant_id\)s"', action='store', default=None, dest='admin_endpoint_v2')

    create_service_credentials_parser.set_defaults(func=create_service_credentials_f)
    
    def install_f(args):
        install(args.user, args.hosts.split(','), args.key_filename, args.password, args.connection, args.rabbit_hosts, args.rabbit_user, args.rabbit_pass, args.auth_uri, args.auth_url, args.cinder_pass, args.my_ip, args.glance_api_servers, args.rbd_secret_uuid, args.memcached_servers, args.populate)
    install_parser = s.add_parser('install', help='install cinder api and volume')
    install_parser.add_argument('--connection', help='mysql database connection string e.g. mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder', action='store', default=None, dest='connection')
    install_parser.add_argument('--rabbit-hosts', help='rabbit hosts e.g. CONTROLLER1,CONTROLLER2', action='store', default=None, dest='rabbit_hosts')
    install_parser.add_argument('--rabbit-user', help='the user for rabbit, default openstack', action='store', default='openstack', dest='rabbit_user')
    install_parser.add_argument('--rabbit-pass', help='the password for rabbit openstack user', action='store', default=None, dest='rabbit_pass')
    install_parser.add_argument('--auth-uri', help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000', action='store', default=None, dest='auth_uri')
    install_parser.add_argument('--auth-url', help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357', action='store', default=None, dest='auth_url')
    install_parser.add_argument('--cinder-pass', help='password for cinder user', action='store', default=None, dest='cinder_pass')
    install_parser.add_argument('--my-ip', help='the host management ip', action='store', default=None, dest='my_ip')
    install_parser.add_argument('--glance-api-servers', help='glance host e.g. http://CONTROLLER_VIP:9292', action='store', default=None, dest='glance_api_servers')
    install_parser.add_argument('--rbd-secret-uuid', help='ceph rbd secret uuid', action='store', default=None, dest='rbd_secret_uuid')
    install_parser.add_argument('--memcached-servers', help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211', action='store', default=None, dest='memcached_servers')
    install_parser.add_argument('--populate', help='Populate the cinder database', action='store_true', default=False, dest='populate')
    install_parser.set_defaults(func=install_f)
    
    return p
        
def main():
    p = parser()
    args = p.parse_args()
    if not hasattr(args, 'func'):
        p.print_help()
    else:
        # XXX on Python 3.3 we get 'args has no func' rather than short help.
        try:
            args.func(args)
            disconnect_all()
            return 0
        except Exception as e:
            sys.stderr.write(e.message)
            sys.exit(1)
    return 1
    
if __name__ == '__main__':
    main()
