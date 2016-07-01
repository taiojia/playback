from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
from playback.templates.nova_conf_for_compute import conf_nova_conf
from playback.templates.nova_compute_conf import conf_nova_compute_conf
from playback.templates.libvirt_bin import conf_libvirt_bin
from playback.templates.libvirtd_conf import conf_libvirtd_conf

from playback import __version__
from playback import common

class NovaCompute(common.Common):

    def _install(self, my_ip, rabbit_hosts, rabbit_user, rabbit_pass, auth_uri, auth_url, nova_pass, novncproxy_base_url, glance_api_servers, neutron_endpoint, neutron_pass, rbd_secret_uuid, memcached_servers):
        print red(env.host_string + ' | Install nova-compute sysfsutils')
        sudo('apt-get update')
        sudo('apt-get -y install nova-compute sysfsutils')

        print red(env.host_string + ' | Update /etc/nova/nova.conf')
        with open('tmp_nova_conf_' + env.host_string, 'w') as f:
            f.write(conf_nova_conf)

        files.upload_template(filename='tmp_nova_conf_'+env.host_string,
                              destination='/etc/nova/nova.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'my_ip': my_ip,
                                       'rabbit_hosts': rabbit_hosts,
                                       'rabbit_user': rabbit_user, 
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': nova_pass,
                                       'novncproxy_base_url': novncproxy_base_url,
                                       'api_servers': glance_api_servers,
                                       'url': neutron_endpoint,
                                       'neutron_password': neutron_pass,
                                       'memcached_servers': memcached_servers})
        os.remove('tmp_nova_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/nova/nova-compute.conf')
        with open('tmp_nova_compute_conf_' + env.host_string, 'w') as f:
            f.write(conf_nova_compute_conf)

        files.upload_template(filename='tmp_nova_compute_conf_'+env.host_string,
                              destination='/etc/nova/nova-compute.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'rbd_secret_uuid': rbd_secret_uuid})

        os.remove('tmp_nova_compute_conf_' + env.host_string)

        print red(env.host_string + ' | Restart Compute service')
        sudo('service nova-compute restart')
        print red(env.host_string + ' |  Remove the SQLite database file')
        sudo('rm -f /var/lib/nova/nova.sqlite')

        print red(env.host_string + ' | Enable libvirt listen on 16509')
        print red(env.host_string + ' | Update /etc/default/libvirt-bin')
        with open('tmp_libvirt_bin_' + env.host_string, 'w') as f:
            f.write(conf_libvirt_bin)
        files.upload_template(filename='tmp_libvirt_bin_' + env.host_string,
                              destination='/etc/default/libvirt-bin',
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_libvirt_bin_' + env.host_string)
        print red(env.host_string + ' | Update /etc/libvirt/libvirtd.conf')
        with open('tmp_libvirtd_conf_' + env.host_string, 'w') as f:
            f.write(conf_libvirtd_conf)
        files.upload_template(filename='tmp_libvirtd_conf_' + env.host_string,
                              destination='/etc/libvirt/libvirtd.conf',
                              use_sudo=True,
                              backup=True)
        os.remove('tmp_libvirtd_conf_' + env.host_string)
        sudo('service libvirt-bin restart')

def install_subparser(s):
    install_parser = s.add_parser('install', help='install nova compute')
    install_parser.add_argument('--my-ip',
                                help='the host management ip',
                                action='store',
                                default=None,
                                dest='my_ip')
    install_parser.add_argument('--rabbit-hosts',
                                help='rabbit hosts e.g. CONTROLLER1,CONTROLLER2',
                                action='store',
                                default=None,
                                dest='rabbit_hosts')
    install_parser.add_argument('--rabbit-user',
                                help='the user for rabbit, default openstack',
                                action='store',
                                default='openstack',
                                dest='rabbit_user')
    install_parser.add_argument('--rabbit-pass',
                                help='the password for rabbit openstack user',
                                action='store',
                                default=None,
                                dest='rabbit_pass')
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
    install_parser.add_argument('--nova-pass',
                                help='passowrd for nova user',
                                action='store',
                                default=None,
                                dest='nova_pass')
    install_parser.add_argument('--novncproxy-base-url',
                                help='nova vnc proxy base url e.g. http://CONTROLLER_VIP:6080/vnc_auto.html',
                                action='store',
                                default=None,
                                dest='novncproxy_base_url')
    install_parser.add_argument('--glance-api-servers',
                                help='glance host e.g. http://CONTROLLER_VIP:9292',
                                action='store',
                                default=None,
                                dest='glance_api_servers')
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
    install_parser.add_argument('--rbd-secret-uuid',
                                help='ceph rbd secret for nova libvirt',
                                action='store',
                                default=None,
                                dest='rbd_secret_uuid')
    install_parser.add_argument('--memcached-servers',
                                help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                                action='store',
                                default=None,
                                dest='memcached_servers')
    return install_parser

def make_target(args):
    try:
        target = NovaCompute(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    return target
        
def install(args):
    target = make_target(args)
    execute(target._install, args.my_ip, args.rabbit_hosts, args.rabbit_user, args.rabbit_pass,
            args.auth_uri, args.auth_url, args.nova_pass, args.novncproxy_base_url,
            args.glance_api_servers, args.neutron_endpoint, args.neutron_pass, args.rbd_secret_uuid, args.memcached_servers)
    
def parser():
    p = argparse.ArgumentParser(prog='nova-compute-deploy', description=cli_description+'this command used for provision Nova Compute')
    p.add_argument('-v', '--version',
                    action='version',
                    version=__version__)
    p.add_argument('--user', 
                    help='the target user', 
                    action='store', 
                    default='ubuntu', 
                    dest='user')
    p.add_argument('--hosts', 
                    help='the target address', 
                    action='store', 
                    dest='hosts')
    p.add_argument('-i', '--key-filename', help='referencing file paths to SSH key files to try when connecting', action='store', dest='key_filename', default=None)
    p.add_argument('--password', help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password', default=None)

    s = p.add_subparsers(dest='subparser_name')
    
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