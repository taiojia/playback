from fabric.api import *
from fabric.contrib import files
from fabric.tasks import Task
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
from playback.neutron_agent_conf import conf_neutron_conf, conf_linuxbridge_agent_ini
from playback import __version__

parser = argparse.ArgumentParser(description=cli_description+'this command used for provision Neutron Agent')
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
                                help='install neutron agent')
install.add_argument('--rabbit-hosts',
                    help='rabbit hosts e.g. controller1,controller2',
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
install.add_argument('--neutron-pass',
                    help='the password for neutron user',
                    action='store',
                    default=None,
                    dest='neutron_pass')
install.add_argument('--public-interface',
                    help='public interface e.g. eth1',
                    action='store',
                    default=None,
                    dest='public_interface')
install.add_argument('--local-ip',
                    help=' underlying physical network interface that handles overlay networks(uses the management interface IP)',
                    action='store',
                    default=None,
                    dest='local_ip')


class NeutronAgent(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(NeutronAgent, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    @runs_once
    def _install(self, rabbit_hosts, rabbit_pass, auth_uri, auth_url, neutron_pass, public_interface, local_ip):
        print red(env.host_string + ' | Install the components')
        sudo('apt-get update')
        sudo('apt-get -y install neutron-plugin-linuxbridge-agent conntrack')

        print red(env.host_string + ' | Update /etc/neutron/neutron.conf')
        with open('tmp_neutron_conf_' + env.host_string, 'w')as f:
            f.write(conf_neutron_conf)
        files.upload_template(filename='tmp_neutron_conf_' + env.host_string,
                              destination='/etc/neutron/neutron.conf',
                              use_jinja=True,
                              use_sudo=True,
                              context={'rabbit_hosts': rabbit_hosts,
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'neutron_pass': neutron_pass})
        os.remove('tmp_neutron_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/plugins/ml2/linuxbridge_agent.ini')
        with open('tmp_linuxbridge_agent_ini_' + env.host_string, 'w')as f:
            f.write(conf_linuxbridge_agent_ini)
        files.upload_template(filename='tmp_linuxbridge_agent_ini_' + env.host_string,
                              destination='/etc/neutron/plugins/ml2/linuxbridge_agent.ini',
                              use_jinja=True,
                              use_sudo=True,
                              context={'public_interface': public_interface,
                                       'local_ip': local_ip})
        os.remove('tmp_linuxbridge_agent_ini_' + env.host_string)

        print red(env.host_string + ' | Restart Services')
        sudo('service nova-compute restart')
        sudo('service neutron-plugin-linuxbridge-agent restart')




def main():
    try:
        target = NeutronAgent(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')
        parser.print_help()
        sys.exit(1)

    if args.subparser_name == 'install':
        execute(target._install, 
                args.rabbit_hosts, 
                args.rabbit_pass, 
                args.auth_uri, 
                args.auth_url, 
                args.neutron_pass, 
                args.public_interface, 
                args.local_ip)

if __name__ == '__main__':
    main()