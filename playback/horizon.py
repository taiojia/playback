from fabric.api import *
from fabric.contrib import files
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
from playback.templates.local_settings_py import conf_local_settings_py
from playback import __version__
from playback import common

class Horizon(common.Common):

    def _install(self, openstack_host, memcached_servers, time_zone):
        print red(env.host_string + ' | Install the packages')
        sudo('apt-get update')
        sudo('apt-get -y install openstack-dashboard')

        print red(env.host_string + ' | Update /etc/openstack-dashboard/local_settings.py')
        with open('tmp_local_settings_py_' + env.host_string, 'w') as f:
            f.write(conf_local_settings_py)
        files.upload_template(filename='tmp_local_settings_py_' + env.host_string,
                              destination='/etc/openstack-dashboard/local_settings.py',
                              use_jinja=True,
                              use_sudo=True,
                              backup=True,
                              context={'openstack_host': openstack_host,
                                       'memcached_servers': memcached_servers,
                                       'time_zone': time_zone})
        os.remove('tmp_local_settings_py_' + env.host_string)

def install(args):
    try:
        target = Horizon(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)

    execute(target._install, 
            args.openstack_host, 
            args.memcached_servers, 
            args.time_zone)

def parser():
    p = argparse.ArgumentParser(prog='horizon-deploy', description=cli_description+'this command used for provision Horizon')
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
    install_parser = s.add_parser('install', help='install horizon')
    install_parser.add_argument('--openstack-host',
                                help='configure the dashboard to use OpenStack services on the controller node e.g. CONTROLLER_VIP',
                                action='store',
                                default=None,
                                dest='openstack_host')
    install_parser.add_argument('--memcached-servers',
                                help='django memcache e.g. CONTROLLER1:11211,CONTROLLER2:11211',
                                action='store',
                                default=None,
                                dest='memcached_servers')
    install_parser.add_argument('--time-zone',
                                help='the timezone of the server. This should correspond with the timezone of your entire OpenStack installation e.g. Asia/Shanghai',
                                action='store',
                                default=None,
                                dest='time_zone')
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