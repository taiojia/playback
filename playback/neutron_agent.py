from fabric.api import *
from fabric.contrib import files
from fabric.tasks import Task
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
from playback.templates.neutron_conf_for_agent import conf_neutron_conf
from playback.templates.linuxbridge_agent_ini_for_agent import conf_linuxbridge_agent_ini
from playback import __version__
from playback import common

class NeutronAgent(common.Common):

    def _install(self, rabbit_hosts, rabbit_user, rabbit_pass, auth_uri, auth_url, neutron_pass, public_interface, local_ip, memcached_servers):
        print red(env.host_string + ' | Install the components')
        sudo('apt-get update')
        # conntrack deprecated in mitaka
        #sudo('apt-get -y install neutron-plugin-linuxbridge-agent conntrack')
        sudo('apt-get -y install neutron-linuxbridge-agent')

        print red(env.host_string + ' | Update /etc/neutron/neutron.conf')
        with open('tmp_neutron_conf_' + env.host_string, 'w')as f:
            f.write(conf_neutron_conf)
        files.upload_template(filename='tmp_neutron_conf_' + env.host_string,
                              destination='/etc/neutron/neutron.conf',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'rabbit_hosts': rabbit_hosts,
                                       'rabbit_user': rabbit_user, 
                                       'rabbit_password': rabbit_pass,
                                       'auth_uri': auth_uri,
                                       'auth_url': auth_url,
                                       'neutron_pass': neutron_pass, 
                                       'memcached_servers': memcached_servers})
        os.remove('tmp_neutron_conf_' + env.host_string)

        print red(env.host_string + ' | Update /etc/neutron/plugins/ml2/linuxbridge_agent.ini')
        with open('tmp_linuxbridge_agent_ini_' + env.host_string, 'w')as f:
            f.write(conf_linuxbridge_agent_ini)
        files.upload_template(filename='tmp_linuxbridge_agent_ini_' + env.host_string,
                              destination='/etc/neutron/plugins/ml2/linuxbridge_agent.ini',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'public_interface': public_interface,
                                       'local_ip': local_ip})
        os.remove('tmp_linuxbridge_agent_ini_' + env.host_string)

        print red(env.host_string + ' | Restart Services')
        sudo('service nova-compute restart')
        sudo('service neutron-linuxbridge-agent restart')

    def install(self, *args, **kwargs):
        return execute(self._install, *args, **kwargs)

def install_subparser(s):
    install_parser = s.add_parser('install', help='install neutron agent')
    install_parser.add_argument('--rabbit-hosts',
                                help='rabbit hosts e.g. controller1,controller2',
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
    install_parser.add_argument('--neutron-pass',
                                help='the password for neutron user',
                                action='store',
                                default=None,
                                dest='neutron_pass')
    install_parser.add_argument('--public-interface',
                                help='public interface e.g. eth1',
                                action='store',
                                default=None,
                                dest='public_interface')
    install_parser.add_argument('--local-ip',
                                help=' underlying physical network interface that handles overlay networks(uses the management interface IP)',
                                action='store',
                                default=None,
                                dest='local_ip')
    install_parser.add_argument('--memcached-servers',
                                help='memcached servers e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                                action='store',
                                default=None,
                                dest='memcached_servers')
    return install_parser

def make_target(args):
    try:
        target = NeutronAgent(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    return target
    
def install(args):
    target = make_target(args)
    target.install(
            args.rabbit_hosts,
            args.rabbit_user,  
            args.rabbit_pass, 
            args.auth_uri, 
            args.auth_url, 
            args.neutron_pass, 
            args.public_interface, 
            args.local_ip, 
            args.memcached_servers)
            
def parser():
    p = argparse.ArgumentParser(prog='neutron-agent-deploy', description=cli_description+'this command used for provision Neutron Agent')
    p.add_argument('-v', '--version', action='version', version=__version__)
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