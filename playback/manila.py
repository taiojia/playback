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

    @runs_once
    def _create_manila_db(self, root_db_pass, manila_db_pass):
        sys.stdout.write(red(env.host_string + ' | Create manila database\n'))
        sudo("mysql -uroot -p{0} -e \"CREATE DATABASE manila;\"".format(root_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON manila.* TO 'manila'@'localhost' IDENTIFIED BY '{1}';\"".format(root_db_pass, manila_db_pass), shell=False)
        sudo("mysql -uroot -p{0} -e \"GRANT ALL PRIVILEGES ON manila.* TO 'manila'@'%' IDENTIFIED BY '{1}';\"".format(root_db_pass, manila_db_pass), shell=False)

    def create_manila_db(self, *args, **kwargs):
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
        return execute(self._install_manila, *args, **kwargs)

def create_manila_db_subparser(s):
    create_manila_db_parser = s.add_parser('create-manila-db', help='create manila database')
    create_manila_db_parser.add_argument('--root-db-pass',
                                            help='the MySQL database root passowrd',
                                            action='store',
                                            default=None,
                                            dest='root_db_pass')
    create_manila_db_parser.add_argument('--manila-db-pass',
                                            help='manila database password',
                                            action='store',
                                            default=None,
                                            dest='manila_db_pass')
    return create_manila_db_parser

def create_service_credentials_subparser(s):
    create_service_credentials_parser = s.add_parser('create-service-credentials', help='create the service credentials')
    create_service_credentials_parser.add_argument('--os-password',
                                                    help='the password for admin user',
                                                    action='store',
                                                    default=None,
                                                    dest='os_password')
    create_service_credentials_parser.add_argument('--os-auth-url',
                                                    help='keystone endpoint url e.g. http://CONTROLLER_VIP:35357/v3',
                                                    action='store',
                                                    default=None,
                                                    dest='os_auth_url')
    create_service_credentials_parser.add_argument('--manila-pass',
                                                    help='passowrd for manila user',
                                                    action='store',
                                                    default=None,
                                                    dest='manila_pass')
    create_service_credentials_parser.add_argument('--public-endpoint-v1',
                                                    help=r'public endpoint for manila service e.g. "http://CONTROLLER_VIP:8786/v1/%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='public_endpoint_v1')
    create_service_credentials_parser.add_argument('--internal-endpoint-v1',
                                                    help=r'internal endpoint for manila service e.g. "http://CONTROLLER_VIP:8786/v1/%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='internal_endpoint_v1')
    create_service_credentials_parser.add_argument('--admin-endpoint-v1',
                                                    help=r'admin endpoint for manila service e.g. "http://CONTROLLER_VIP:8786/v1/%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='admin_endpoint_v1')
    create_service_credentials_parser.add_argument('--public-endpoint-v2',
                                                    help=r'public endpoint for manila service e.g. "http://CONTROLLER_VIP:8786/v2/%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='public_endpoint_v2')
    create_service_credentials_parser.add_argument('--internal-endpoint-v2',
                                                    help=r'internal endpoint for manila service e.g. "http://CONTROLLER_VIP:8786/v2/%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='internal_endpoint_v2')
    create_service_credentials_parser.add_argument('--admin-endpoint-v2',
                                                    help=r'admin endpoint for manila service e.g. "http://CONTROLLER_VIP:8786/v2/%%\(tenant_id\)s"',
                                                    action='store',
                                                    default=None,
                                                    dest='admin_endpoint_v2')
    return create_service_credentials_parser

def install_subparser(s):
    install_parser = s.add_parser('install',help='install manila')
    install_parser.add_argument('--connection',
                                help='mysql manila database connection string e.g. mysql+pymysql://manila:MANILA_PASS@CONTROLLER_VIP/manila',
                                action='store',
                                default=None,
                                dest='connection')
    install_parser.add_argument('--auth-uri',
                                help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                                action='store',
                                default=None,
                                dest='auth_uri')
    install_parser.add_argument('--auth-url',
                                help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                                action='store',
                                default=None,
                                dest='auth_url')
    install_parser.add_argument('--manila-pass',
                                help='passowrd for manila user',
                                action='store',
                                default=None,
                                dest='manila_pass')
    install_parser.add_argument('--my-ip',
                                help='the host management ip',
                                action='store',
                                default=None,
                                dest='my_ip')
    install_parser.add_argument('--memcached-servers',
                                help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                                action='store',
                                default=None,
                                dest='memcached_servers')
    install_parser.add_argument('--rabbit-hosts',
                                help='rabbit hosts e.g. CONTROLLER1,CONTROLLER2',
                                action='store',
                                default=None,
                                dest='rabbit_hosts')
    install_parser.add_argument('--rabbit-user',
                                help='the user for rabbit openstack user, default openstack',
                                action='store',
                                default='openstack',
                                dest='rabbit_user')
    install_parser.add_argument('--rabbit-pass',
                                help='the password for rabbit openstack user',
                                action='store',
                                default=None,
                                dest='rabbit_pass')
    install_parser.add_argument('--populate',
                                help='Populate the manila database',
                                action='store_true',
                                default=False,
                                dest='populate')
    return install_parser

def make_target(args):
    try:
        target = Manila(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    return target

def create_manila_db(args):
    target = make_target(args)
    target.create_manila_db(args.root_db_pass, args.manila_db_pass)

def create_service_credentials(args):
    target = make_target(args)
    target.create_service_credentials(
            args.os_password,
            args.os_auth_url,
            args.manila_pass,
            args.public_endpoint_v1,
            args.internal_endpoint_v1,
            args.admin_endpoint_v1,
            args.public_endpoint_v2,
            args.internal_endpoint_v2,
            args.admin_endpoint_v2)

def install(args):
    target = make_target(args)
    target.install_manila(
            args.connection,
            args.auth_uri,
            args.auth_url,
            args.manila_pass,
            args.my_ip,
            args.memcached_servers,
            args.rabbit_hosts,
            args.rabbit_user,
            args.rabbit_pass,
            args.populate)

def parser():
    des = 'this command used for provision manila controller node.'
    p, s = common.parser(des)

    def create_manila_db_f(args):
        create_manila_db(args)
    create_manila_db_parser = create_manila_db_subparser(s)
    create_manila_db_parser.set_defaults(func=create_manila_db_f)

    def create_service_credentials_f(args):
        create_service_credentials(args)
    create_service_credentials_parser = create_service_credentials_subparser(s)
    create_service_credentials_parser.set_defaults(func=create_service_credentials_f)

    def install_f(args):
        install(args)
    install_parser = install_subparser(s)
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
    return 1

if __name__ == '__main__':
    main()