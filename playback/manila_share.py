from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback import __version__
from playback import common
from playback.templates.manila_conf_for_share import conf_manila_conf

class ManilaShare(common.Common):

    def _install_manila(self, connection, auth_uri, auth_url, manila_pass, my_ip, memcached_servers, rabbit_hosts, rabbit_user, rabbit_pass, neutron_endpoint, neutron_pass, nova_pass, cinder_pass):
        sys.stdout.write(red(env.host_string + ' | Install manila-share python-pymysql and neutron-plugin-linuxbridge-agent\n'))
        sudo('apt update')
        sudo('apt install manila-api manila-share python-pymysql neutron-plugin-linuxbridge-agent -y')

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
                                    'my_ip': my_ip,
                                    'neutron_endpoint': neutron_endpoint,
                                    'neutron_pass': neutron_pass,
                                    'nova_pass': nova_pass,
                                    'cinder_pass': cinder_pass
                                })
        os.remove('tmp_manila_conf_' + env.host_string)
        
        sys.stdout.write(red(env.host_string + ' | Restart the Share File Systems service including its dependencies\n'))
        finalize = sudo('systemctl restart manila-share')
        if finalize.failed or self._release == 'trusty':
            sudo('service manila-share restart')



def install_subparser(s):
    install_parser = s.add_parser('install',help='install manila share node')
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
    install_parser.add_argument('--neutron-endpoint',
                                help='neutron endpoint e.g. http://CONTROLLER_VIP:9696',
                                action='store',
                                default=None,
                                dest='neutron_endpoint')
    install_parser.add_argument('--neutron-pass',
                                help='the password for neutron user',
                                action='store',
                                default=None,
                                dest='neutron_pass')
    install_parser.add_argument('--nova-pass',
                                help='passowrd for nova user',
                                action='store',
                                default=None,
                                dest='nova_pass')
    install_parser.add_argument('--cinder-pass',
                                help='passowrd for cinder user',
                                action='store',
                                default=None,
                                dest='cinder_pass')
                            
    return install_parser

def make_target(args):
    try:
        target = ManilaShare(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    return target

def install(args):
    target = make_target(args)
    execute(target._install_manila,
            args.connection,
            args.auth_uri,
            args.auth_url,
            args.manila_pass,
            args.my_ip,
            args.memcached_servers,
            args.rabbit_hosts,
            args.rabbit_user,
            args.rabbit_pass,
            args.neutron_endpoint,
            args.neutron_pass,
            args.nova_pass,
            args.cinder_pass)

def parser():
    des = 'this command used for provision manila share node.'
    p, s = common.parser(des)

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