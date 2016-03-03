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
group.add_argument('--create-service-credentials',
                   help='create the swift service credentials',
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
parser.add_argument('--swift-pass',
                    help='password for swift user',
                    action='store',
                    default=None,
                    dest='swift_pass')
parser.add_argument('--public-internal-endpoint',
                    help='public and internal endpoint for swift service e.g. http://CONTROLLER_VIP:8080/v1/AUTH_%%\(tenant_id\)s',
                    action='store',
                    default=None,
                    dest='public_internal_endpoint')
parser.add_argument('--admin-endpoint',
                    help='admin endpoint for swift service e.g. http://CONTROLLER_VIP:8080/v1',
                    action='store',
                    default=None,
                    dest='admin_endpoint')

args = parser.parse_args()




class Swift(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(Swift, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _create_service_credentials(self, os_password, os_auth_url, swift_pass, public_internal_endpoint, admin_endpoint):
        with shell_env(OS_PROJECT_DOMAIN_ID='default',
                       OS_USER_DOMAIN_ID='default',
                       OS_PROJECT_NAME='admin',
                       OS_TENANT_NAME='admin',
                       OS_USERNAME='admin',
                       OS_PASSWORD=os_password,
                       OS_AUTH_URL=os_auth_url, 
                       OS_IDENTITY_API_VERSION='3',
                       OS_IMAGE_API_VERSION='2'):
            print red(env.host_string + ' | Create the swift user')
            sudo('openstack user create --domain default --password {0} swift'.format(swift_pass))
            print red(env.host_string + ' | Add the admin role to the swift user and service project')
            sudo('openstack role add --project service --user swift admin')
            print red(env.host_string + ' | Create the swift service entity')
            sudo('openstack service create --name swift --description "OpenStack Object Storage" object-store')
            print red(env.host_string + ' | Create the Object Storage service API endpoints')
            sudo('openstack endpoint create --region RegionOne object-store public {0}'.format(public_internal_endpoint))
            sudo('openstack endpoint create --region RegionOne object-store internal {0}'.format(public_internal_endpoint))
            sudo('openstack endpoint create --region RegionOne object-store admin {0}'.format(admin_endpoint))



def main():
    try:
        target = Swift(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')

    if args.create_service_credentials:
        execute(target._create_service_credentials,
                args.os_password, 
                args.os_auth_url, 
                args.swift_pass, 
                args.public_internal_endpoint, 
                args.admin_endpoint)

if __name__ == '__main__':
    main()

