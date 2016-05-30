from fabric.api import *
from fabric.contrib import files
from fabric.tasks import Task
from fabric.network import disconnect_all
from fabric.colors import red
import os
import argparse
import sys
from playback.cli import cli_description
from playback import __version__
from playback.horizon_conf import conf_local_settings_py

parser = argparse.ArgumentParser(description=cli_description+'this command used for provision Horizon')
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
                                help='install horizon')
install.add_argument('--openstack-host',
                    help='configure the dashboard to use OpenStack services on the controller node e.g. CONTROLLER_VIP',
                    action='store',
                    default=None,
                    dest='openstack_host')
install.add_argument('--memcache',
                    help='django memcache e.g. CONTROLLER1:11211',
                    action='store',
                    default=None,
                    dest='memcache')
install.add_argument('--time-zone',
                    help='the timezone of the server. This should correspond with the timezone of your entire OpenStack installation e.g. Asia/Shanghai',
                    action='store',
                    default=None,
                    dest='time_zone')

args = parser.parse_args()

class Horizon(Task):
    def __init__(self, user, hosts=None, parallel=True, *args, **kwargs):
        super(Horizon, self).__init__(*args, **kwargs)
        self.user = user
        self.hosts = hosts
        self.parallel = parallel
        env.user = self.user
        env.hosts = self.hosts
        env.parallel = self.parallel

    def _install(self, openstack_host, memcache, time_zone):
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
                              context={'openstack_host': openstack_host,
                                       'memcache': memcache,
                                       'time_zone': time_zone})
        os.remove('tmp_local_settings_py_' + env.host_string)



def main():
    try:
        target = Horizon(user=args.user, hosts=args.hosts.split(','))
    except AttributeError:
        print red('No hosts found. Please using --hosts param.')
        parser.print_help()
        sys.exit(1)

    if args.subparser_name == 'install':
        execute(target._install, 
                args.openstack_host, 
                args.memcache, 
                args.time_zone)

if __name__ == '__main__':
    main()