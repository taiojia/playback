from fabric.api import *
from fabric.contrib import files
from fabric.tasks import Task
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
from playback.nova_compute_conf import conf_nova_conf, conf_nova_compute_conf, conf_libvirt_bin, conf_libvirtd_conf
from playback import __version__

parser = argparse.ArgumentParser(description=cli_description+'this command used for provision Nova Compute')
parser.add_argument('-v', '--version',
                   action='version',
                   version=__version__)
parser.add_argument('--user', 
                    help='the target user', 
                    action='store', 
                    default='ubuntu', 
                    dest='user')
parser.add_argument('--hosts', 
                    help='the target address', 
                    action='store', 
                    dest='hosts')

subparsers = parser.add_subparsers(dest='subparser_name')
install = subparsers.add_parser('install',
                                help='install nova compute')
install.add_argument('--my-ip',
                    help='the host management ip',
                    action='store',
                    default=None,
                    dest='my_ip')
install.add_argument('--rabbit-hosts',
                    help='rabbit hosts e.g. CONTROLLER1,CONTROLLER2',
                    action='store',
                    default=None,
                    dest='rabbit_hosts')
install.add_argument('--rabbit-pass',
                    help='the password for rabbit openstack user',
                    action='store',
                    default=None,
                    dest='rabbit_pass')
install.add_argument('--auth-uri',
                    help='keystone internal endpoint e.g. http://CONTROLLER_VIP:5000',
                    action='store',
                    default=None,
                    dest='auth_uri')
install.add_argument('--auth-url',
                    help='keystone admin endpoint e.g. http://CONTROLLER_VIP:35357',
                    action='store',
                    default=None,
                    dest='auth_url')
install.add_argument('--nova-pass',
                    help='passowrd for nova user',
                    action='store',
                    default=None,
                    dest='nova_pass')
install.add_argument('--novncproxy-base-url',
                    help='nova vnc proxy base url e.g. http://CONTROLLER_VIP:6080/vnc_auto.html',
                    action='store',
                    default=None,
                    dest='novncproxy_base_url')
install.add_argument('--glance-host',
                    help='glance host e.g. CONTROLLER_VIP',
                    action='store',
                    default=None,
                    dest='glance_host')
install.add_argument('--neutron-endpoint',
                    help='neutron endpoint e.g. http://CONTROLLER_VIP:9696',
                    action='store',
                    default=None,
                    dest='neutron_endpoint')
install.add_argument('--neutron-pass',
                    help='the password for neutron user',
                    action='store',
                    default=None,
                    dest='neutron_pass')
install.add_argument('--rbd-secret-uuid',
                    help='ceph rbd secret for nova libvirt',
                    action='store',
                    default=None,
                    dest='rbd_secret_uuid')

args = parser.parse_args()






class NovaCompute(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(NovaCompute, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _install(self, my_ip, rabbit_hosts, rabbit_pass, auth_uri, auth_url, nova_pass, novncproxy_base_url, glance_host, neutron_endpoint, neutron_pass, rbd_secret_uuid):
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
                              context={'my_ip': my_ip,
                                       'rabbit_hosts': rabbit_hosts,
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'password': nova_pass,
                                       'novncproxy_base_url': novncproxy_base_url,
                                       'host': glance_host,
                                       'url': neutron_endpoint,
                                       'neutron_password': neutron_pass})
        os.remove('tmp_nova_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/nova/nova-compute.conf')
        with open('tmp_nova_compute_conf_' + env.host_string, 'w') as f:
            f.write(conf_nova_compute_conf)

        files.upload_template(filename='tmp_nova_compute_conf_'+env.host_string,
                              destination='/etc/nova/nova-compute.conf',
                              use_jinja=True,
                              use_sudo=True,
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
                              use_sudo=True)
        os.remove('tmp_libvirt_bin_' + env.host_string)
        print red(env.host_string + ' | Update /etc/libvirt/libvirtd.conf')
        with open('tmp_libvirtd_conf_' + env.host_string, 'w') as f:
            f.write(conf_libvirtd_conf)
        files.upload_template(filename='tmp_libvirtd_conf_' + env.host_string,
                              destination='/etc/libvirt/libvirtd.conf',
                              use_sudo=True)
        os.remove('tmp_libvirtd_conf_' + env.host_string)
        sudo('restart libvirt-bin')


def main():
    try:
        target = NovaCompute(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')
        parser.print_help()
        sys.exit(1)

    if args.subparser_name == 'install':
        execute(target._install,
                args.my_ip,
                args.rabbit_hosts,
                args.rabbit_pass,
                args.auth_uri,
                args.auth_url,
                args.nova_pass,
                args.novncproxy_base_url,
                args.glance_host,
                args.neutron_endpoint,
                args.neutron_pass,
                args.rbd_secret_uuid)
        

if __name__ == '__main__':
    main()